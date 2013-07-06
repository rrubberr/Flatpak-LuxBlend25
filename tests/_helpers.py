import unittest
import mox

class _BaseTest(unittest.TestCase):
	
	def setUp(self):
		self.mox = mox.Mox()
	
	def tearDown(self):
		self.mox.VerifyAll()
		self.mox.UnsetStubs()

class _AnyObject(object):
	def __init__(self, *a, **k):
		pass

class _LiteralObject(object):
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)
