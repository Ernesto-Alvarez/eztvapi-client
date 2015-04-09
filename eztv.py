import requests
import copy
import magnet
import videocollection
import threading

class index():
	def __init__(self,url = 'http://eztvapi.re/',retry=True):
		self.base_url = url
		self.show_list = {}
		self.missing_pages = []
		self.get_all_show_pages()
		self.page_maintenance = None
		self.set_auto_retry(retry)


	def set_auto_retry(self,retry):
		#DOES NOT WORK. 
		#Object will permanently remain in scope if auto retry is active and all references are lost.
		#Timer will hold a reference of its own and will run forever, causing a memory (and thread) leak.
		if retry == True:
			if self.page_maintenance == None:
				self.page_maintenance = threading.Timer(15,self.__auto_retry_pages)
				self.page_maintenance.daemon = True
				self.page_maintenance.start()
		else:
			if self.page_maintenance != None:
				self.page_maintenance.cancel()
				self.page_maintenance = None

	def __auto_retry_pages(self):
		self.get_missing_pages()
		self.page_maintenance = threading.Timer(60,self.__auto_retry_pages)
		self.page_maintenance.start()

	def get_all_show_pages(self):	
		pages = requests.get(self.base_url + 'shows',proxies={'http': 'http://127.0.0.1:8080'})
		self.missing_pages = []
		for i in pages.json():
			self.missing_pages.append(i)
		self.get_missing_pages()

	def get_missing_pages(self):
		for i in copy.copy(self.missing_pages):
			self.__get_show_page(i)

	def __get_show_page(self,page):
		print "Getting: " + page
		shows = requests.get(self.base_url + page,proxies={'http': 'http://127.0.0.1:8080'})
		try:
			for j in shows.json():
				self.show_list[j['_id']] = j['title']
			self.missing_pages.remove(page)
		except ValueError:
			pass			

	def search_shows(self,terms=None):
		retval = []
		for i in self.show_list:
			if terms == None or terms.lower() in self.show_list[i].lower():
				retval.append((i,self.show_list[i]))
		return retval

	def get_show(self,id):
		r = requests.get(self.base_url + 'show/' + id,proxies={'http': 'http://127.0.0.1:8080'})
		show_data = r.json()

		retvalue = videocollection.show(show_data['_id'],show_data['title'])
		
		for ep in show_data['episodes']:
			episode = videocollection.video(ep['tvdb_id'],ep['title'])
			for quality in ep['torrents']:
				if quality != "0":
					episode.add_torrent(videocollection.get_quality_from_string(quality),ep['torrents'][quality]['url'])
			retvalue.add_episode(ep['season'],ep['episode'],episode)
		return retvalue

