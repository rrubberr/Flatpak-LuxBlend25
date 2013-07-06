

def log(*a,**k):
	pass

class Addon(object):
	def __init__(self, info):
		self.BL_VERSION = info['version']
	
	# mocked out decorator
	def addon_register_class(self, cls):
		return cls

class declarative_property_group(object):
	pass
