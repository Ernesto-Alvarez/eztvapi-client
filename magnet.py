import base64

class InvalidDataError(ValueError):
	pass

class NotMagnetLinkError(InvalidDataError):
	pass

class NotBTIHError(InvalidDataError):
	pass

def is_infohash(hash):
	if is_binary_infohash(hash):
		return True

	if is_hex_infohash(hash):
		return True

	if is_base32_infohash(hash):
		return True

	return False

def is_binary_infohash(hash):
	return(len(hash) == 20)

def is_hex_infohash(hash):
	return (len(hash) == 40 and all(i in '1234567890abcdefABCDEF' for i in hash))

def is_base32_infohash(hash):
	return (len(hash) == 32 and all(i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for i in hash))

def is_magnet(url):
	if not __is_magnet_format(url):
		return False
	hash = __get_raw_infohash_from_magnet(url)

	if is_infohash(hash):
		return True
	else:
		return False

def __is_magnet_format(url):
	return url[:8] == 'magnet:?' and 'btih' in url

def __get_raw_infohash_from_magnet(url):
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



def __convert_hash_to_raw(hash):
	if is_binary_infohash(hash):
		return hash
	elif is_hex_infohash(hash):
		return hash.decode('hex')
	elif is_base32_infohash(hash):
		return base64.b32decode(hash)
	else:
		raise NotBTIHError()

def get_binary_infohash(url):
	if is_magnet(url):
		hash = __get_raw_infohash_from_magnet(url)
	elif is_infohash(url):
		hash = url
	else:
		raise NotMagnetLinkError()

	if is_infohash(hash):
		return __convert_hash_to_raw(hash) 
	else:
		raise NotBTIHError()

def synth_magnet(hash):
	if not is_magnet(hash) and not is_infohash(hash):
		raise NotBTIHError()
	
	if not is_binary_infohash(hash):
		hash = get_binary_infohash(hash)

	hex_hash = hash.encode('hex')

	link = 'magnet:?xt=urn:btih:' + hex_hash 

	return link
	