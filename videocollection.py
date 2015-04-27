import magnet
import copy


################# VIDEO QUALITY RANKING ###############################

def enum(**enums):
    return type('Enum', (), enums)

quality = enum(_1080p=8, _720p=7, _1080i = 6, _720i = 5, _576p = 4, _480p = 3, _576i = 2, _480i = 1, unknown = 0)
quality_priority = enum(speed=1,quality=2)

def print_quality(q):
	if q == quality._480i:
		return "480i"

	if q == quality._576i:
		return "576i"

	if q == quality._480p:
		return "480p"

	if q == quality._576p:
		return "576i"

	if q == quality._720i:
		return "720i"

	if q == quality._1080i:
		return "1080i"

	if q == quality._720p:
		return "720p"

	if q == quality._1080p:
		return "1080p"

	return "unknown"

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

######GENERIC VIDEO COLLECTION CLASSES######

class show():
	def __init__(self,id,name=None):
		self.id = id
		self.name = name
		self.seasons = {}

	def set_name(self,name):
		self.name = name

	def get_name(self):
		return self.name

	def get_id(self):
		return self.id
		

	def add_episode(self,season,episode,video):
		if season not in self.seasons:
			self.seasons[season] = {}
		self.seasons[season][episode] = copy.deepcopy(video)


	def get_season_list(self):
		return [i for i in self.seasons]

	def get_episode(self,season,episode):
		return self.seasons[season][episode]

	def get_season(self,season):
		return [self.seasons[season][i] for i in self.seasons[season]]

	def search_episodes(self,terms=None):
		retval = []
		for i in self.get_season_list():
			for j in self.seasons[i]:
				if terms == None or terms.lower() in self.seasons[i][j].get_name().lower():
					retval.append((i,j,self.seasons[i][j].get_name()))
		return retval


	def get_episode(self,season,episode):
		#Need to better check whether the episode exists
		return copy.deepcopy(self.seasons[season][episode])



class video():
	def __init__(self,id,name=None):
		self.id = id
		self.name = name
		self.torrents = {}

	def set_name(self,name):
		self.name = name

	def get_id(self):
		return self.id

	def get_name(self):
		return self.name


	def add_torrent(self,quality,btih):
		self.torrents[quality] = magnet.get_binary_infohash(btih)


	def list_magnets(self):
		listing = {}
		for i in self.torrents:
			listing[print_quality(i)] = magnet.synth_magnet(self.torrents[i])
		return listing


	def get_magnet(self,qual=quality._1080p,qual_prio=quality_priority.quality):
		hash = self.get_infohash(qual,qual_prio)
		return magnet.synth_magnet(hash)

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
