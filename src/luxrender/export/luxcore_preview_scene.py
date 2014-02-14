# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# David Bucciarelli
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
import bpy
import mathutils

from .. import pyluxcore
from ..export.materials import get_material_volume_defs, get_preview_flip, get_preview_zoom
from ..outputs import LuxLog
from ..properties import find_node

def preview_config(scene):
	cfgProps = pyluxcore.Properties()

	cfgProps.Set(pyluxcore.Property('renderengine.type', ['PATHCPU']))
	cfgProps.Set(pyluxcore.Property('accelerator.instances.enable', [False]))

	# Film
	xr, yr = scene.camera.data.luxrender_camera.luxrender_film.resolution(scene)
	cfgProps.Set(pyluxcore.Property('film.width', [xr]))
	cfgProps.Set(pyluxcore.Property('film.height', [yr]))

	# Image Pipeline
	cfgProps.Set(pyluxcore.Property('film.imagepipeline.0.type', ['TONEMAP_LUXLINEAR']))
	cfgProps.Set(pyluxcore.Property('film.imagepipeline.0.exposure', [1.25]))
	cfgProps.Set(pyluxcore.Property('film.imagepipeline.1.type', ['GAMMA_CORRECTION']))
	cfgProps.Set(pyluxcore.Property('film.imagepipeline.1.value', [1.0]))
	
	# Pixel Filter
	cfgProps.Set(pyluxcore.Property('film.filter.type', ['MITCHELL_SS']))
	
	# Sampler
	cfgProps.Set(pyluxcore.Property('sampler.type', ['METROPOLIS']))

	return cfgProps;

def preview_scene(scene, obj=None, mat=None, tex=None):
	sceneProps = pyluxcore.Properties()
	
	mat_preview_xz = get_preview_flip(mat)
	preview_zoom = get_preview_zoom(mat)

	# Camera
	if tex != None:
		# Texture preview is always topview
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.orig', [0.0, 0.0, 4.0]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.target', [0.0, 0.0, 0.0]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.up', [0.0, 1.0, 0.0]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.fieldofview', [22.5]))
	elif mat.preview_render_type == 'FLAT' and mat_preview_xz == False and tex == None: # mat preview XZ-flip
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.orig', [0.0, 0.0, 4.0]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.target', [0.0, 0.0, 0.0]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.up', [0.0, 1.0, 0.0]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.fieldofview', [22.5 / preview_zoom]))
	else:
		# Standard sideview
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.orig', [0.0, -3.0, 0.5]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.target', [0.5, 0.0, -2.0]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.up', [0.0, 0.0, 1.0]))
		sceneProps.Set(pyluxcore.Property('scene.camera.lookat.fieldofview', [22.5 / preview_zoom]))

	# Light
	
	if tex == None:
		# For usability, previev_scale is not an own property but calculated from the object dimensions
		# A user can directly judge mappings on an adjustable object_size, we simply scale the whole preview
		preview_scale = bpy.data.scenes['Scene'].luxrender_world.preview_object_size / 2
		
		sceneProps.Set(pyluxcore.Property("scene.materials.mat_preview_light_source.type", ["matte"]))
		sceneProps.Set(pyluxcore.Property("scene.materials.mat_preview_light_source.kd", [0.0, 0.0, 0.0]))

		if mat.preview_render_type == 'FLAT' and mat_preview_xz == True:
			emission = 1.5 / preview_scale
			sceneProps.Set(pyluxcore.Property('scene.materials.mat_preview_light_source.emission', [emission, emission, emission]))

			trans = mathutils.Matrix(
				([0.5, 0.0, 0.0, 0.0],
				[0.0, 0.5, 0.0, 0.0],
				[0.0, 0.0, 0.5, 0.0],
				[2.5, -2.5, 2.5, 1.0])
				)
			sceneProps.Set(pyluxcore.Property('scene.objects.preview_light_source.transformation',
				[element for sub in trans for element in sub]))
		elif mat.preview_render_type == 'FLAT' and mat_preview_xz == False:
			emission = 7.0 / preview_scale
			sceneProps.Set(pyluxcore.Property('scene.materials.mat_preview_light_source.emission', [emission, emission, emission]))

			trans = mathutils.Matrix(
				([0.5, 0.0, 0.0, 0.0],
				[0.0, 0.5, 0.0, 0.0],
				[0.0, 0.0, 0.5, 0.0],
				[2.5, -2.5, 4.5, 0.3])
				)
			trans *= mathutils.Matrix.Translation((-2, 1, 5))
			sceneProps.Set(pyluxcore.Property('scene.objects.preview_light_source.transformation',
				[element for sub in trans for element in sub]))
		else:
			emission = 1.0 / preview_scale
			sceneProps.Set(pyluxcore.Property('scene.materials.mat_preview_light_source.emission', [emission, emission, emission]))

			trans = mathutils.Matrix(
				([0.5996068120002747, 0.800294816493988, 2.980232594040899e-08, 0.0],
				[-0.6059534549713135, 0.45399996638298035, 0.6532259583473206, 0.0],
				[0.5227733850479126, -0.3916787803173065, 0.7571629285812378, 0.0],
				[4.076245307922363, -3.0540552139282227, 5.903861999511719, 1.0])
				)
			sceneProps.Set(pyluxcore.Property('scene.objects.preview_light_source.transformation',
				[element for sub in trans for element in sub]))

		sceneProps.Set(pyluxcore.Property('scene.objects.preview_light_source.material', ['mat_preview_light_source']))

		areax = 1
		areay = 1
		points = [-areax / 2.0, areay / 2.0, 0.0, areax / 2.0, areay / 2.0, 0.0, areax / 2.0, -areay / 2.0, 0.0, -areax / 2.0, -areay / 2.0, 0.0]
		sceneProps.Set(pyluxcore.Property('scene.objects.preview_light_source.vertices', points))
		sceneProps.Set(pyluxcore.Property('scene.objects.preview_light_source.faces', [0, 1, 2, 0, 2, 3]))
	
	# Add a background color (light)
	if tex == None:
		inf_gain = 0.1
	else:
		inf_gain = 1.2
	sceneProps.Set(pyluxcore.Property('scene.lights.preview_infinite.type', ['constantinfinite']))
	sceneProps.Set(pyluxcore.Property('scene.lights.preview_infinite.color', [inf_gain, inf_gain, inf_gain]))
	
