from utils import *
from System import DateTime
from System.IO import Path

import getCMXData
import config as cfg

#@Name	Comixology Scraper
#@Hook	Books
#@Description Scrape Comixology website for metadata
def ComixologyScraper(books):
    booksProcessed = 0
    booksNotMatched = 0

    for book in books:
        IDinCA = False
        CMXData = None
        CMXID = getCMXIDFromString(book.Notes)

        print("======> Scraping {0}".format(Path.GetFileName(book.FilePath)))
        if CMXID is not None:
            IDinCA = True
            CMXData = getCMXData.byCMXID(CMXID, True)

        if CMXID is not None:
            if CMXData is not None and (IDinCA or verifyMatch(book, CMXData)):
                booksProcessed += 1
                updateMetadata(book, CMXData)
            else:
                booksNotMatched += 1
                print('Not a close enough match')
        else:
            print('Could not find Comixology ID in Notes or via google')
        
        print('')

    print "Comixology Scraper finished (scraped {0}, skipped {1}).".format(booksProcessed, booksNotMatched)
            

#function copied from CVS - ComicVine Scraper
# a quick function to make splitting ComicRack comicbook fields easier
def split(s):
    return s.split(",") if s else [] 

def verifyMatch(book, CMXData):
    return book.Series == CMXData['series'] and book.Number == CMXData['issue'] and book.ReleasedTime.Year == CMXData['Year'] and book.ReleasedTime.Month == CMXData['Month']    

def overwritable(prop):
    if type(prop) is str:
        return cfg.overwrite or len(prop) == 0
    elif type(prop) is int:
         return cfg.overwrite or prop == -1    
    elif type(prop) is DateTime:
        return cfg.overwrite or prop == DateTime.MinValue       
    else:
        return cfg.overwrite or prop is None

def updateMetadata(book, CMXData):
    if overwritable(book.Series):
        book.Series = CMXData.get('series', book.Series)
    
    if overwritable(book.Volume):
        book.Volume = CMXData.get('volume', book.Volume)
    
    if overwritable(book.Number):
        book.Number = CMXData.get('issue', book.Number)

    if overwritable(book.Summary):
        book.Summary = CMXData.get('description', book.Summary)
    if overwritable(book.Web):
        book.Web = CMXData.get('webLink', book.Web)

    if overwritable(book.Publisher):
        book.Publisher = CMXData.get('publisher', book.Publisher)

    #credits - extra work with the split and join
    if overwritable(book.Writer):
        book.Writer = ', '.join(CMXData.get('Writer', split(book.Writer)))
    if overwritable(book.Penciller):
        book.Penciller = ', '.join(CMXData.get('Penciller', split(book.Penciller)))
    if overwritable(book.Inker):
        book.Inker = ', '.join(CMXData.get('Inker', split(book.Inker)))
    if overwritable(book.Colorist):
        book.Colorist = ', '.join(CMXData.get('Colorist', split(book.Colorist)))
    if overwritable(book.CoverArtist):
        book.CoverArtist = ', '.join(CMXData.get('Cover', split(book.CoverArtist)))

    if overwritable(book.Genre):
        book.Genre = ', '.join(CMXData.get('genres', split(book.Genre)))

    #released date - datetime
    if overwritable(book.ReleasedTime):
        book.ReleasedTime = DateTime(CMXData.get('Year', book.ReleasedTime.Year), 
            CMXData.get('Month', book.ReleasedTime.Month), 
            CMXData.get('Day', book.ReleasedTime.Day))

    #special handling for Notes
    #Add Comixology ID note if not present in the notes. Never overwrite notes
    if book.Notes.find(CMXData['Notes']) == -1:
        #no CMX ID in notes, append to notes
        if len(book.Notes) > 0:
            book.Notes += "\n"
        book.Notes += CMXData['Notes']