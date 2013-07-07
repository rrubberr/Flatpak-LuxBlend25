import unittest
import mox

# LuxBlend stores objects in sets/dict keys for caching,
# therefore our mock obejcts need to be hashable
mox.MockAnything.__hash__ = lambda self: id(self)

class _BaseTest(unittest.TestCase):
	
	def setUp(self):
		self.mox = mox.Mox()
	
	def tearDown(self):
		self.mox.VerifyAll()
		self.mox.UnsetStubs()

class _AnyObject(object):
	def __init__(self, *a, **k):
		pass

def _LiteralObject(_base=object, *la, **lk):
	class _BasedLiteralObject(_base):
		def __init__(self, *a, **k):
			self.__dict__.update(k)
		def __repr__(self):
			return '<_LiteralObject(%s) %s>' % (_base.__name__, self.__dict__)
	
	return _BasedLiteralObject(*la, **lk)
