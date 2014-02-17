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

from .. import pyluxcore
from ..outputs import LuxManager, LuxLog
from ..outputs.luxcore_api import ToValidLuxCoreName

class BlenderSceneConverter(object):
	blScene = None
	lcScene = None
	
	scnProps = None
	cfgProps = None
	
	materialsCache = set()
	texturesCache = set()
	
	def __init__(self, blScene):
		LuxManager.SetCurrentScene(blScene)

		self.blScene = blScene
		self.lcScene = pyluxcore.Scene()
		self.scnProps = pyluxcore.Properties()
		self.cfgProps = pyluxcore.Properties()
	
	def ConvertObjectGeometry(self, obj):
		try:
			mesh_definitions = []

			if obj.hide_render:
				return mesh_definitions

			mesh = obj.to_mesh(self.blScene, True, 'RENDER')
			if mesh is None:
				LuxLog('Cannot create render/export object: %s' % obj.name)
				return mesh_definitions

			mesh.transform(obj.matrix_world)
			mesh.update(calc_tessface = True)

			# Collate faces by mat index
			ffaces_mats = {}
			mesh_faces = mesh.tessfaces
			for f in mesh_faces:
				mi = f.material_index
				if mi not in ffaces_mats.keys():
					ffaces_mats[mi] = []
				ffaces_mats[mi].append(f)
			material_indices = ffaces_mats.keys()

			number_of_mats = len(mesh.materials)
			if number_of_mats > 0:
				iterator_range = range(number_of_mats)
			else:
				iterator_range = [0]

			for i in iterator_range:
				try:
					if i not in material_indices:
						continue

					mesh_name = '%s-%s_m%03d' % (obj.data.name, self.blScene.name, i)

					uv_textures = mesh.tessface_uv_textures
					if len(uv_textures) > 0:
						if uv_textures.active and uv_textures.active.data:
							uv_layer = uv_textures.active.data
					else:
						uv_layer = None

					# Export data
					points = []
					normals = []
					uvs = []
					face_vert_indices = []		# List of face vert indices

					# Caches
					vert_vno_indices = {}		# Mapping of vert index to exported vert index for verts with vert normals
					vert_use_vno = set()		# Set of vert indices that use vert normals

					vert_index = 0				# Exported vert index
					for face in ffaces_mats[i]:
						fvi = []
						for j, vertex in enumerate(face.vertices):
							v = mesh.vertices[vertex]

							if face.use_smooth:
								if uv_layer:
									vert_data = (v.co[:], v.normal[:], uv_layer[face.index].uv[j][:])
								else:
									vert_data = (v.co[:], v.normal[:], tuple())

								if vert_data not in vert_use_vno:
									vert_use_vno.add(vert_data)

									points.append(vert_data[0])
									normals.append(vert_data[1])
									uvs.append(vert_data[2])

									vert_vno_indices[vert_data] = vert_index
									fvi.append(vert_index)

									vert_index += 1
								else:
									fvi.append(vert_vno_indices[vert_data])

							else:
								# all face-vert-co-no are unique, we cannot
								# cache them
								points.append(v.co[:])
								normals.append(face.normal[:])
								if uv_layer:
									uvs.append(uv_layer[face.index].uv[j][:])

								fvi.append(vert_index)

								vert_index += 1

						# For Lux, we need to triangulate quad faces
						face_vert_indices.append(tuple(fvi[0:3]))
						if len(fvi) == 4:
							face_vert_indices.append((fvi[0], fvi[2], fvi[3]))

					del vert_vno_indices
					del vert_use_vno

					# Define a new mesh
					lcObjName = ToValidLuxCoreName(mesh_name)
					self.lcScene.DefineMesh('Mesh-' + lcObjName, points, face_vert_indices, normals, uvs if uv_layer else None, None, None)				
					mesh_definitions.append((lcObjName, i))

				except Exception as err:
					LuxLog('Mesh export failed, skipping this mesh:\n%s' % err)

			del ffaces_mats
			bpy.data.meshes.remove(mesh)

			return mesh_definitions;

		except Exception as err:
			LuxLog('Object export failed, skipping this object:\n%s' % err)
			return []

	def ConvertObject(self, obj):
		########################################################################
		# Convert the object geometry
		########################################################################

		meshDefinitions = []
		meshDefinitions.extend(self.ConvertObjectGeometry(obj))

		for meshDefinition in meshDefinitions:
			objName = meshDefinition[0]
			objMatIndex = meshDefinition[1]
			
			####################################################################
			# Convert the material
			####################################################################
			
			try:
				objMat = obj.material_slots[objMatIndex].material
			except IndexError:
				objMat = None
				LuxLog('WARNING: material slot %d on object "%s" is unassigned!' % (objMatIndex + 1, obj.name))
			
			if objMat is not None:
				try:
					objMatName = objMat.luxrender_material.luxcore_export(self.blScene, self.scnProps, objMat, self.materialsCache, self.texturesCache)
				except Exception as err:
					LuxLog('Material export failed, skipping material: %s\n%s' % (objMat.name, err))
					import traceback
					traceback.print_exc()
					objMatName = 'LUXBLEND_LUXCORE_CLAY_MATERIAL'
			else:
				objMatName = 'LUXBLEND_LUXCORE_CLAY_MATERIAL'

			####################################################################
			# Create the mesh
			####################################################################
			
			self.scnProps.Set(pyluxcore.Property('scene.objects.' + objName + '.material', [objMatName]))
			self.scnProps.Set(pyluxcore.Property('scene.objects.' + objName + '.ply', ['Mesh-' + objName]))
		
	def Convert(self, imageWidth = None, imageHeight = None):
		########################################################################
		# Convert camera definition
		########################################################################

		self.scnProps.Set(self.blScene.camera.data.luxrender_camera.luxcore_output(self.blScene,
			imageWidth = imageWidth, imageHeight = imageHeight))

		########################################################################
		# Add a sky definition
		########################################################################

		self.scnProps.Set(pyluxcore.Property('scene.lights.skylight.type', ['sky']))
		self.scnProps.Set(pyluxcore.Property('scene.lights.skylight.gain', [1.0, 1.0, 1.0]))

		########################################################################
		# Add dummy material
		########################################################################

		self.scnProps.Set(pyluxcore.Property('scene.materials.LUXBLEND_LUXCORE_CLAY_MATERIAL.type', ['matte']))
		self.scnProps.Set(pyluxcore.Property('scene.materials.LUXBLEND_LUXCORE_CLAY_MATERIAL.kd', [0.7, 0.7, 0.7]))

		########################################################################
		# Convert all objects
		########################################################################

		LuxLog('Object conversion:')
		for obj in self.blScene.objects:
			LuxLog('  %s' % obj.name)
			self.ConvertObject(obj)

		self.lcScene.Parse(self.scnProps)

		########################################################################
		# Create the configuration
		########################################################################

		self.cfgProps.Set(pyluxcore.Property('renderengine.type', ['PATHCPU']))
		self.cfgProps.Set(pyluxcore.Property('accelerator.instances.enable', [False]))

		# Film
		if (not imageWidth is None) and (not imageHeight is None):
			filmWidth = imageWidth
			filmHeight = imageHeight
		else:
			filmWidth, filmHeight = self.blScene.camera.data.luxrender_camera.luxrender_film.resolution(self.blScene)

		self.cfgProps.Set(pyluxcore.Property('film.width', [filmWidth]))
		self.cfgProps.Set(pyluxcore.Property('film.height', [filmHeight]))

		# Image Pipeline
		self.cfgProps.Set(pyluxcore.Property('film.imagepipeline.0.type', ['TONEMAP_AUTOLINEAR']))
		self.cfgProps.Set(pyluxcore.Property('film.imagepipeline.1.type', ['GAMMA_CORRECTION']))
		self.cfgProps.Set(pyluxcore.Property('film.imagepipeline.1.value', [2.2]))

		# Pixel Filter
		self.cfgProps.Set(pyluxcore.Property('film.filter.type', ['MITCHELL_SS']))

		# Sampler
		self.cfgProps.Set(pyluxcore.Property('sampler.type', ['RANDOM']))

		self.lcConfig = pyluxcore.RenderConfig(self.cfgProps, self.lcScene)

		return self.lcConfig
