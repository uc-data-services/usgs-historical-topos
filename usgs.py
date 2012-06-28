import csv
import zipfile
import os
import urllib2
import random

try:
    from cStringIO import StringIO #faster
except:
    from StringIO import StringIO

USGS_CSV = "usgshist.csv" #USGS Historical Topo Download
SAVE_DIR = "/home/tim/usgs" #think about getting this from cmd line arg


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
    print (geourls)
    return geourls

def open_and_unzip_geofiles(geourls):
    """
    takes a list of urls, opens, and saves to a file
    """
    for url in geourls:
        response = urllib2.urlopen(url)
        data = response.read()
        input = StringIO(data)
        unzip_geofile_and_save(input)

def main():
    """ main method"""
    open_and_unzip_geofiles(open_csv_get_urls())


if __name__ == '__main__':
    main()

# TODO: context operator
# TODO: error handling
# TODO; time how long it takes to download and unzip each one
# TODO: need to keep track of downloaded files and links, where we are in list of urls, batch running and where to pick back up
# TODO: for above explore popping off the list
# TODO: poss use pickle to persist tracking
# TODO: need logging
# TODO: run as chron


