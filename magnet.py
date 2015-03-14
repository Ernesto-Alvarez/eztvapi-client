class NotMagnetLink(ValueError):
	pass

class NotBTIH(ValueError):
	pass

def is_infohash(hash):
	if hash == None:
		return False
	return (len(hash) == 32 or len(hash) == 40) and hash.isalnum() and hash.isupper()



def is_magnet(url):
	return url[:7] == 'magnet:' and 'btih' in url

def get_infohash_from_magnet_no_check(url):
	
	url_body = url.split('?')[1]
	url_params = url_body.split('&')
	for i in url_params:
		if i[0:2] == 'xt':
			xt_parts = i.split(':')
			if xt_parts[1] != 'btih':
				return None
			else:
				if not is_infohash(xt_parts[2]):
					return None
				return xt_parts[2]

def get_infohash_from_magnet(url):
	if is_infohash(url):
		return url

	if not is_magnet(url):
		raise NotMagnetLink()

	btih = get_infohash_from_magnet_no_check(url)

	if not is_infohash(btih):
		raise NotBTIH()

	return btih

