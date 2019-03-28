import requests
from bs4 import BeautifulSoup
from datetime import date
import csv

def getPage(link):
	content = requests.get(link).content	
	return content

def search_wikicfp(conf_name, year = date.today().year):
	wikicfp_url = "http://wikicfp.com"
	base_link = "http://wikicfp.com/cfp/servlet/tool.search?q=<name>&year=<year>"
	base_link = base_link.replace("<name>", conf_name)
	base_link = base_link.replace("<year>", str(year))

	soup = BeautifulSoup(getPage(base_link), 'html.parser')
	conf_rows = soup.find("div", class_="contsec").table.find_all("tr")

	conf_links = []

	for row in conf_rows:
		try:
			if conf_name.lower() in row.td.string.lower():
				conf_href = row.td.a['href']
				conf_links.append(wikicfp_url + conf_href)
		except:
			# sometimes, row.td.string is None
			pass

	return conf_links

def getSpanDate(ele, pname = "v:startDate"):
	d = ''
	try:
		d = ele.select("span[property='" + pname + "']")[0]['content']
		d = d.split("T")[0]
	except:
		pass
	return d

def scrape_details(link):
	details = []

	soup = BeautifulSoup(getPage(link), 'lxml')
	conf_rows = soup.find("table", class_="gglu").find_all("tr")

	conf_name_fq = soup.select("span[property='v:description']")[0].text.strip()	
	conf_startdate = getSpanDate(soup)
	conf_enddate = getSpanDate(soup, "v:endDate")
	conf_location = soup.select("span[property='v:locality']")[0]['content']

	details += [conf_name_fq, conf_startdate, conf_enddate, conf_location]

	(conf_href, conf_deadline, conf_notification, conf_camera_ready) = ('', '', '', '')

	# TODO: Find a better way to extract link of the conference
	try:
		for row in soup.find("div", class_="contsec").table.find_all("tr"):
			if "Link:" in row.get_text():
				conf_href = row.a['href']
				break				
	except Exception as e:
		print(e)
		pass

	for row in conf_rows:
		if "submission deadline" in row.get_text().strip().lower():
			conf_deadline = getSpanDate(row)

		elif "notification due" in row.get_text().strip().lower():	
			conf_notification = getSpanDate(row)

		elif "final version due" in row.get_text().strip().lower():
			conf_camera_ready = getSpanDate(row)

	details += [conf_deadline, conf_notification, conf_camera_ready, conf_href]

	return details

from sys import argv

conf_links = search_wikicfp(argv[1])

for link in conf_links:
	details = scrape_details(link)
	print(details)
	with open("semap.csv", "a+") as csvfile:
		csv_writer = csv.writer(csvfile)
		csv_writer.writerow(details)
