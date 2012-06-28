import csv
import zipfile
import os
import urllib
import urllib2
import random
try:
	from cStringIO import StringIO #faster
except:
	from StringIO import StringIO	

USGS_CSV = "usgshist.csv" #USGS Historical Topo Download
SAVE_DIR = "/home/tim/usgs" #think about getting this from cmd line arg


def unzip_geofile_and_save(io_input):
	'''Takes a zip filename, unzips and saves a pdf to the file system'''
	zf = zipfile.ZipFile(io_input)
	for name in zf.namelist():
	    geo_pdf = open(os.path.join(SAVE_DIR, name), 'wb') #look in os for platform independent dir ref
	    geo_pdf.write(zf.read(name))
	    geo_pdf.flush()
	    geo_pdf.close()

def open_csv_get_urls():
	'''Opens csv and returns list of urls to retrieve'''
	histtops = csv.DictReader(open(USGS_CSV))
	urllist = list()
	for row in histtops:
	    urllist.append(row['DownloadGeoPDF'])
	#urllist = random.sample(urllist, 5) #for testing
	geourls = [url.replace(' ', '%20') for url in urllist]
	return geourls

geourls = open_csv_get_urls()
for url in geourls:
	response = urllib2.urlopen(url)
	data = response.read()
	input = StringIO(data)
	unzip_geofile_and_save(input)

'''
# TODO: context operator
# TODO: error handling
# TODO: need to keep track of downloaded files and links, where we are in list of urls, batch running and where to pick back up 
# poss use pickle to persist tracking
# TODO: need logging
# TODO: run as chron
# TODO: github repo 

#geourl = 'http://ims.er.usgs.gov/gda_services/download?item_id=5507057&quad=Academy&state=CA&grid=7.5X7.5&series=Map GeoPDF'
#geourls = geourl.replace(' ', '%20')

