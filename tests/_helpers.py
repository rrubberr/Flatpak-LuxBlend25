import unittest
import mox

import sys
sys.path.append('src')

import os
os.environ['LUXBLEND_NO_REGISTER'] = '1'

class _BaseTest(unittest.TestCase):
	
	def setUp(self):
		self.mox = mox.Mox()
	
	def tearDown(self):
		self.mox.VerifyAll()
		self.mox.UnsetStubs()
