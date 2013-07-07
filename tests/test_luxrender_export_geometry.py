from _helpers import _BaseTest, _LiteralObject

from luxrender import export
from luxrender.export import geometry

class Test_GeometryExporter(_BaseTest):
	
	def setUp(self):
		super(Test_GeometryExporter, self).setUp()
		
		self.lux_context = self.mox.CreateMockAnything()
		
	
	def test_buildMesh(self):
		
		# Data Setup -----------------------------------------------------------
		visibility_scene = _LiteralObject(
			luxrender_engine=_LiteralObject(
				export_type='INT',
				write_files=False
			),
			luxrender_testing=_LiteralObject(
				object_analysis=True,
			),
			camera=_LiteralObject(
				data=_LiteralObject(
					luxrender_camera=_LiteralObject(
						usemblur=False,
						objectmblur=False
					)
				)
			),
			frame_current=1
		)
		
		luxrender_mesh = self.mox.CreateMockAnything()
		luxrender_mesh.mesh_type = 'global'
		
		luxrender_mesh.get_paramset().AndReturn(export.ParamSet())
		
		obj = self.mox.CreateMockAnything()
		obj.parent = None
		obj.data = _LiteralObject(
			name='unit-test-object',
			luxrender_mesh=luxrender_mesh,
			users=1
		)
		obj.luxrender_object=_LiteralObject(
			append_proxy=False
		)
		
		
		geometry_scene = self.mox.CreateMockAnything()
		geometry_scene.name = 'unit-test-scene'
		
		vert = _LiteralObject(
			co=[1,2,3]
		)
		
		face = _LiteralObject(
			material_index=0,
			vertices = [0, 0 ,0],
			use_smooth=False,
			normal=[4,5,6],
			index=0
		)
		
		material = _LiteralObject(
		)
		
		mesh = self.mox.CreateMockAnything()
		mesh.tessfaces = [face]
		mesh.materials = [material]
		mesh.tessface_uv_textures = []
		mesh.tessface_vertex_colors=_LiteralObject(
			active=False
		)
		mesh.vertices = [vert, vert, vert]
		
		obj.to_mesh(geometry_scene, True, 'RENDER').AndReturn(mesh)
		
		
		# Execute --------------------------------------------------------------
		self.mox.ReplayAll()
		
		GE = geometry.GeometryExporter(self.lux_context, visibility_scene)
		GE.geometry_scene = geometry_scene
		
		result_1 = GE.buildMesh(obj)
		
		# running a 2nd time gets the result_1 from cache,
		# so we don't set up any extra .AndReturn() mocks
		self.assertEqual(GE.ExportedObjects.cache_keys, set([(geometry_scene, obj)]))
		result_2 = GE.buildMesh(obj)
		
		# Verify ---------------------------------------------------------------
		expected = [
			(
				'unit-test-object-unit-test-scene_m000',
				0,
				'mesh',
				[
					['integer triindices', [0, 1, 2]],
					['point P', [1, 2, 3, 1, 2, 3, 1, 2, 3]],
					['normal N', [4, 5, 6, 4, 5, 6, 4, 5, 6]]
				]
			)
		]
		self.assertEqual(result_1, expected)
		self.assertEqual(result_2, expected)
