from _helpers import _BaseTest

from luxrender import export

class Test_LuxRender_Export_ExportCache(_BaseTest):
	
	def test_add_have_get_clear(self):
		
		exportCache = export.ExportCache('unit-test')
		
		self.assertEqual(exportCache.name, 'unit-test')
		
		self.assertEqual(len(exportCache.cache_keys), 0)
		self.assertEqual(len(exportCache.cache_items), 0)
		self.assertEqual(len(exportCache.serial_counter), 0)
		
		self.assertFalse(exportCache.have('test-key-1'))
		
		exportCache.add('test-key-1', { 'a': 0 })
		
		self.assertTrue(exportCache.have('test-key-1'))
		
		self.assertEqual(len(exportCache.cache_keys), 1)
		self.assertEqual(len(exportCache.cache_items), 1)
		self.assertEqual(len(exportCache.serial_counter), 0)
		
		self.assertEqual(exportCache.get('test-key-1'), { 'a': 0 })
		
		exportCache.clear()
		
		self.assertEqual(len(exportCache.cache_keys), 0)
		self.assertEqual(len(exportCache.cache_items), 0)
		self.assertEqual(len(exportCache.serial_counter), 0)
		
		self.assertRaises(
			Exception,
			exportCache.get,
				'test-key-1'
		)

class Test_ParamSetItem(_BaseTest):
	
	def test_getSize(self):
		
		paramSetItem = export.ParamSetItem('TYPE', 'NAME', 'VALUE')
		self.assertEqual(paramSetItem.getSize(), 105)
	
	def test_to_string_all_types_scalar(self):
		
		# param types which have single values only
		test_data = (
			('float',	12.34,	'"float NAME" [12.340000000000000]'),
			('integer',	12,		'"integer NAME" [12]'),
			('string',	'TEST',	'"string NAME" ["TEST"]'),
			('texture',	'TEST',	'"texture NAME" ["TEST"]'),
			('bool',	True,	'"bool NAME" ["true"]'),
			('bool',	False,	'"bool NAME" ["false"]'),
			('bool',	1,		'"bool NAME" ["true"]'),
			('bool',	0,		'"bool NAME" ["false"]'),
		)
		
		for ps_type, ps_data, ps_string in test_data:
			paramSetItem = export.ParamSetItem(ps_type, 'NAME', ps_data)
			self.assertEqual(paramSetItem.to_string(), ps_string)
	
	def test_to_string_all_types_array(self):
		
		# param types which work with arrays
		test_data = (
			('float',	[12.34, 56.78],		'"float NAME" [12.340000000000000 56.780000000000001]'),
			('integer',	[12, 56],			'"integer NAME" [12 56]'),
			('string',	['TEST1', 'TEST2'],	'"string NAME" ["TEST1"\n"TEST2"]'),
			('vector',	[1,2,3],			'"vector NAME" [1.000000000000000 2.000000000000000 3.000000000000000]'),
			('point',	[1,2,3],			'"point NAME" [1.000000000000000 2.000000000000000 3.000000000000000]'),
			('normal',	[1,2,3],			'"normal NAME" [1.000000000000000 2.000000000000000 3.000000000000000]'),
			('color',	[1,2,3],			'"color NAME" [1.00000000 2.00000000 3.00000000]'),
		)
		
		for ps_type, ps_data, ps_string in test_data:
			paramSetItem = export.ParamSetItem(ps_type, 'NAME', ps_data)
			self.assertEqual(paramSetItem.to_string(), ps_string)
	
	def test_to_string_invalid_type(self):
		
		paramSetItem = export.ParamSetItem('TYPE', 'NAME', 'VALUE')
		self.assertEqual(paramSetItem.to_string(), '# unknown param (TYPE, NAME, VALUE)')
	
	def test_as_list(self):
		paramSetItem = export.ParamSetItem('TYPE', 'NAME', 'VALUE')
		self.assertEqual(paramSetItem[:], ['TYPE NAME', 'VALUE'])

class Test_ParamSet(_BaseTest):
	
	def test_add(self):
		paramSet = export.ParamSet()
		
		self.assertEqual(len(paramSet), 0)
		self.assertEqual(len(paramSet.names), 0)
		
		paramSet.add('TYPE', 'NAME', 'VALUE A')
		
		self.assertEqual(len(paramSet), 1)
		self.assertEqual(len(paramSet.names), 1)
		
		# same name replaces old value
		paramSet.add('TYPE', 'NAME', 'VALUE B')
		
		self.assertEqual(len(paramSet), 1)
		self.assertEqual(len(paramSet.names), 1)
		self.assertEqual(paramSet[0][:], ['TYPE NAME', 'VALUE B'])

class Test_functions(_BaseTest):
	
	def _make_obj(self, _hide_render, _layers):
		class _obj(object):
			hide_render = _hide_render
			layers = _layers
		return _obj()
	
	def _make_scene(self, _scene_layers, _render_active_layers):
		class _scene(object):
			layers = _scene_layers
			class render:
				class layers:
					class active:
						layers = _render_active_layers
		return _scene()
	
	def test_is_obj_visible(self):
		T = True
		F = False
		
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [F]), self._make_obj(F, [F]), F), 	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [F]), self._make_obj(F, [F]), T),	T)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [F]), self._make_obj(F, [T]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [F]), self._make_obj(F, [T]), T),	T)
		
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [F]), self._make_obj(T, [F]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [F]), self._make_obj(T, [F]), T),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [F]), self._make_obj(T, [T]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [F]), self._make_obj(T, [T]), T),	F)
		
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [T]), self._make_obj(F, [F]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [T]), self._make_obj(F, [F]), T),	T)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [T]), self._make_obj(F, [T]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [T]), self._make_obj(F, [T]), T),	T)
		
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [T]), self._make_obj(T, [F]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [T]), self._make_obj(T, [F]), T),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [T]), self._make_obj(T, [T]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([F], [T]), self._make_obj(T, [T]), T),	F)
		
		
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [F]), self._make_obj(F, [F]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [F]), self._make_obj(F, [F]), T),	T)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [F]), self._make_obj(F, [T]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [F]), self._make_obj(F, [T]), T),	T)
		
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [F]), self._make_obj(T, [F]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [F]), self._make_obj(T, [F]), T),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [F]), self._make_obj(T, [T]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [F]), self._make_obj(T, [T]), T),	F)
		
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [T]), self._make_obj(F, [F]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [T]), self._make_obj(F, [F]), T),	T)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [T]), self._make_obj(F, [T]), F),	T)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [T]), self._make_obj(F, [T]), T),	T)
		
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [T]), self._make_obj(T, [F]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [T]), self._make_obj(T, [F]), T),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [T]), self._make_obj(T, [T]), F),	F)
		self.assertEqual(export.is_obj_visible(self._make_scene([T], [T]), self._make_obj(T, [T]), T),	F)
	
	def test_matrix_to_list(self):
		
		test_mat = [
			[0,1,2,3],
			[4,5,6,7],
			[8,9,0,1],
			[2,3,4,5]
		]
		
		self.assertEqual(export.matrix_to_list(test_mat, False), [
			0.0, 4.0, 8.0, 2.0,
			1.0, 5.0, 9.0, 3.0,
			2.0, 6.0, 0.0, 4.0,
			3.0, 7.0, 1.0, 5.0
		])
