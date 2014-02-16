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
from ..outputs import LuxLog
from ..outputs.luxcore_api import ToValidLuxCoreName

def ConvertBlenderObject(blScene, lcScene, obj):
	try:
		mesh_definitions = []

		if obj.hide_render:
			return mesh_definitions
		
		mesh = obj.to_mesh(blScene, True, 'RENDER')
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

				mesh_name = '%s-%s_m%03d' % (obj.data.name, blScene.name, i)

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
				lcScene.DefineMesh('Mesh-' + lcObjName, points, face_vert_indices, normals, uvs if uv_layer else None, None, None)				
				mesh_definitions.append((obj, lcObjName, i))
				
			except Exception as err:
				LuxLog('Mesh export failed, skipping this mesh:\n%s' % err)

		del ffaces_mats
		bpy.data.meshes.remove(mesh)
		
		return mesh_definitions;

	except Exception as err:
		LuxLog('Object export failed, skipping this object:\n%s' % err)
		return []

def ConvertBlenderScene(blScene):
	########################################################################
	# Create the scene
	########################################################################

	lcScene = pyluxcore.Scene()
	scnProps = pyluxcore.Properties()

	########################################################################
	# Convert camera definition
	########################################################################

	scnProps.Set(blScene.camera.data.luxrender_camera.luxcore_output(blScene));
	
	########################################################################
	# Add a sky definition
	########################################################################
	
	scnProps.Set(pyluxcore.Property('scene.lights.skylight.type', ['sky']))
	scnProps.Set(pyluxcore.Property('scene.lights.skylight.gain', [1.0, 1.0, 1.0]))
	
	########################################################################
	# Add dummy material
	########################################################################

	scnProps.Set(pyluxcore.Property('scene.materials.dummymat.type', ['matte']))
	scnProps.Set(pyluxcore.Property('scene.materials.dummymat.kd', [0.7, 0.7, 0.7]))

	########################################################################
	# Convert all objects
	########################################################################

	LuxLog('Object coneversion:')
	meshDefinitions = []
	for obj in blScene.objects:
		LuxLog('  %s' % obj.name)
		meshDefinitions.extend(ConvertBlenderObject(blScene, lcScene, obj))

	for meshDefinition in meshDefinitions:
		objName = meshDefinition[1]
		scnProps.Set(pyluxcore.Property('scene.objects.' + objName + '.material', ['dummymat']))
		scnProps.Set(pyluxcore.Property('scene.objects.' + objName + '.ply', ['Mesh-' + objName]))
		
	lcScene.Parse(scnProps)
	
	return lcScene
