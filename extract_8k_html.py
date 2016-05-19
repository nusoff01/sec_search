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

def search_CIK (cik_num, cik_start):
	cik_url = create_CIK_URL(cik_num, cik_start)
	print("searching: " + cik_url)
	response = urllib2.urlopen(cik_url)
	cik_html = response.read()
	return cik_html

# search_documents: takes in a cik_num and returns a list of document URLs for
#                   any document which contains either a 2.01 or 2.05

## implementation notes: looks like this is a table, going through row by row
#  seems to be the way to go

def find_classification (cik_num):
	cik_start = 0
	cont_true = True
	count_filings = 0
	while cont_true:
		cik_page = search_CIK(cik_num, cik_start)
		soup = BeautifulSoup(cik_page, "html.parser")
		try:
			soupfind = soup.findAll('table')[2].findAll('tr')

			for row in soupfind:
				try:
					typeTDStr = str(row.findAll('td')[2])
					if(typeTDStr.find("2.02") > -1 or typeTDStr.find("2.05") > -1):
						count_filings += 1
				except:
					pass
		except:
			pass
		cont_true = next_page_present(cik_page)
		cik_start += 100
	print(count_filings)
	return 0







###################### Helper Functions ####################

# create_CIK_URL: from a CIK and starting index, creates and returns the 
#                 corresponding search url

def create_CIK_URL (cik_num, startNum):
	return (sec_base + "cgi-bin/browse-edgar?action=getcompany&CIK=" + cik_num 
	                + "&type=8-K%25&dateb=&owner=exclude&start=" + 
	                str(startNum) + "&count=100")


# boolean function which checks to see if there is a next page of filings for a company
def next_page_present (cik_page):
	soup = BeautifulSoup(cik_page, "html.parser")
	table = soup.findAll('table')[1]
	return (str(table).find("Next 100")) != -1
	




# Go through each line in templist and use as a CIK

with open('templist.txt') as f:
    lines = f.read().splitlines()

cik_pages = []
# for line in lines:
# 	cik_pages.append(search_CIK(line))

# print(cik_pages)


for cik in lines:
	find_classification(cik)





    