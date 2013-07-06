from _helpers import _BaseTest

from luxrender.util import dict_merge, bEncoder, bDecoder

class Test_LuxRender_Util(_BaseTest):
	
	def test_dict_merge(self):
		
		# Simple append
		d1 = { 'a': 0 }
		d2 = { 'b': 1 }
		d3 = { 'c': 2 }
		
		result = dict_merge(d1, d2, d3)
		
		self.assertDictEqual(result, {
			'a': 0,
			'b': 1,
			'c': 2
		})
		
		# overload
		d1 = { 'c': 0 }
		d2 = { 'b': 1 }
		d3 = { 'c': 2 }
		
		result = dict_merge(d1, d2, d3)
		
		self.assertDictEqual(result, {
			'b': 1,
			'c': 2
		})
	
	
	def test_bEncoder(self):
		enc = bEncoder()
		
		from io import StringIO
		
		src = StringIO()
		src.name = '<INPUT STRING>'
		
		dst = StringIO()
		dst.name = '<OUTPUT STRING>'
		
		src.write('TEST STRING')
		src.seek(0)
		
		enc._Encode(src, dst)
		
		dst.seek(0)
		result = dst.read()
		
		self.assertEqual(result, 'eNoLcQ0OUQgOCfL0cwcAE2ADOA==\n')
	
	def test_bDecoder(self):
		dec = bDecoder()
		
		from io import StringIO
		
		src = StringIO()
		src.name = '<INPUT STRING>'
		
		dst = StringIO()
		dst.name = '<OUTPUT STRING>'
		
		src.write('eNoLcQ0OUQgOCfL0cwcAE2ADOA==\n')
		src.seek(0)
		
		dec._Decode(src, dst)
		
		dst.seek(0)
		result = dst.read()
		
		self.assertEqual(result, 'TEST STRING')
