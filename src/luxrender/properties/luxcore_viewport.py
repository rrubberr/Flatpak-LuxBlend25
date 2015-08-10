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

from ..extensions_framework import declarative_property_group
from .. import LuxRenderAddon


@LuxRenderAddon.addon_register_class
class luxcore_viewportsettings(declarative_property_group):
    """
    Storage class for LuxCore viewport render setttings.
    """

    ef_attach_to = ['Scene']

    controls = [
        ['use_reduced_resolution', 'duration_reduced_resolution'],
        'duration_total',
    ]

    visibility = {

    }

    alert = {}

    enabled = {
        'duration_reduced_resolution': {'use_reduced_resolution': True},
        'duration_full_resolution': {'use_full_resolution': True},
    }

    properties = [
        {
            'type': 'bool',
            'attr': 'use_reduced_resolution',
            'name': 'Reduced Resolution',
            'description': 'Use a reduced resolution during viewport updates for more fluid navigation',
            'default': True,
        },
        {
            'type': 'float',
            'attr': 'duration_reduced_resolution',
            'name': 'Duration (s)',
            'description': 'How long should the resolution stay reduced after a viewport update, in seconds',
            'default': 1.5,
            'min': 0.5,
            'soft_max': 20.0,
        },
        {
            'type': 'float',
            'attr': 'duration_total',
            'name': 'Total Duration (s)',
            'description': 'The viewport render stops after this amount of time',
            'default': 5.0,
            'min': 1.0,
            'soft_max': 120.0,
        },
    ]