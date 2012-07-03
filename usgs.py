import csv
import zipfile
import os
import urllib2
import random
import logging
try:
    from cStringIO import StringIO #faster
except:
    from StringIO import StringIO

USGS_CSV = "usgshist.csv" #USGS Historical Topo Download
SAVE_DIR = "/home/tim/usgs" #think about getting this from cmd line arg
LAST_LIST_ITEM_FILE = "last_index_processed"
#setting up logger
#TODO: find a better way to instantiate logger
logger = logging.getLogger('usgs-scrape')
handler = logging.FileHandler('usgs.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

def unzip_geofile_and_save(io_input):
    """
    Takes a zip filename, unzips and saves a pdf to the file system
    """
    zf = zipfile.ZipFile(io_input)
    for name in zf.namelist():
        geo_pdf = open(os.path.join(SAVE_DIR, name), 'wb') #look in os for platform independent dir ref
        geo_pdf.write(zf.read(name))
        geo_pdf.flush()
        geo_pdf.close()
        logger.info('File %s to directory' %name)

def open_csv_get_urls():
    """
    Opens csv and gets urls from file. Returns a list of urls.
    """
    histtops = csv.DictReader(open(USGS_CSV))
    urllist = list()
    for row in histtops:
        urllist.append(row['DownloadGeoPDF'])
    urllist = random.sample(urllist, 5) #for testing
    geourls = [url.replace(' ', '%20') for url in urllist]
    logger.info('Number of urls in file: %d' %len(geourls))
    return geourls

def get_start_and_end_index():
    """
    If last list index file exists, will read in number as start at +1 of that number and determine end number by adding
    global bulk load number to determine end index. If last list file doesn't exist, will start at zero. Returns start
     index and end index.
    """
    bulk_run = 20
    if os.path.isfile(LAST_LIST_ITEM_FILE):
        with open(LAST_LIST_ITEM_FILE, 'r') as f:
            start_index = int(f.read())+1
            stop_index = start_index+bulk_run
    else:
        start_index = 0
        stop_index = start_index+bulk_run
    return start_index, stop_index

def save_last_processed_index(last_index):
    """
    saves last processed url to a file.
    """
    with open(LAST_LIST_ITEM_FILE, 'at') as f:
        f.write(last_index)
    logger.info('Set to log last index num.')

def open_and_unzip_geofiles(geourls, start_index, stop_index):
    """
    takes a list of urls, opens, and saves to a file
    """
    #TODO: figure out how to iterate a list and stop at a count
    for index, url in enumerate(geourls[start_index:stop_index]):
        response = urllib2.urlopen(url)
        data = response.read()
        input = StringIO(data)
        unzip_geofile_and_save(input)
        if index == stop_index:
            save_last_processed_index(index)

def main():
    """ main method"""
    open_and_unzip_geofiles(open_csv_get_urls(), get_start_and_end_index())
    logger.info("Starting log file with date")

if __name__ == '__main__':
    main()

# TODO: context operator
# TODO: error handling
# TODO; time how long it takes to download and unzip each one - logging has time stuff
# TODO: need to keep track of downloaded files and links, where we are in list of urls, batch running and where to pick back up
# TODO: need logging
# TODO: run as chron