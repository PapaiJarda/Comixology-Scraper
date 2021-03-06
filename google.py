from url_utils import UrlPathEncode
from parseGoogle import parseGoogleResult

GOOGLEURL = "https://www.google.com/search?ie=utf-8&oe=utf-8&q="
GOOGLEBASESEARCH = "comixology.com \"digital-comic\" \"{0} ({1}\" \"#{2}\""
COMICFORMATSEARCH = ' {0}'

def buildGoogleQueryURL(series, volume, issue, format, debug = False):
    QS = GOOGLEBASESEARCH.format(series, volume, issue)
    if format and format == 'Annual':
        QS += COMICFORMATSEARCH.format(format)

    QS = UrlPathEncode(QS)
    URL = GOOGLEURL + QS
    if debug:
        print(URL)
    return URL

def googleSeries(series, volume, issue, format, debug = False):
    URL = buildGoogleQueryURL(series, volume, issue, format)
    if debug:
        print(URL) 
    return parseGoogleResult(URL, debug)

def findCMXID(series, volume, issue, format, debug = False):
    CMXID = googleSeries(series, volume, issue, format, debug)

    if CMXID is None and ' Annual' in series:
        #check for Annual (maybe other formats?) in series name
        if debug:
            print("Remove Annual from series name and try again")
        CMXID = findCMXID(series.replace(' Annual', ''), volume, issue, 'Annual', debug)   

    if CMXID is None:
        #try without volume, if one was passed in
        if debug:
            print("Trying without volume")
        CMXID = googleSeries(series, '', issue, format, debug)

    if CMXID is None and series[0:4] == 'The ':
        #try removing leading The
        if debug:
            print("Removing leading 'The '")
        CMXID = googleSeries(series.replace('The ', '', 1), volume, issue, format, debug)
        
    if CMXID is None and issue == '1':
        #graphic novels, some one-shots don't have a number on CMX
        if debug:
            print("Trying without issue number")
        CMXID = googleSeries(series, volume, '', format, debug)

    if CMXID is None and issue == '1':
        #graphic novels, some one-shots don't have a number on CMX
        if debug:
            print("Trying without issue number and without volume")
        CMXID = googleSeries(series, '', '', format, debug)        

    if CMXID == -1:
        CMXID = None

    return CMXID
