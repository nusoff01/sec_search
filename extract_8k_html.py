# extract_8k_html.py
# created by Nick Usoff
#
# The purpose of this script is to extract 8-k forms from the SEC website.
# This is done by making a call to the corresponding CIK code for an 
# organization and determining whether that organization has an "Item 2.01" or
# "Item 2.05" associated with Item

##############################################################################
# Dependencies  
##############################################################################


from bs4 import BeautifulSoup
import os
import urllib2


##############################################################################
# Global Variables  
##############################################################################

sec_base = "http://www.sec.gov/"


##############################################################################
# Functions
##############################################################################

# search_CIK: takes in a CIK number, and returns the raw page of the search
#             result in a tuple with the CIK number

def search_CIK (cik_num, cik_start):
	cik_url = create_CIK_URL(cik_num, cik_start)
	# print("searching: " + cik_url)
	response = urllib2.urlopen(cik_url)
	cik_html = response.read()
	return (cik, cik_html)


# search_documents: takes in a cik_num and returns a list of document URLs for
#                   any document which contains either a 2.01 or 2.05

def find_classification (cik_num):
	cik_start = 0
	cont_true = True
	count_filings = 0
	filing_links = []
	while cont_true:
		cik_page = search_CIK(cik_num, cik_start)
		soup = BeautifulSoup(cik_page[1], "html.parser")
		try:
			soupfind = soup.findAll('table')[2].findAll('tr')

			for row in soupfind:
				try:
					typeTDStr = str(row.findAll('td')[2])
					if(typeTDStr.find("2.01") > -1 or typeTDStr.find("2.05") > -1):
						count_filings += 1
						filing_links.append(row.findAll('a')[0]['href'])
				except:
					pass
		except:
			pass
		cont_true = next_page_present(cik_page[1])
		cik_start += 100
	print(str(cik_num) + ": " + str(count_filings))
	return (filing_links, cik_num)


# extract_document: from a link to a filing, find the corresponding document
#		            url and path where it should go

def extract_document(filing_link, cik):
	filing_url = sec_base + filing_link
	print("filing_url: " + filing_url)
	response = urllib2.urlopen(filing_url)
	filing_html = response.read()
	soup = BeautifulSoup(filing_html, "html.parser")
	filing_rows = soup.findAll('table')[0].findAll('tr')
	for row in filing_rows:
		if(str(row).find('<td scope="row">8-K') != -1):
			# print(row)
			doc_url = sec_base + str(row.findAll('a')[0]['href'])
			last_slash = doc_url.rfind('/')
			trunc_url = doc_url[:last_slash]
			filing_id = trunc_url[trunc_url.rfind('/'):]

			# file_from_url(doc_url, ("output/"+ cik + "/" + filing_id + "_"
			# 	          + doc_url[last_slash + 1:]))
			return (doc_url, ("output/"+ cik + "/" + filing_id + "_"
				          + doc_url[last_slash + 1:]))
	return


##############################################################################
# Helper Functions  
##############################################################################

# create_CIK_URL: from a CIK and starting index, creates and returns the 
#                 corresponding search url

def create_CIK_URL (cik_num, startNum):
	return (sec_base + "cgi-bin/browse-edgar?action=getcompany&CIK=" + cik_num 
	                + "&type=8-K%25&dateb=&owner=exclude&start=" + 
	                str(startNum) + "&count=100")


# next_page_present: boolean function which checks to see if there is a next 
#                    page of filings for a company

def next_page_present (cik_page):
	soup = BeautifulSoup(cik_page, "html.parser")
	table = soup.findAll('table')[1]
	return (str(table).find("Next 100")) != -1


# file_from_url: takes in a url and a location, and writes to the location 
#                the raw HTML at whatever the url is.

def file_from_url (url, path):
	response = urllib2.urlopen(url)
	html = response.read()

	if not os.path.exists(os.path.dirname(path)):
	    try:
	        os.makedirs(os.path.dirname(path))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise
	with open(path, "w") as f:
	    f.write(html)
	return

	
##############################################################################
# Testing Functions
##############################################################################

def test_file_from_url ():
	url = "https://www.sec.gov/Archives/edgar/data/1041859/000114420408067808/v134037_8k.htm"
	file_from_url(url, "testOutput/1.html" )
	return

##############################################################################
# Exectution 
##############################################################################

# write_to_file: takes in a file and a path and writes the file to the path

def write_to_file(file, path): 
	if not os.path.exists(os.path.dirname(path)):
	    try:
	        os.makedirs(os.path.dirname(path))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise
	with open(path, "w") as f:
	    f.write(file)
	return


# Go through each line in templist and use as a CIK

with open('templist.txt') as f:
    lines = f.read().splitlines()

cik_pages = []

filing_links_list = []
for cik in lines:
	filing_links_list.append(find_classification(cik))


url_path_list = []
for company in filing_links_list:
	for filing in company[0]:
	 	url_path_list.append(extract_document(filing, company[1]))





import grequests
rs = (grequests.get(u[0]) for u in url_path_list)

path_list = zip(*url_path_list)[1]
responses = grequests.map(rs)

url_unzipped = []
content_unzipped = []
for response in responses:
	url_unzipped.append(str(response.url))
	content_unzipped.append(str(response.content))

response_path_list = zip(content_unzipped, path_list)

for res_path in response_path_list:
	write_to_file(res_path[0], res_path[1])










    