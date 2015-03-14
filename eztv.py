import requests


import sys
import time
import datetime
import magnet

################# VIDEO QUALITY RANKING ###############################

def enum(**enums):
    return type('Enum', (), enums)

quality = enum(_1080p=8, _720p=7, _1080i = 6, _720i = 5, _576p = 4, _480p = 3, _576i = 2, _480i = 1, unknown = 0)
quality_priority = enum(speed=1,quality=2)

def get_quality_from_string(string):

	if type(string) is int:
		return string

	if string == '480i':
		return quality._480i

	if string == '480p':
		return quality._480p

	if string == '576i':
		return quality._576i

	if string == '576p':
		return quality._576p

	if string == '720i':
		return quality._720i

	if string == '720p':
		return quality._720p

	if string == '1080i':
		return quality._1080i

	if string == '1080p':
		return quality._1080p

	return quality.unknown

####################FORCING UTF-8#################################3

def set_output_encoding(encoding='utf-8'):
    import sys
    import codecs
    '''When piping to the terminal, python knows the encoding needed, and
       sets it automatically. But when piping to another program (for example,
       | less), python can not check the output encoding. In that case, it 
       is None. What I am doing here is to catch this situation for both 
       stdout and stderr and force the encoding'''
    current = sys.stdout.encoding
    if current is None :
        sys.stdout = codecs.getwriter(encoding)(sys.stdout)
    current = sys.stderr.encoding
    if current is None :
        sys.stderr = codecs.getwriter(encoding)(sys.stderr)


#######################EZTV CLASSES###############################


class index():
	def __init__(self,url = 'http://eztvapi.re/'):
		self.base_url = url
		self.show_list = {}
		self.retrieved_pages = []
		self.failed_pages = []

		self.get_show_pages()
		self.download_show_list()

	def get_show_pages(self):
		pages = requests.get(self.base_url + 'shows',proxies={'http': 'http://127.0.0.1:8080'})
		for i in pages.json():
			if i not in self.retrieved_pages and i not in self.failed_pages:
				self.failed_pages.append(i)
		
	def download_show_list(self):

		for i in self.failed_pages:
			try:
				shows = requests.get(self.base_url + i,proxies={'http': 'http://127.0.0.1:8080'})
				for j in shows.json():
					self.show_list[j['_id']] = j['title']
			except ValueError:
				pass

			time.sleep(1)

	def list_shows(self):
		list = []
		for i in self.show_list:
			list.append((self.show_list[i],i))
		return list.sort()

	def search_shows(self,term):
		list = []
		for i in self.show_list:
			if term.lower() in self.show_list[i].lower():
				list.append((self.show_list[i],i))
		sorted = list.sort()
		if sorted != None:
			return sorted
		else:
			return list

	def get_show_by_name(self,search):
		result = (self.search_shows(search))[0][1]
		return self.get_show(result)

	def get_show(self,id):
		return show(id)

class show():
	def __init__(self,id,base_url='http://eztvapi.re/'):
		self.id = id
		self.base_url = base_url
		self.seasons = {}

		self.__download_show_data()

	def __download_show_data(self):
		r = requests.get(self.base_url + 'show/' + self.id,proxies={'http': 'http://127.0.0.1:8080'})
		show_data = r.json()

		self.name = show_data['title']
		self.status = show_data['status']

		for i in show_data['episodes']:
			season = i['season']
			episode_number = i['episode']
			ep_title = i['title']
			
			if season not in self.seasons:
				self.seasons[season] = {}
			#FIXME: caso en el que el episodio ya esta agregado
			self.seasons[season][episode_number] = episode()
			for j in i['torrents']:
				if j != '0':
					self.seasons[season][episode_number].add_torrent(get_quality_from_string(j),i['torrents'][j]['url'])

	def get_season_list(self):
		retval = []
		for i in self.seasons:
			retval.append(i)
		return retval

	def get_episode_list(self):
		retval = []
		for i in self.get_season_list():
			for j in self.seasons[i]:
				retval.append(str(i) + 'x' + str(j))
		return retval
			
	def get_episode(self,season,ep_number):
		return self.seasons[season][ep_number]

	def get_season(self,season):
		retval = []
		for i in self.seasons[season]:
			retval.append(self.seasons[season][i])
		return retval

class episode():
	def __init__(self):
		self.torrents = {}

	def add_torrent(self,quality,btih):
		#Magnet lib handles adding raw infohashes
		self.torrents[quality] = magnet.get_infohash_from_magnet(btih)
			
	def list_files(self):
		for i in self.torrents:
			print i,self.torrents[i]

	def get_magnet(self,qual=quality._1080p,qual_prio=quality_priority.quality):
		return 'magnet:?xt=urn:btih:' + self.get_infohash(qual,qual_prio)

	def get_infohash(self,qual=quality._1080p,qual_prio=quality_priority.quality):
		if qual in self.torrents:
			return self.torrents[qual]
		else:
			if len(self.torrents) == 0:
				return None

			better = []
			worse = []
			for i in self.torrents:
				if i < qual:
					worse.append(i)
				else:
					better.append(i)

			if len(worse) == 0:
				best_worse = min(better)
			else:
				best_worse = max(worse)

			if len(better) == 0:
				worst_better = max(worse)
			else:
				worst_better = min(better)


			if qual_prio == quality_priority.quality:
				return self.torrents[worst_better]
			else:
				return self.torrents[best_worse]



