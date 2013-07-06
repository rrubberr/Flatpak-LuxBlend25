from _helpers import _AnyObject, _LiteralObject

class Node(_AnyObject):
	pass

class NodeSocket(_AnyObject):
	pass

class NodeTree(_AnyObject):
	pass

class Operator(_AnyObject):
	pass

class Menu(_AnyObject):
	draw_preset = None

class Panel(_AnyObject):
	@staticmethod
	def append(*a, **k):
		pass

class Armature(_AnyObject):
	pass

class Bone(_AnyObject):
	pass

class EditBone(_AnyObject):
	pass

class PoseBone(_AnyObject):
	pass

class Camera(_AnyObject):
	pass

class Curve(_AnyObject):
	pass

class Lamp(_AnyObject):
	pass

class Lattice(_AnyObject):
	pass

class UIList(_AnyObject):
	pass

class Mesh(_AnyObject):
	pass

class MetaBall(_AnyObject):
	pass

class Speaker(_AnyObject):
	pass

class Material(_AnyObject):
	pass

class Object(_AnyObject):
	pass

class ParticleSettings(_AnyObject):
	pass

class Scene(_AnyObject):
	pass

class Brush(_AnyObject):
	pass

class Texture(_AnyObject):
	pass

class World(_AnyObject):
	pass

class Header(_AnyObject):
	pass

class PropertyGroup(_AnyObject):
	pass

class RenderEngine(_AnyObject):
	pass

class AddonPreferences(_AnyObject):
	pass

class RigidBodyConstraint(_AnyObject):
	class bl_rna:
		properties = {
			'type': _LiteralObject(enum_items=[])
		}

INFO_MT_file_export = []
RENDER_PT_output = []

