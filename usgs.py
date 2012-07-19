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
from ConfigParser import SafeConfigParser

USGS_CSV = "usgshist.csv" #USGS Historical Topo Download
CSV_DIR = '/home/tim/Dropbox/usgs-historical-topos/'
SAVE_DIR = "/home/tim/usgs" #think about getting this from cmd line arg
LAST_LIST_ITEM_FILE = "last_index_processed"
#setting up logger below
#TODO: find a better way to instantiate logger
logger = logging.getLogger('usgs-scrape')
handler = logging.FileHandler('usgs.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(formatter)
logger.addHandler(handler)
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
        logger.info('Saved file %(file)s to %(dir)s' % \
                    {'file':name, 'dir':SAVE_DIR})

def open_csv_get_urls():
    """
    Opens csv and gets urls from file. Returns a list of urls.
    """
    histtops = csv.DictReader(open(CSV_DIR+USGS_CSV))
    urllist = list()
    for row in histtops:
        urllist.append(row['DownloadGeoPDF'])
    urllist = random.sample(urllist, 12) #for testing
    geourls = [url.replace(' ', '%20') for url in urllist]
    logger.info('Number of urls in %(usgs_file)s: %(#)03d' % \
                {'usgs_file':CSV_DIR+USGS_CSV, '#': len(geourls)})
    return geourls

def get_start_and_end_index():
    """
    If last list index file exists, will read in number as start at +1 of that number and determine end number by adding
    global bulk load number to determine end index. If last list file doesn't exist, will start at zero. Returns start
     index and end index.
    """
    bulk_run = 5 #TODO: move to config
    if os.path.isfile(LAST_LIST_ITEM_FILE):
        with open(LAST_LIST_ITEM_FILE, 'r') as f:
            start_index = int(f.read())
            print start_index
            stop_index = start_index+bulk_run
            print stop_index
    else:
        start_index = 0
        print start_index
        stop_index = bulk_run
        print stop_index
    return start_index, stop_index

def save_last_processed_index(last_index):
    """
    saves last processed url to a file.
    """
    with open(LAST_LIST_ITEM_FILE, 'w+') as f:
        f.write(str(last_index))
    logger.info('Index of last url/document process: %s' % last_index)

def open_and_unzip_geofiles(geourls, start_index, stop_index):
    """
    takes a list of urls, opens, and saves to a file
    """
    for index, url in enumerate(geourls[start_index:stop_index]):
        response = urllib2.urlopen(url)
        data = response.read()
        input = StringIO(data)
        unzip_geofile_and_save(input)
    save_last_processed_index(stop_index)

def get_config_info():
    """open usgs.ini and return config"""
    parser = SafeConfigParser()
    parser.read('usgs.ini')
    return parser.get('config_info',USGS_CSV), parser.get('config_info',CSV_DIR), \
           parser.get('config_info', SAVE_DIR), parser.getint('config_info', bulk_run)

def main():
    """ main method"""
    logger.info("Starting script")
    usgs_csv, csv_dir, save_dir, bulk_run = get_config_info()#need to refactor above to use
    start_index, stop_index = get_start_and_end_index()
    open_and_unzip_geofiles(open_csv_get_urls(), start_index, stop_index)

if __name__ == '__main__':
    main()

# TODO: error handling
# TODO; time how long it takes to download and unzip each one - logging has time stuff
# TODO: need to keep track of downloaded files and links, where we are in list of urls, batch running and where to pick back up
# TODO: need logging
# TODO: run as chron