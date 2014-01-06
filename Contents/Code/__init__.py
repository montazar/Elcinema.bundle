# -*- coding: utf-8 -*-

# elcinema.com
# Auther : Montazar@github

import time, types, re
from transliterate import Transliterator

# Elcinema URL defines
ELC_BASE_URL            = 'http://www.elcinema.com/'
ELC_SEARCH_URL          = ELC_BASE_URL + 'search/?search_for=%s&category=work'
ELC_WORK_URL            = ELC_BASE_URL + '%s/work/%s'                                

# Variable defines
LANG_AR                 = Locale.Language.Arabic        
LANG_EN                 = Locale.Language.English
LANG_NONE               = Locale.Language.NoLanguage

MEDIA_TYPE_THEATHER     = 'مسرحية'                         # Media type information, for comparison, [Theather in arabic]
MEDIA_TYPE_MOVIE        = 'فيلم'                          # Media type information, for comparison, [Movie in arabic]
THRESHOLD_SCORE         = 70                             # Minimum value considered credible for results.
INITIAL_SCORE           = 80                             # Starting value for score.

def Start():
  HTTP.CacheTime = CACHE_1DAY
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13'

####################################################################################################
class elcinema(Agent.Movies):
  name = 'elcinema'
  languages = [Locale.Language.NoLanguage, Locale.Language.Arabic, Locale.Language.English]
  primary_provider = True
  accepts_from = ['com.plexapp.agents.localmedia']

  ## Translates a string from arabizi to arabic.
  def convert_to_arabic(self,name):
    # Only number within a word is allowed
    # Merge words start with AL/EL
    try:
        name = re.sub("[^a-zA-Z0-9]"," ", name)
        name = re.sub("(?x)\d{3,}(\S|)|\W\d(?=\W)|\d{2,2}(?=\W)","", name)
        name = re.sub(r'\b(el|al)\s',"el",name.lower())
    except: return None
    
    # Translate one word a time    
    arabic_char = ''
    t = Transliterator() 

    for word in name.strip().split(' '):
      # if number, keep it
      if not word.isdigit():
        try: 
          w = t.TRANSLATE_WORD(word)[0]
          if w:
            arabic_char += ' %s' % w
        except:pass
      else:
         arabic_char += ' %s' % word

    return arabic_char.strip()  

  ## Checks if string contains western characters
  def is_wester_char(self,s):
    try:
      s.encode("iso-8859-1")
      return True
    except:
      return False

  ## Searches for media and returns a list/html of results.
  def get_html_result(self,name):
    try:
      # Search, fetch html
      req = HTML.ElementFromURL(ELC_SEARCH_URL % name.replace(" ", "+"))
      # Fetch/traverse to search result
      result = req.cssselect('div.boxed-1 div.padded2-h div.media-photo ul.span3')
    except: return None

    return result

  #####################################################
  def search(self, results, media, lang, manual=False):
    # DEBUG
    self.log('# ****************************************')
    self.log('# STARTING SEARCH FOR "%s", Year: %s',media.name,media.year)
    self.log('# ****************************************')

    # If western letters/char try to convert to arabic => better search result.
    converted_name = None
    # TODO: BETTER SERACH SYSTEM FOR ARABIZI->ARABIC TRANSLATION
    if Prefs['transliterator'] and self.is_wester_char(media.name):
       # DEBUG
       self.log('# WESTERN LETTERS DETECTED')

       arabic_name = self.convert_to_arabic(media.name)
       if arabic_name:
          # DEBUG
          self.log('# ARABIC TITLE : %s', arabic_name)
          # temp name
          temp_arabic_name = arabic_name
          for i in range(0,len(temp_arabic_name.split())):
            # Search, fetch html and fetch/traverse to search result
            html_search = self.get_html_result(temp_arabic_name)

            if(len(html_search) > 0):
              # Set true for later comparison, for better scoring system
              converted_name = arabic_name
              break
            else:
              # shrink sentence with one word
              temp_arabic_name = temp_arabic_name.rsplit(' ', 1)[0]
    
    # Conversion didn't go well
    if not converted_name: 
      # Title might have english-work-title in it, clean the name, for better score comparison
      media.name = re.sub(r'\([^)]*\)', '', media.name)
      html_search = self.get_html_result(media.name)


    # try to find it in the media name
    # TODO: ONLY ON AUTO SERACH
    if not media.year:
      try: media.year = int(re.findall(r'\d{4}',media.name)[0].strip())
      except:pass

    # DEBUG
    if converted_name:
      self.log('# Search string:     %s',arabic_name)
    else:
      self.log('# Search string:     %s',media.name)
    self.log('# Year:              %s',media.year)
    self.log('# Result(s):         %s',str(len(html_search)))
    if not Prefs['theater']:
      self.log('# ONLY MEDIA OF TYPE MOVIE ARE PROCESSED')

    # Fetch media info from result
    for item in html_search:
      # Var
      media_arabic_title = ""
      media_english_title = ""
      media_id = ""
      media_type = ""
      media_year = 0

      # Fetch media data
      try:media_arabic_title = item.cssselect("li a")[0].text_content()
      except:pass

      try:media_english_title = item.cssselect("li a")[1].text_content()
      except: pass

      try:media_id = item.cssselect("li a")[0].get('href').replace("work","").replace("/","")
      except:pass
      
      try:media_type = item.cssselect("li:last-child")[0].text_content()
      except: pass

      try:media_year = int(item.cssselect("li span")[0].text_content().replace('(','').replace(')','').strip())
      except: pass

      # proccess only if its a movie
      if (self.safe_unicode(MEDIA_TYPE_MOVIE) in self.safe_unicode(media_type)) or (Prefs['theater'] and self.safe_unicode(MEDIA_TYPE_THEATHER) in self.safe_unicode(media_type)):
        
        # set tittle
        if media_english_title:
          media_title = (('%s (%s)') % (media_arabic_title, media_english_title))
        else:
          media_title = media_arabic_title;

        # SCORE CALCULATION 
        # TODO: BETTER SCORING SYSTEM
        # TODO: BETTER STRING COMPARISON FOR ARABIC
          # difference between names
        if converted_name:
          media_score = INITIAL_SCORE - abs(String.LevenshteinDistance(converted_name.lower(), media_arabic_title.lower()))
          s1 = converted_name
          s2 = media_arabic_title
        elif lang == LANG_AR or lang == LANG_NONE or not media_english_title:
          media_score = INITIAL_SCORE - abs(String.LevenshteinDistance(media.name.lower(), media_arabic_title.lower()))
          s1 = media.name
          s2 = media_arabic_title
        else:
          media_score = INITIAL_SCORE - abs(String.LevenshteinDistance(media.name.lower(), media_english_title.lower()))
          s1 = media.name
          s2 = media_english_title

        # DEBUG
        self.log("# LevensDis '%s' / '%s' : %s", s1.lower(),s2.lower() ,media_score)
          
          # year difference
        if media.year and media_year > 0:
          diff_year = abs(int(media.year) - int(media_year))
          if diff_year == 0:
            media_score += 10
          elif diff_year == 1:
            media_score += 5
          else:
            media_score = media_score - (5 * diff_year)

        # Add it to result
        if (media_score > THRESHOLD_SCORE): 
          results.Append(MetadataSearchResult(
            id = media_id,
            name = media_title,
            year = media_year,
            score = media_score,
            lang = lang
            ))
        
        # DEBUG
        self.log_serach_template(media_id,media_title,media_year,media_score,lang)
      else:
        continue

  #####################################################
  def update(self, metadata, media, lang, force=False):
    # TODO: FETCH FAN ART
    # TODO: FETCH POSTERS FROM ALT. SOURCE  
    # TODO: FETCH MORE DATA FROM ALT. SOURCE

    # Fetch html source for media
    if lang == LANG_NONE:
      url = ELC_WORK_URL % (LANG_AR.lower(),metadata.id)
    else:
      url = ELC_WORK_URL % (lang.lower(),metadata.id)
    html_request = HTML.ElementFromURL(url)

    # Filter out english title
    english_title = ''
    try: english_title = html_request.cssselect('div.span7more div div.span7more h3 span span')[0].text_content().strip()
    except: pass

    # Filter out arabic title
    arabic_title = ''
    try: arabic_title = html_request.cssselect('div.span7more div div.span7more h1')[0].text_content().strip()
    except: pass 

    # Set tittle according preferences
    title = '%s' % (arabic_title) 
    if Prefs['english_title'] and english_title:
      title = '%s (%s)' % (title,english_title) 

    metadata.title = self.safe_unicode(title)
    metadata.original_title = self.safe_unicode(arabic_title)

    # Filter out year
    year = 0
    try: year = int(html_request.cssselect('meta[name="title"]')[0].get('content').split()[-1])
    except: pass
    metadata.year = int(year)

    # Filter out rating
    rating = 0.0;
    try: 
      rating = float(html_request.cssselect('span[itemprop="ratingValue"]')[0].text_content())
    except: pass
    metadata.rating = float(rating)

    # Filter out genre 
    genre_list = []
    try: genre_list = html_request.cssselect('div.span7more div.padded1-v div.row ul.stats li')
    except: pass

    metadata.genres.clear()
    for item in genre_list:
      metadata.genres.add(self.safe_unicode(item.text_content().replace("|", "").replace("\n", "").strip()))

    # Get description
    description = ""
    try: 
      description = html_request.cssselect('p[itemprop="description"]')[0].text_content().split("...", 1)[0].strip().replace("  ", " ")
    except: pass
    metadata.summary = self.safe_unicode(description)

    # Get director
    director_list = []
    try: 
      director_list = html_request.cssselect('div.span7more div ul.unstyled li:first-child ul.inline li a')
    except: pass

    metadata.directors.clear()
    for item in director_list:
      metadata.directors.add(self.safe_unicode(item.text_content()))

    # Get writers
    writer_list = []
    try: 
      writer_list = html_request.cssselect('div.span7more div ul.unstyled li ul.inline')[1].cssselect("li a")
    except: pass

    metadata.writers.clear()
    for item in writer_list:
      metadata.writers.add(self.safe_unicode(item.text_content()))

    # Fetch poster
    poster_thumb = ""
    poster = ""
    try: 
      poster_thumb = html_request.cssselect("div.row div.span3 div.media-photo a img")[0].get('src')
      poster = poster_thumb.replace("_140.", "_147.")
    except: pass

    if (len(poster) > 0) and poster not in metadata.posters:
      try: metadata.posters[poster] = Proxy.Preview(HTTP.Request(poster_thumb), sort_order=0)
      except: pass

    # Log-it
    self.log_update_template('UPDATE',url,metadata)

  
  ## Log template used for debugging, called by serach func
  def log_serach_template(self,id,title,year,score,lang):
    self.log('|\\')
    if score > THRESHOLD_SCORE:
      self.log('| * Status:          %s', 'Added')
    else:
      self.log('| * Status:          %s', 'Ignored')
    self.log('| * ID:              %s', id)
    self.log('| * Name:            %s', title)
    self.log('| * Year:            %s', year)
    self.log('| * Score:           %s', score)
    self.log('| * Lang:            %s', lang)
    self.log('|/')

  ## Log template used for debugging, called by update func
  def log_update_template(self, header, url, metadata):
    self.log('****************************************')
    self.log(header)
    self.log('****************************************')
    self.log('* ID:              %s', metadata.id)
    self.log('* URL:             %s', url)
    self.log('* Title:           %s', metadata.title)
    self.log('* Orginal title:   %s', metadata.original_title)
    self.log('* Release date:    %s', str(metadata.originally_available_at))
    self.log('* Rating:          %s', str(metadata.rating))
    self.log('* Year:            %s', metadata.year)
    self.log('* Studio:          %s', metadata.studio)
    self.log('* Tagline:         %s', metadata.tagline)
    self.log('* Summary:         %s', metadata.summary)

    if len(metadata.directors) > 0:
        self.log('|\\')
        for i in range(len(metadata.directors)):
            self.log('| * Director:      %s', metadata.directors[i])

    if len(metadata.writers) > 0:
        self.log('|\\')
        for i in range(len(metadata.writers)):
            self.log('| * Writer:        %s', metadata.writers[i])

    if len(metadata.collections) > 0:
        self.log('|\\')
        for i in range(len(metadata.collections)):
            self.log('| * Collection:    %s', metadata.collections[i])

    if len(metadata.roles) > 0:
        self.log('|\\')
        for i in range(len(metadata.roles)):
            self.log('| * Starring:      %s (%s)', metadata.roles[i].actor, metadata.roles[i].photo)

    if len(metadata.genres) > 0:
        self.log('|\\')
        for i in range(len(metadata.genres)):
            self.log('| * Genre:         %s', metadata.genres[i])

    if len(metadata.posters) > 0:
        self.log('|\\')
        for poster in metadata.posters.keys():
            self.log('| * Poster URL:    %s', poster)

    if len(metadata.art) > 0:
        self.log('|\\')
        for art in metadata.art.keys():
            self.log('| * Fan art URL:   %s', art)

    self.log('****************************************')

  ## Logging
  def log(self, message, *args):
    if Prefs['debug']:
      Log(message, *args)

  ## safe unicode
  def safe_unicode(self,s, encoding='utf-8'):
    if s is None:
        return None
    if isinstance(s, basestring):
        if isinstance(s, types.UnicodeType):
            return s
        else:
            return s.decode(encoding)
    else:
        return str(s).decode(encoding)