#	# back drop
#	if mat.preview_render_type == 'FLAT' and mat_preview_xz == True and tex == None:
#		lux_context.attributeBegin()
#		lux_context.transform([
#			5.0, 0.0, 0.0, 0.0,
#			0.0, 5.0, 0.0, 0.0,
#			0.0, 0.0, 5.0, 0.0,
#			0.0, 10.0, 0.0, 1.0
#		])
#		lux_context.scale(4,1,1)
#		lux_context.rotate(90, 1,0,0)
#		checks_pattern_params = ParamSet() \
#			.add_integer('dimension', 2) \
#			.add_string('mapping', 'uv') \
#			.add_float('uscale', 36.8) \
#			.add_float('vscale', 36.0*4)
#		lux_context.texture('checks::pattern', 'float', 'checkerboard', checks_pattern_params)
#		checks_params = ParamSet() \
#			.add_texture('amount', 'checks::pattern') \
#			.add_color('tex1', [0.75, 0.75, 0.75]) \
#			.add_color('tex2', [0.05, 0.05, 0.05])
#		lux_context.texture('checks', 'color', 'mix', checks_params)
#		mat_params = ParamSet().add_texture('Kd', 'checks')
#		lux_context.material('matte', mat_params)
#		bd_shape_params = ParamSet() \
#			.add_integer('ntris', 6) \
#			.add_integer('nvertices', 4) \
#			.add_integer('indices', [0,1,2,0,2,3]) \
#			.add_point('P', [
#				 1.0,  1.0, 0.0,
#				-1.0,  1.0, 0.0,
#				-1.0, -1.0, 0.0,
#				 1.0, -1.0, 0.0,
#			]) \
#			.add_normal('N', [
#				0.0,  0.0, 1.0,
#				0.0,  0.0, 1.0,
#				0.0,  0.0, 1.0,
#				0.0,  0.0, 1.0,
#			]) \
#			.add_float('uv', [
#				0.333334, 0.000000,
#				0.333334, 0.333334,
#				0.000000, 0.333334,
#				0.000000, 0.000000,
#			])
#		lux_context.shape('loopsubdiv', bd_shape_params)
#	else: # sideview
#		lux_context.attributeBegin()
#		lux_context.transform([
#			5.0, 0.0, 0.0, 0.0,
#			0.0, 5.0, 0.0, 0.0,
#			0.0, 0.0, 5.0, 0.0,
#			0.0, 0.0, 0.0, 1.0
#		])
#		if mat.preview_render_type == 'FLAT':
#			lux_context.translate(-0.31, -0.22, -1.2)
#
#		lux_context.scale(4,1,1)
#		checks_pattern_params = ParamSet() \
#			.add_integer('dimension', 2) \
#			.add_string('mapping', 'uv') \
#			.add_float('uscale', 36.8) \
#			.add_float('vscale', 36.0*4) #.add_string('aamode', 'supersample') \
#		lux_context.texture('checks::pattern', 'float', 'checkerboard', checks_pattern_params)
#		checks_params = ParamSet() \
#			.add_texture('amount', 'checks::pattern') \
#			.add_color('tex1', [0.75, 0.75, 0.75]) \
#			.add_color('tex2', [0.05, 0.05, 0.05])
#		lux_context.texture('checks', 'color', 'mix', checks_params)
#		mat_params = ParamSet().add_texture('Kd', 'checks')
#		lux_context.material('matte', mat_params)
#		bd_shape_params = ParamSet() \
#			.add_integer('nlevels', 3) \
#			.add_bool('dmnormalsmooth', True) \
#			.add_bool('dmsharpboundary', False) \
#			.add_integer('ntris', 18) \
#			.add_integer('nvertices', 8) \
#			.add_integer('indices', [0,1,2,0,2,3,1,0,4,1,4,5,5,4,6,5,6,7]) \
#			.add_point('P', [
#				 1.0,  1.0, 0.0,
#				-1.0,  1.0, 0.0,
#				-1.0, -1.0, 0.0,
#				 1.0, -1.0, 0.0,
#				 1.0,  3.0, 0.0,
#				-1.0,  3.0, 0.0,
#				 1.0,  3.0, 2.0,
#				-1.0,  3.0, 2.0,
#			]) \
#			.add_normal('N', [
#				0.0,  0.000000, 1.000000,
#				0.0,  0.000000, 1.000000,
#				0.0,  0.000000, 1.000000,
#				0.0,  0.000000, 1.000000,
#				0.0, -0.707083, 0.707083,
#				0.0, -0.707083, 0.707083,
#				0.0, -1.000000, 0.000000,
#				0.0, -1.000000, 0.000000,
#			]) \
#			.add_float('uv', [
#				0.333334, 0.000000,
#				0.333334, 0.333334,
#				0.000000, 0.333334,
#				0.000000, 0.000000,
#				0.666667, 0.000000,
#				0.666667, 0.333333,
#				1.000000, 0.000000,
#				1.000000, 0.333333,
#			])
#		lux_context.shape('loopsubdiv', bd_shape_params)
#	
#	if bl_scene.luxrender_world.default_interior_volume != '':
#		lux_context.interior(bl_scene.luxrender_world.default_interior_volume)
#	if bl_scene.luxrender_world.default_exterior_volume != '':
#		lux_context.exterior(bl_scene.luxrender_world.default_exterior_volume)
#	
#	lux_context.attributeEnd()
#	
#	# Preview object
#	if obj is not None and mat is not None:
#		trans = mathutils.Matrix.Identity(4)
#		pv_transform = (
#			[0.5, 0.0, 0.0, 0.0],
#			[0.0, 0.5, 0.0, 0.0],
#			[0.0, 0.0, 0.5, 0.0],
#			[0.0, 0.0, 0.5, 1.0]
#			)
#		pv_export_shape = True
#
#		if mat.preview_render_type == 'FLAT':
#			if tex == None :
#				if mat_preview_xz == True:
#					trans *= mathutils.Matrix.Scale(8, 4, (0, 0, 1))
#					trans *= mathutils.Matrix.Rotation(90, 4, (1, 0, 0))
#					pv_transform = (
#						[0.1, 0.0, 0.0, 0.0],
#						[0.0, 0.1, 0.0, 0.0],
#						[0.0, 0.0, 0.2, 0.0],
#						[0.0, 0.06, -1, 1.0]
#						)
#				else:
#					trans *= mathutils.Matrix.Scale(0.25, 4, (1, 0, 0)) * mathutils.Matrix.Scale(2.0, 4, (0, 1, 0)) * mathutils.Matrix.Scale(2.0, 4, (0, 0, 1))
#					trans *= mathutils.Matrix.Rotation(90, 4, (1, 0, 0))
#			else:
#				# keep tex pre always same 
#				trans *= mathutils.Matrix.Rotation(90, 4, (0, 0, 1))
#				trans *= mathutils.Matrix.Scale(2.0, 4, (1, 0, 0)) * mathutils.Matrix.Scale(2.0, 4, (0, 1, 0)) * mathutils.Matrix.Scale(2.0, 4, (0, 0, 1))
#				trans *= mathutils.Matrix.Translation((0, 0, -1))
#
#		if mat.preview_render_type == 'SPHERE':
#			pv_transform = (
#				[0.1, 0.0, 0.0, 0.0],
#				[0.0, 0.1, 0.0, 0.0],
#				[0.0, 0.0, 0.1, 0.0],
#				[0.0, 0.0, 0.5, 1.0]
#				)
#		
#		if mat.preview_render_type == 'CUBE':
#			trans *= mathutils.Matrix.Scale(0.8, 4, (1, 0, 0)) * mathutils.Matrix.Scale(0.8, 4, (0, 1, 0)) * mathutils.Matrix.Scale(0.8, 4, (0, 0, 1))
#			trans *= mathutils.Matrix.Rotation(-35, 4, (0, 0, 1))
#		if mat.preview_render_type == 'MONKEY':
#			pv_transform = (
#				[1.0573405027389526, 0.6340668201446533, 0.0, 0.0],
#				[-0.36082395911216736, 0.601693332195282, 1.013795018196106, 0.0],
#				[0.5213892459869385, -0.8694445490837097, 0.7015902996063232, 0.0],
#				[0.0, 0.0, 0.5, 1.0]
#				)
#		if mat.preview_render_type == 'HAIR':
#			pv_export_shape = False
#		if mat.preview_render_type == 'SPHERE_A':
#			pv_export_shape = False
#		
#		trans *= mathutils.Matrix(pv_transform)
#		
#		if pv_export_shape: #Any material, texture, light, or volume definitions created from the node editor do not exist before this conditional!
#			GE = GeometryExporter(lux_context, scene)
#			GE.is_preview = True
#			GE.geometry_scene = scene
#			for mesh_mat, mesh_name, mesh_type, mesh_params in GE.buildNativeMesh(obj):
#				if tex != None:
#					lux_context.transformBegin()
#					lux_context.identity()
#					texture_name = export_preview_texture(lux_context, tex)
#					lux_context.transformEnd()
#					
#					lux_context.material('matte', ParamSet().add_texture('Kd', texture_name))
#				else:
#					mat.luxrender_material.export(scene, lux_context, mat, mode='direct')
#					int_v, ext_v = get_material_volume_defs(mat)
#					if int_v != '' or ext_v != '':
#						if int_v != '': lux_context.interior(int_v)
#						if ext_v != '': lux_context.exterior(ext_v)
#
#					if int_v == '' and bl_scene.luxrender_world.default_interior_volume != '':
#						lux_context.interior(bl_scene.luxrender_world.default_interior_volume)
#					if ext_v == '' and bl_scene.luxrender_world.default_exterior_volume != '':
#						lux_context.exterior(bl_scene.luxrender_world.default_exterior_volume)
#					
#					output_node = find_node(mat, 'luxrender_material_output_node')
#					if mat.luxrender_material.nodetree:
#						object_is_emitter = False
#						if output_node != None:
#							light_socket = output_node.inputs[3]
#							if light_socket.is_linked:
#								light_node = light_socket.links[0].from_node
#								object_is_emitter = light_socket.is_linked
#					else:
#						object_is_emitter = hasattr(mat, 'luxrender_emission') and mat.luxrender_emission.use_emission
#					if object_is_emitter:
#						if not mat.luxrender_material.nodetree:
#						# lux_context.lightGroup(mat.luxrender_emission.lightgroup, [])
#							lux_context.areaLightSource( *mat.luxrender_emission.api_output(obj) )
#						else:
#							tex_maker = luxrender_texture_maker(lux_context, mat.luxrender_material.nodetree)
#							lux_context.areaLightSource( *light_node.export(tex_maker.make_texture) )
#
#				lux_context.shape(mesh_type, mesh_params)
#		else:
#			lux_context.shape('sphere', ParamSet().add_float('radius', 1.0))
#
#		lux_context.attributeEnd()
	
	return sceneProps
	
