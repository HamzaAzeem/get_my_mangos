# CURRENTLY ONLY SUPPORTS MANGAREADER/MANGAPANDA LINKS
import requests
import os
import re
from bs4 import BeautifulSoup

LIBRARY_DIR = ''
MANGO_LIST = []
LATEST_CHAP_LIST = []

def parse_config_file():
	with open('./config.txt', 'r') as config:
		global LIBRARY_DIR
		global MANGO_LIST

		LIBRARY_DIR = re.findall('"([^"]*)"', config.readline())[0]
		MANGO_LIST = [line.rstrip('\n') for line in config if 'http://' in line]

		if not os.path.isdir(LIBRARY_DIR):
			os.mkdir(LIBRARY_DIR)

def grab_latest_chapters():
	for mango in MANGO_LIST:
		attempt = 0
		success = False
		while not success:
			try:
				print "CHECKING LATEST " + mango.split('/')[-1].upper() + " CHAPTER"
				r = requests.get(mango)
				soup = BeautifulSoup(r.content)
				success = True
			except:
				if attempt >= 3:
					print "-------------------------------------------------"
					print "SKIPPING THIS MANGO. MAKE SURE THE URL IS CORRECT"
					print "-------------------------------------------------"

					continue
				print "-------------------------------------------------"
				print "FAILED TO LOAD LIST OF CHAPTERS"
				print "TRYING AGAIN..."
				print "-------------------------------------------------"
				attempt += 1
		latest_chapter_link = soup.select('#latestchapters ul > li a')[0].get('href')

		name = latest_chapter_link.split('/')[-2]
		num = latest_chapter_link.split('/')[-1]
		directory = "%s - %s" % (name, num)
		location = LIBRARY_DIR + '/' + directory
		if os.path.isdir(location):
			print "-- LIBRARY ALREADY HAS LATEST CHAPTER. SKIPPING... --"
			continue
		# if MANGAREADER:
		latest_chapter_link = mango + '/' + latest_chapter_link.split('/')[-1]

		LATEST_CHAP_LIST.append(latest_chapter_link)
		print "-- OK --"

def download_images(name, url_list):
	global LIBRARY_DIR
	for page, image_src in enumerate(url_list):
		print "DOWNLOADING PAGE " + str(page + 1) + "/" + str(len(url_list))
		image_response = requests.get(image_src)

		if image_response.status_code == 200:
			location = LIBRARY_DIR + '/' + name
			if not os.path.isdir(location):
				os.mkdir(location)
			file = open(location + "/%s.jpg" % str(page + 1), 'wb')
			file.write(image_response.content)
			file.close()
			print "-- SUCCESS --"

def get_images():
	global LIBRARY_DIR

	for chapter in LATEST_CHAP_LIST:
		name = chapter.split('/')[-2]
		num = chapter.split('/')[-1]
		directory = "%s - %s" % (name, num)

		print "-------------------------------------------------"
		print "DOWNLOADING: " + directory
		print "-------------------------------------------------"
		url_list = []
		print "REQUESTING " + chapter
		r = requests.get(chapter)
		soup = BeautifulSoup(r.content)
		pages = soup.find_all('select')[1].find_all('option')

		# OR FOR MULTIPLE IMAGES ON ONE PAGE:
		# url_list = [img.attrs.get('src') for i in soup.select('#imgholder img')]

		for num, page in enumerate(pages):
			success = False
			while not success:
				print ("LOCATING PAGE " + str(num + 1))
				try:
					r = requests.get(chapter + '/' + str(num + 1))
					s = BeautifulSoup(r.text)
					success = True
				except Exception:
					print Exception
					print "TRYING AGAIN..."

			image_src = s.select('#imgholder img')[0].get('src') if s.select('#imgholder img') != [] else False
			if not image_src:
				print "ERROR IN GRABBING PAGE " + str(num + 1) + "'S IMAGE ELEMENT"
				continue
			print "-- OK --"
			url_list.append(image_src)
		download_images(directory, url_list)

parse_config_file()
grab_latest_chapters()
get_images()
