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

import urllib2
from bs4 import BeautifulSoup
import os


##############################################################################
# Global Variables  
##############################################################################

sec_base = "http://www.sec.gov/"


##############################################################################
# Functions
##############################################################################

# search_CIK: takes in a CIK number, and returns the raw page of the search
#             result

def search_CIK (cik_num, cik_start):
	cik_url = create_CIK_URL(cik_num, cik_start)
	# print("searching: " + cik_url)
	response = urllib2.urlopen(cik_url)
	cik_html = response.read()
	return cik_html


# search_documents: takes in a cik_num and returns a list of document URLs for
#                   any document which contains either a 2.01 or 2.05

def find_classification (cik_num):
	cik_start = 0
	cont_true = True
	count_filings = 0
	filing_links = []
	while cont_true:
		cik_page = search_CIK(cik_num, cik_start)
		soup = BeautifulSoup(cik_page, "html.parser")
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
		cont_true = next_page_present(cik_page)
		cik_start += 100
	print(count_filings)
	return filing_links


# extract_document: from a link to a filing, find the corresponding document
# 				    and write it to a local file

def extract_document(filing_link):
	filing_url = sec_base + filing_link
	response = urllib2.urlopen(filing_url)
	filing_html = response.read()
	soup = BeautifulSoup(filing_html, "html.parser")
	filing_rows = soup.findAll('table')[0].findAll('tr')
	for row in filing_rows:
		if(str(row).find('<td scope="row">8-K') != -1):
			print(row)

			return
	print("miss")
	print(soup.findAll('table')[0])


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
	file_from_url(url, "testOutput/testHTML.html")

##############################################################################
# Exectution 
##############################################################################


# Go through each line in templist and use as a CIK

with open('templist.txt') as f:
    lines = f.read().splitlines()

cik_pages = []
# for line in lines:
# 	cik_pages.append(search_CIK(line))

# print(cik_pages)

# filing_links_list = []
# for cik in lines:
# 	filing_links_list.append(find_classification(cik))

# for company in filing_links_list:
# 	for filing in company:
# 		extract_document(filing)


test_file_from_url()







    