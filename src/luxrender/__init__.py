# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
from os import getenv
from .extensions_framework import util as efutil
import sys

bl_info = {
    "name": "LuxRender",
    "author": "LuxRender Project: Doug Hammond (dougal2), Asbjørn Heid (LordCrc), Daniel Genrich (Genscher), "
    "Jens Verwiebe, Jason Clarke (JtheNinja), Michael Klemm (neo2068), Simon Wendsche (B.Y.O.B.)",
    "version": (1, 8, 'dev'),
    "blender": (2, 79, 1),
    "api": 57908,
    "category": "Render",
    "location": "Info header, render engine menu",
    "warning": "",
    "wiki_url": "http://www.luxrender.net/wiki/LuxBlend25_Manual",
    "tracker_url": "http://www.luxrender.net/mantis",
    "description": "LuxRender integration for Blender"
}

def find_luxrender_path():
    path = efutil.find_config_value('luxrender', 'defaults', 'install_path', '')

    if not path:
        path = getenv('LUXRENDER_ROOT', '')

    return path

def import_bindings_module(name):
    """Import Lux Python bindings module (e.g. pylux)."""
    import os.path
    import sys
    import importlib
    from .outputs import LuxLog

    def _import_bindings_module(path, name, relative=False):
        if relative:
            package = os.path.split(path)[1]
            module = importlib.import_module('.' + name, package=package)
        else:
            sys.path.insert(0, path)
            try:
                module = importlib.import_module(name)
            except ImportError:
                raise
            finally:
                del sys.path[0]
        return module

    lux_path = find_luxrender_path()
    luxblend_path = os.path.dirname(os.path.abspath(__file__))
    if sys.platform == 'darwin':
        return _import_bindings_module(luxblend_path, name, True)
    else:
        try:
            module = _import_bindings_module(lux_path, name)
        except ImportError as error:
            module = _import_bindings_module(luxblend_path, name, True)
        return module

if 'core' in locals():
    import importlib

    importlib.reload(core)
else:
    import bpy
    from bpy.types import AddonPreferences
    from bpy.props import StringProperty
    from .extensions_framework import Addon
    import nodeitems_utils

    def set_luxrender_path(self, path):
        """Save Lux install path to persistent disk storage."""
        if not path:
            return
        efutil.write_config_value('luxrender', 'defaults', 'install_path',
                                  efutil.filesystem_path(path))

    def get_luxrender_path(self):
        """Load Lux install path from persistent disk storage."""
        return efutil.find_config_value('luxrender', 'defaults',
                                        'install_path', '')

    class LuxRenderAddonPreferences(AddonPreferences):
        # this must match the addon name
        bl_idname = __name__

        install_path = StringProperty(
            name="Path to LuxRender Installation",
            description='Path to LuxRender install directory',
            subtype='DIR_PATH',
            default=find_luxrender_path(),
            get=get_luxrender_path,
            set=set_luxrender_path
        )

        def draw(self, context):
            layout = self.layout

            split = layout.split(percentage=0.78)
            split.template_reports_banner()
            split.label(text="After editing these settings please restart Blender for the changes to take effect.",
                        icon='INFO')
            split.operator("luxrender.update_luxblend", icon='RECOVER_AUTO')

            split = layout.split(percentage=0.78)
            split.template_reports_banner()
            split.label(text="Updating LuxBlend only updates the addon, not the LuxRender binaries. Use this instead:")
            split.operator("luxrender.open_daily_builds_webpage", icon='URL')

            layout.prop(self, "install_path")

    LuxRenderAddon = Addon(bl_info)
    addon_register, addon_unregister = LuxRenderAddon.init_functions()

    def register():
        bpy.utils.register_class(LuxRenderAddonPreferences)
        nodeitems_utils.register_node_categories("LUX_SHADER", ui.node_editor.luxrender_node_categories_material)
        nodeitems_utils.register_node_categories("LUX_VOLUME", ui.node_editor.luxrender_node_categories_volume)
        addon_register()

    def unregister():
        bpy.utils.unregister_class(LuxRenderAddonPreferences)
        nodeitems_utils.unregister_node_categories("LUX_SHADER")
        nodeitems_utils.unregister_node_categories("LUX_VOLUME")
        addon_unregister()


    # Importing the core package causes extensions_framework managed
    # RNA class registration via @LuxRenderAddon.addon_register_class
    from . import core
