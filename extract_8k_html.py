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
from datetime import datetime
import grequests
import sys


##############################################################################
# Global Variables  
##############################################################################

sec_base = "http://www.sec.gov/"
startTime = datetime.now()
BATCH_SIZE = 200

##############################################################################
# Functions
##############################################################################

# from a cik_page, return a list of filings with the correct

def find_filings (cik_page):
	filing_links = []
	count_filings = 0
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
	return filing_links


# ciks_to_cik_pages: given a list of ciks, return a list of tuples with a cik
# 					 number and a cik page

# TBD finish this

def ciks_to_cik_pages (cik_list):
	cik_urls = []
	cik_start = 0
	filing_links_list = []

	while len(cik_list) > 0 : # only proceed if there are urls left to process
		for cik in cik_list:
			cik_urls.append(create_CIK_URL(cik, cik_start))
		rs = (grequests.get(cik_url) for cik_url in cik_urls)
		responses = grequests.map(rs, exception_handler=greq_exception_handler)

		cik_content_list = content_zipper(cik_list, responses)


# ciks_to_classifications: given a list of ciks, return a list of tuples with
#                          a cik and a link to a filing associated with that 
#						   cik

def ciks_to_classifications (cik_list):
	cik_urls = []
	cik_start = 0
	filing_links_list = []

	while len(cik_list) > 0 : # only proceed if there are urls left to process
		for cik in cik_list:
			cik_urls.append(create_CIK_URL(cik, cik_start))
		rs = (grequests.get(cik_url) for cik_url in cik_urls)
		responses = grequests.map(rs, exception_handler=greq_exception_handler)

		cik_content_list = content_zipper(cik_list, responses)
		cik_list = []
		cik_urls = []
		for cik_content in cik_content_list:
			# try: 
			filing_links = find_filings(cik_content[1])
			for filing_link in filing_links:
				filing_links_list.append((cik_content[0], str(filing_link)))
			if next_page_present(cik_content[1]):
				cik_list.append(cik_content[0])

		cik_start += 100
	print("loaded CIK pages. Total time elapsed: " + 
		  str(datetime.now() - startTime))
	return filing_links_list


# extract_documents: from a list of links to filings, find the corresponding
#                    document urls and path where it should go

def extract_documents(filing_links_list):
	filing_urls = []
	ciks = []
	for filing_link in filing_links_list:
		ciks.append(filing_link[0])
		filing_urls.append(sec_base + filing_link[1])
	rs = (grequests.get(filing_url) for filing_url in filing_urls)
	responses = grequests.map(rs, exception_handler=greq_exception_handler)
	print("loaded filing pages. Total time elapsed: " + 
		  str(datetime.now() - startTime))
	cik_filing_list = content_zipper(ciks, responses)
	
	doc_path_list = []
	for cik_filing in cik_filing_list:
		soup = BeautifulSoup(cik_filing[1], "html.parser")
		filing_rows = soup.findAll('table')[0].findAll('tr')
		for row in filing_rows:
			if(str(row).find('<td scope="row">8-K') != -1):
				doc_url = sec_base + str(row.findAll('a')[0]['href'])
				last_slash = doc_url.rfind('/')
				trunc_url = doc_url[:last_slash]
				filing_id = trunc_url[trunc_url.rfind('/'):]

				# file_from_url(doc_url, ("output/"+ cik + "/" + filing_id + "_"
				# 	          + doc_url[last_slash + 1:]))
				doc_path_list.append((doc_url, ("output/"+ cik_filing[0] + "/" +
					                  filing_id + "_"+ doc_url[last_slash 
					                  + 1:])))
				continue
	return doc_path_list 

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
	# if soup fails, retrun false
	try:
		table = soup.findAll('table')[1]
		return (str(table).find("Next 100") != -1)
	except:
		return False

# content_zipper: given a list of responses and another list, zip the other
#                 list with the content of each response
def content_zipper (other_list, responses):
	content_unzipped = []
	counter = 0
	for response in responses:
		try: 
			content_unzipped.append(response.content)
		except Exception as e:
			print(e)
			print(other_list[counter])
		finally:
			counter += 1
	return zip(other_list, content_unzipped)



# write_to_file: takes in a file and a path and writes the file to the path.

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

def greq_exception_handler (request, exception):
	print("request failed. Quiting program.")
	print(request.url)
	sys.exit()
	return

##############################################################################
# Testing Functions
##############################################################################



##############################################################################
# Exectution 
##############################################################################




# Go through each line in templist and use as a CIK

with open('CIKlist.txt') as f:
    lines = f.read().splitlines()



# Only process 100 at a time
start_pos = 0
lines_length = len(lines)
while (start_pos < lines_length):
	print(("starting a new batch of downloads. The first CIK is number " 
		  + str(start_pos) + " out of " + str(lines_length)))
	cur_lines = lines[start_pos:(start_pos+50)]


	filing_links_list = ciks_to_classifications(cur_lines)
	url_path_list = extract_documents(filing_links_list)
	if (len(url_path_list) == 0):
		start_pos += BATCH_SIZE
		continue


	rs = (grequests.get(u[0]) for u in url_path_list)

	path_list = zip(*url_path_list)[1]
	responses = grequests.map(rs, exception_handler=greq_exception_handler)
	print("loaded raw filings. Total time elapsed: " + 
			  str(datetime.now() - startTime))

	url_unzipped = []
	content_unzipped = []
	for response in responses:
		url_unzipped.append(str(response.url))
		content_unzipped.append(str(response.content))

	response_path_list = zip(content_unzipped, path_list)

	for res_path in response_path_list:
		write_to_file(res_path[0], res_path[1])


	print("Wrote files locally. Total time elapsed: " + 
		  str(datetime.now() - startTime))
	start_pos += BATCH_SIZE



    