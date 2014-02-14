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

def ConvertBlenderScene(blScene):
	########################################################################
	# Create the scene
	########################################################################

	scene = pyluxcore.Scene()
	scnProps = pyluxcore.Properties()

	########################################################################
	# Add camera definition
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

	scnProps.Set(pyluxcore.Property("scene.materials.dummymat.type", ["matte"]))
	scnProps.Set(pyluxcore.Property("scene.materials.dummymat.kd", [0.7, 0.7, 0.7]))

	########################################################################
	# Add all objects
	########################################################################

	rendertypes = ["MESH", "SURFACE", "META", "TEXT", "CURVE"]
	for obj in blScene.objects:
		objName = ToValidLuxCoreName(obj.name)
		if not obj.hide_render and obj.type in rendertypes:
			try:
				if type(obj) == bpy.types.Object:
					LuxLog("Object: {}".format(objName))
					mesh = obj.to_mesh(blScene, True, "RENDER")
				else:
					LuxLog("Mesh: {}".format(objName))
					mesh = obj
					mesh.update(calc_tessface = True)
			except:
				LuxLog("Pass")
				pass

			mesh.transform(obj.matrix_world)
			mesh.update(calc_tessface = True)

			verts = [v.co[:] for v in mesh.vertices]

			# Split all polygons in triangles
			tris = []
			for poly in mesh.polygons:
				for loopIndex in range(poly.loop_start + 1, poly.loop_start + poly.loop_total - 1):
					tris.append((mesh.loops[poly.loop_start].vertex_index,
						mesh.loops[loopIndex].vertex_index,
						mesh.loops[loopIndex + 1].vertex_index))
			
			# Define a new object
			scene.DefineMesh("Mesh-" + objName, verts, tris, None, None, None, None)
			scnProps.Set(pyluxcore.Property("scene.objects." + objName + ".material", ["dummymat"]))
			scnProps.Set(pyluxcore.Property("scene.objects." + objName + ".ply", ["Mesh-" + objName]))
	
	scene.Parse(scnProps)
	
	return scene
