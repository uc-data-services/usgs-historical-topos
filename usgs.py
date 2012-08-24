import csv
import zipfile
import os, os.path
from urllib2 import Request, urlopen, URLError
import time
import logging
try:
    from cStringIO import StringIO #faster
except:
    from StringIO import StringIO
from ConfigParser import SafeConfigParser

LAST_LIST_ITEM_FILE = "last_index_processed"

#setting up logger below
logger = logging.getLogger('usgs-scrape')
handler = logging.FileHandler('usgs.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
RESTART_DELAY = 10

def unzip_geofile_and_save(io_input, save_dir):
    """
    Takes a zip filename, unzips and saves a pdf to the file system
    """
    zf = zipfile.ZipFile(io_input)
    for name in zf.namelist():
        try:
            geo_pdf = open(os.path.join(save_dir, name), 'wb') #look in os for platform independent dir ref
            geo_pdf.write(zf.read(name))
            geo_pdf.flush()
            geo_pdf.close()
            logger.info('Saved file %(file)s to %(dir)s' % \
                        {'file':name, 'dir':save_dir})
        except OSError as e:
            logger.error("OSError", e.message)
        except IOError as e:
            #need to look up in geourls list and grab index where
            logger.error("IOError", e.message, e.errno)


def open_csv_get_urls(csv_dir, usgs_csv):
    """
    Opens csv and gets urls from file. Returns a list of urls.
    """
    try:
        histtops = csv.DictReader(open(csv_dir+usgs_csv))
        urllist = list()
        for row in histtops:
            urllist.append(row['DownloadGeoPDF'])
        geourls = [url.replace(' ', '%20') for url in urllist]
        logger.info('Number of urls in %(usgs_file)s: %(#)03d' % \
                    {'usgs_file':csv_dir+usgs_csv, '#': len(geourls)})
    except csv.Error as e:
        logger.error("csv error", e.message)
    return geourls

def get_start_and_end_index(bulk_run):
    """
    If last list index file exists, will read in number as start at +1 of that number and determine end number by adding
    global bulk load number to determine end index. If last list file doesn't exist, will start at zero. Returns start
     index and end index.
    """
    try:
       if os.path.isfile(LAST_LIST_ITEM_FILE):
            with open(LAST_LIST_ITEM_FILE, 'r') as f:
                start_index = int(f.read())
                print start_index
                stop_index = start_index+bulk_run
                print stop_index
       else:
            start_index = 0
            stop_index = bulk_run
    except OSError as e:
       logger.error("OSError:", e.message)

    return start_index, stop_index

def save_last_processed_index(last_index):
    """
    saves last processed url to a file.
    """
    try:
        with open(LAST_LIST_ITEM_FILE, 'w+') as f:
            f.write(str(last_index))
        logger.info('Index of last url/document process: %s' % last_index)
    except IOError as err:
        logger.error(err.message) #figure out what goes in ()

def get_geo_url(url):
    """takes a geo url and returns a respnse object"""
    try:
        response = urlopen(url)          
    except (urllib2.URLError, urllib2.HTTPError) as e:
        logger.error('Reason: ', e.reason)
        time.sleep(RESTART_DELAY)
    return response

def open_and_unzip_geofiles(geourls, start_index, stop_index, save_dir):
    """
    takes a list of urls, opens, and saves to a file
    """
    end_index = start_index #going to keep a counter of where we are
    for index, url in enumerate(geourls[start_index:stop_index]):
        while True:
            try:
                response = urlopen(url)
            except (urllib2.URLError, urllib2.HTTPError) as e:
                logger.error('Reason: ', e.reason)
                time.sleep(RESTART_DELAY)
            else:
                data = response.read()
                input = StringIO(data)
                unzip_geofile_and_save(input, save_dir)
                end_index += 1
                break
    save_last_processed_index(end_index)

def get_config_info():
    """open usgs.ini and return config info"""
    try:
        parser = SafeConfigParser()
        parser.read('usgs.ini')
    except ConfigParser.ParsingError as e:
        logger.error('Reason:', e.message)
    return parser.get('config_info', 'usgs_csv'), parser.get('config_info', 'csv_dir'), \
           parser.get('config_info', 'save_dir'), parser.getint('config_info', 'bulk_run')

def main():
    """ main method"""
    logger.info("Starting script")
    usgs_csv, csv_dir, save_dir, bulk_run = get_config_info() #need to refactor above to use
    start_index, stop_index = get_start_and_end_index(bulk_run)
    open_and_unzip_geofiles(open_csv_get_urls(csv_dir, usgs_csv), start_index, stop_index, save_dir)
    number_geopdfs_indir = len([name for name in os.listdir(save_dir) if os.path.isfile(save_dir+"/"+name)])
    logger.info('number of geopdfs in save_dir: %d' % number_geopdfs_indir)

if __name__ == '__main__':
    main()
