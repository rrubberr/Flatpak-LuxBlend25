from _helpers import _BaseTest

from luxrender import export

class Test_LuxRender_Export_ExportCache(_BaseTest):
	
	def setUp(self):
		super(Test_LuxRender_Export_ExportCache, self).setUp()
		
		self.exportCache = export.ExportCache('unit-test')
	
	def test_add_have_get_clear(self):
		
		self.assertEqual(self.exportCache.name, 'unit-test')
		
		self.assertEqual(len(self.exportCache.cache_keys), 0)
		self.assertEqual(len(self.exportCache.cache_items), 0)
		self.assertEqual(len(self.exportCache.serial_counter), 0)
		
		self.assertFalse(self.exportCache.have('test-key-1'))
		
		self.exportCache.add('test-key-1', { 'a': 0 })
		
		self.assertTrue(self.exportCache.have('test-key-1'))
		
		self.assertEqual(len(self.exportCache.cache_keys), 1)
		self.assertEqual(len(self.exportCache.cache_items), 1)
		self.assertEqual(len(self.exportCache.serial_counter), 0)
		
		self.assertEqual(self.exportCache.get('test-key-1'), { 'a': 0 })
		
		self.exportCache.clear()
		
		self.assertEqual(len(self.exportCache.cache_keys), 0)
		self.assertEqual(len(self.exportCache.cache_items), 0)
		self.assertEqual(len(self.exportCache.serial_counter), 0)
		
		self.assertRaises(
			Exception,
			self.exportCache.get,
				'test-key-1'
		)

class Test_ParamSetItem(_BaseTest):
	
	def test_getSize(self):
		
		paramSetItem = export.ParamSetItem('TYPE', 'NAME', 'VALUE')
		self.assertEqual(paramSetItem.getSize(), 105)
	
	def test_to_string(self):
		
		paramSetItem = export.ParamSetItem('TYPE', 'NAME', 'VALUE')
		self.assertEqual(paramSetItem.to_string(), '# unknown param (TYPE, NAME, VALUE)')
