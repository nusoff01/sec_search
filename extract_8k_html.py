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
	return sec_base + "cgi-bin/browse-edgar?action=getcompany&CIK=" + cik_num + "&type=8-K%25&dateb=&owner=exclude&start=0&count=100"


# boolean function which checks to see if there is a next page of filings for a company
def next_page_present (cik_page):
	soup = BeautifulSoup(cik_page, "html.parser")
	table = soup.findAll('table')[1]
	print(table)
	return 0




# Go through each line in templist and use as a CIK

with open('templist_short.txt') as f:
    lines = f.read().splitlines()

cik_pages = []
for line in lines:
	cik_pages.append(search_CIK(line))

# print(cik_pages)







url = "http://www.samhsa.gov/data/NSDUH/2k10State/NSDUHsae2010/NSDUHsaeAppC2010.htm"
soup = BeautifulSoup(cik_pages[0], "html.parser")

# for row in soup.findAll('table')[2].findAll('tr'):
# 	print(row)
	# if(row.find("8-K") != -1):
	# 	print(row)

soupfind = soup.findAll('table')[2].findAll('tr')
print(len(soupfind))

countFilings = 0
for row in soupfind:
	try:
		typeTDStr = str(row.findAll('td')[2])
		if(typeTDStr.find("2.02") > -1 or typeTDStr.find("2.05") > -1):
			print(typeTDStr)
			countFilings += 1
	except:
		pass

print("2.02 count: " + str(countFilings))
# ncext_page_present(cik_pages[0])

    