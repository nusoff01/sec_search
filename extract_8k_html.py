# extract_8k_html.py
# created by Nick Usoff
#
# The purpose of this script is to extract 8-k forms from the SEC website.
# This is done by making a call to the corresponding CIK code for an 
# organization and determining whether that organization has an "Item 2.01" or
# "Item 2.05" associated with Item

###################### External Libraries ##################
import urllib2
from bs4 import BeautifulSoup

###################### Global Variables ####################
sec_base = "http://www.sec.gov/"







# search_CIK: takes in a CIK number, and returns the raw page of the search
#             result

def search_CIK (cik_num):

	cik_url = create_CIK_URL(cik_num)
	print("searching: " + cik_url)
	response = urllib2.urlopen(cik_url)
	cik_html = response.read()
	return cik_html

# search_documents: takes in a cik_page and returns a list of document URLs for
#                   any document which contains either a 2.01 or 2.05

## implementation notes: looks like this is a table, going through row by row
#  seems to be the way to go

def find_classification (cik_page):
	print(cik_page)
	return 0

###################### Helper Functions ####################

# create_CIK_URL: from a CIK, creates and returns the corresponding search url

def create_CIK_URL (cik_num):
	return sec_base + "cgi-bin/browse-edgar?CIK=" + cik_num + "&owner=exclude&action=getcompany&Find=Search"




print(create_CIK_URL("10254"))
search_CIK("10254")



# Go through each line in templist and use as a CIK

with open('templist.txt') as f:
    lines = f.read().splitlines()

cik_pages = []
for line in lines:
	cik_pages.append(search_CIK(line))

# print(cik_pages)







url = "http://www.samhsa.gov/data/NSDUH/2k10State/NSDUHsae2010/NSDUHsaeAppC2010.htm"
soup = BeautifulSoup(urllib2.urlopen(url).read())

for row in soup.findAll('table')[0].tbody.findAll('tr'):
    first_column = row.findAll('th')[0].contents
    third_column = row.findAll('td')[2].contents
    print first_column, third_column
