***DEPRECATED DUE TO LACK OF INTEREST***
=
elCinema metadata agent
=
This metadata agent will retrieve the metadata available on [elcinema](http://www.elcinema.com/).

This module is still in beta and I would appreciate any bug reports via Github issue tracker on this page.
To get the best results, follow the [standard plex naming convention for movies](http://wiki.plexapp.com/index.php/Media_Naming_and_Organization_Guide#Movie_Content).

Below are current adjustable settings:

* **The ability to get output information in logs** - This is for debugging purposes. **Defualt: Off**.
* **Include theatre media in search result.** - It´s not possible to determine if the media is a movie or theatre, and that many arabic theatre has the same name as the movie. There is no alternative but to give the user the ability to filter out the results. **Defualt: Off**.
* **Include the English working title with the Arabic, if it exists** - If enabled, The English work title will be included in the media-title in Plex. It will have the format 'arabic-title (english-title)'. **Defualt: On**.
* **The ability to translate arabizi to arabic.** - Most of the arabic movies is named with arabizi(arabic in latin-script, e.g. '7abibi' or 'habibi' will be converted to 'حبيبي'), this will provide much better search results. Take into consideration that this could also provide poor results if the naming is not done with Arabizi. This functionality will not manipulate names given with Arabic characters, only latin charecters. (Note. This mechanism is available through Yamil and is available in a seperat class and file). **Defualt: On**.
* **Choose to retrieve metadata in Arabic or English** By setting the agent as the default agent for a library, you have the possibility to choose between retrieving metadata either in Arabic or English. It is also possible to choose a language when you issue a search manually.
