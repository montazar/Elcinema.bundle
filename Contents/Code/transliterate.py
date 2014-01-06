# -*- coding: utf-8 -*-
# Transliterator with Yamli

'''
This is a command line translator with Yamli translate behind it.
Auther : Montazar@github
'''

import re, json, types

try:
    import urllib2 as request
    from urllib import quote
except:
    from urllib import request
    from urllib.parse import quote

class Transliterator:

    # defines
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13'}
    API_URL = "http://api.yamli.com/transliterate.ashx?word=%s&tool=&account_id=&prot=http&hostname=&path=&build=&sxhr_id="
   
    ## Translates a word from arabizi to arabic
    def TRANSLATE_WORD(self, word):
        if not word or not self.IS_WESTER_CHAR(word) or ' ' in word:
            return None
        return self.FILTER_TRANSLITERATION(self.GET_DATA_FROM_YAMLI(word))

    ## Checks if string contains western characters
    def IS_WESTER_CHAR(self,s):
        try:
            s.encode("iso-8859-1")
            return True
        except:
            return False

    ## Filters out the translation result and returns a list
    ## returns a list, with most accurate translation listed first
    def FILTER_TRANSLITERATION(self, data):
        if not data:
            return None

        try: 
            # filter out callback data
            data = re.sub('[();]', '', data.split("dataCallback",1)[1])[:-1]
            # json decode
            data = json.loads(json.loads(data)['data'])['r']

            # clean result and split
            data = re.sub('[01|/\d+]', ' ',data)
            data = re.sub(' +',' ',data).split(" ")
        except: return None

        # return list
        return data

    ## Fetches and returns the translation 
    def GET_DATA_FROM_YAMLI(self, word):
        if not word or ' ' in word:
            return None

        try:
            word = quote(word, '')
            req = request.urlopen(request.Request(url=(self.API_URL % word), headers = self.HEADERS))
            req = req.read().decode('utf-8')
        except: return None

        return req
