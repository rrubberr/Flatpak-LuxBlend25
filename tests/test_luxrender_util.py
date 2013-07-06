import tempfile, os

from _helpers import _BaseTest

from luxrender import util

class Test_LuxRender_Util(_BaseTest):
	
	def test_dict_merge(self):
		
		# Simple append
		d1 = { 'a': 0 }
		d2 = { 'b': 1 }
		d3 = { 'c': 2 }
		
		result = util.dict_merge(d1, d2, d3)
		
		self.assertDictEqual(result, {
			'a': 0,
			'b': 1,
			'c': 2
		})
		
		# overload
		d1 = { 'c': 0 }
		d2 = { 'b': 1 }
		d3 = { 'c': 2 }
		
		result = util.dict_merge(d1, d2, d3)
		
		self.assertDictEqual(result, {
			'b': 1,
			'c': 2
		})
	
	# ENCODING is going from BINARY -> STRING
	
	def test_bEncoder(self):
		enc = util.bEncoder()
		
		from io import StringIO, BytesIO
		
		src = BytesIO()
		src.name = '<INPUT BINARY>'
		
		dst = StringIO()
		dst.name = '<OUTPUT STRING>'
		
		src.write(b'TEST BINARY DATA')
		src.seek(0)
		
		enc._Encode(src, dst)
		
		dst.seek(0)
		result = dst.read()
		
		self.assertEqual(result, 'eNoLcQ0OUXDy9HMMilRwcQxxBAAlzwRg\n')
	
	def test_bencode_file2file(self):
		# test operating on files uses binary data for both
		
		with tempfile.TemporaryDirectory() as tempdir:
			in_filename = os.path.join(tempdir, 'input_file')
			out_filename = os.path.join(tempdir, 'output_file')
			
			with open(in_filename, 'wb') as in_file:
				in_file.write(b'TEST BINARY DATA')
			
			result = util.bencode_file2file(in_filename, out_filename)
			
			with open(out_filename, 'rb') as out_file:
				out_data = out_file.read()
		
		self.assertEqual(result, None)
		self.assertEqual(out_data, b'eNoLcQ0OUXDy9HMMilRwcQxxBAAlzwRg' + os.linesep.encode())
		
	def test_bencode_file2string(self):
		
		with tempfile.TemporaryDirectory() as tempdir:
			in_filename = os.path.join(tempdir, 'input_file')
			
			with open(in_filename, 'wb') as in_file:
				in_file.write(b'TEST BINARY DATA')
			
			result = util.bencode_file2string(in_filename)
		
		self.assertEqual(result, 'eNoLcQ0OUXDy9HMMilRwcQxxBAAlzwRg\n')
	
	def test_bencode_file2string_with_size(self):
		
		with tempfile.TemporaryDirectory() as tempdir:
			in_filename = os.path.join(tempdir, 'input_file')
			
			with open(in_filename, 'wb') as in_file:
				in_file.write(b'TEST BINARY DATA')
			
			result = util.bencode_file2string_with_size(in_filename)
		
		self.assertEqual(result, ('eNoLcQ0OUXDy9HMMilRwcQxxBAAlzwRg\n', 33))
	
	# DECODING is going from STRING -> BINARY
	
	def test_bDecoder(self):
		dec = util.bDecoder()
		
		from io import StringIO, BytesIO
		
		src = BytesIO()
		src.name = '<INPUT STRING>'
		
		dst = BytesIO()
		dst.name = '<OUTPUT BINARY>'
		
		src.write(b'eNoLcQ0OUXDy9HMMilRwcQxxBAAlzwRg\n')
		src.seek(0)
		
		dec._Decode(src, dst)
		
		dst.seek(0)
		result = dst.read()
		
		self.assertEqual(result, b'TEST BINARY DATA')
	
	def test_bdecode_file2file(self):
		# test operating on files uses binary data for both
		
		with tempfile.TemporaryDirectory() as tempdir:
			in_filename = os.path.join(tempdir, 'input_file')
			out_filename = os.path.join(tempdir, 'output_file')
			
			with open(in_filename, 'wb') as in_file:
				in_file.write(b'eNoLcQ0OUXDy9HMMilRwcQxxBAAlzwRg\n')
			
			result = util.bdecode_file2file(in_filename, out_filename)
			
			with open(out_filename, 'rb') as out_file:
				out_data = out_file.read()
		
		self.assertEqual(result, None)
		self.assertEqual(out_data, b'TEST BINARY DATA')
	
	def test_bdecode_file2string(self):
		# src is binary file, dest is bytes object
		
		with tempfile.TemporaryDirectory() as tempdir:
			in_filename = os.path.join(tempdir, 'input_file')
			
			with open(in_filename, 'wb') as in_file:
				in_file.write(b'eNoLcQ0OUXDy9HMMilRwcQxxBAAlzwRg\n')
			
			result = util.bdecode_file2string(in_filename)
		
		self.assertEqual(result, b'TEST BINARY DATA')
	
	def test_bdecode_string2file(self):
		with tempfile.TemporaryDirectory() as tempdir:
			out_filename = os.path.join(tempdir, 'output_file')
			
			result = util.bdecode_string2file('eNoLcQ0OUXDy9HMMilRwcQxxBAAlzwRg\n', out_filename)
			
			with open(out_filename, 'rb') as out_file:
				out_data = out_file.read()
		
		self.assertEqual(result, None)
		self.assertEqual(out_data, b'TEST BINARY DATA')
