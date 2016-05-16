# extract_8k_html.py
# created by Nick Usoff
#
# The purpose of this script is to extract 8-k forms from the SEC website.
# This is done by making a call to the corresponding CIK code for an 
# organization and determining whether that organization has an "Item 2.01" or
# "Item 2.05" associated with Item

###################### External Libraries ##################


###################### Global Variables ####################
sec_base = "http://www.sec.gov/"
import urllib2



# search_CIK: takes in a CIK number, and returns the raw page of the search
#             result

def search_CIK (cik_num):
	cik_url = create_CIK_URL(cik_num)
	response = urllib2.urlopen(cik_url)
	html = response.read()
	# print(html)

###################### Helper Functions ####################

# create_CIK_URL: from a CIK, creates and returns the corresponding search url

def create_CIK_URL (cik_num):
	return sec_base + "cgi-bin/browse-edgar?CIK=" + cik_num + "&owner=exclude&action=getcompany&Find=Search"




print(create_CIK_URL("10254"))
search_CIK("10254")



# Go through each line in templist and use as a CIK

with open('templist.txt') as f:
    lines = f.read().splitlines()

print(lines)

for line in lines:
	print(create_CIK_URL(line))