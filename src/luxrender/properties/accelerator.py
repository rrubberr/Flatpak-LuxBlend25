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
from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O

from .. import LuxRenderAddon
from ..export import ParamSet


@LuxRenderAddon.addon_register_class
class luxrender_accelerator(declarative_property_group):
    """
    Storage class for LuxRender Accelerator settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        'spacer',
        'accelerator',

        'costsamples',
        'intersectcost',
        'traversalcost',
        'emptybonus',
        'maxprims',
        'maxdepth',
        'maxprimsperleaf',
        'fullsweepthreshold',
        'skipfactor',
        'spacer',  # add an extra one for halt settings, which does not have its own advanced option
    ]

    visibility = {
        'spacer': {'advanced': True},
        'accelerator': {'advanced': True},
        'costsamples': {'advanced': True, 'accelerator': 'bvh'},
        'intersectcost': {'advanced': True, 'accelerator': O(['tabreckdtree', 'bvh'])},
        'traversalcost': {'advanced': True, 'accelerator': O(['tabreckdtree', 'bvh'])},
        'emptybonus': {'advanced': True, 'accelerator': O(['tabreckdtree', 'bvh'])},
        'maxprims': {'advanced': True, 'accelerator': 'tabreckdtree'},
        'maxdepth': {'advanced': True, 'accelerator': 'tabreckdtree'},
        'maxprimsperleaf': {'advanced': True, 'accelerator': 'qbvh'},
        'fullsweepthreshold': {'advanced': True, 'accelerator': 'qbvh'},
        'skipfactor': {'advanced': True, 'accelerator': 'qbvh'},
    }

    properties = [
        {
            'type': 'text',
            'attr': 'spacer',
            'name': '',  # This param just draws some blank space in the panel
        },
        {
            'type': 'enum',
            'attr': 'accelerator',
            'name': 'Accelerator',
            'description': 'Scene accelerator type',
            'default': 'qbvh',
            'items': [  # As of 1.9, other accelerator types have been removed from the core entirely
                        ('tabreckdtree', 'KD Tree', 'A traditional KD Tree'),
                        ('qbvh', 'QBVH', 'Quad bounding volume hierarchy'),
                        ('bvh', 'BVH', 'Experimental 8-wide SIMD BVH accelerator with node collapsing'),
                        ('none', 'None', 'Simply brute-force the scene. This is not recommended in actual production use.'),
            ],
            'save_in_preset': True
        },
        {
            'attr': 'advanced',
            'type': 'bool',
            'name': 'Advanced',
            'description': 'Configure advanced accelerator options',
            'default': False,
            'save_in_preset': True
        },
        {
            'attr': 'costsamples',
            'type': 'int',
            'name': 'Cost Samples',
            'default': 8,
            'save_in_preset': True
        },
        {
            'attr': 'intersectcost',
            'type': 'int',
            'name': 'Intersect Cost',
            'default': 80,
            'save_in_preset': True
        },
        {
            'attr': 'traversalcost',
            'type': 'int',
            'name': 'Traversal Cost',
            'default': 1,
            'save_in_preset': True
        },
        {
            'attr': 'emptybonus',
            'type': 'float',
            'name': 'Empty Bonus',
            'default': 0.0,
            'save_in_preset': True
        },
        {
            'attr': 'maxprims',
            'type': 'int',
            'name': 'Max. Prims',
            'default': 1,
            'save_in_preset': True
        },
        {
            'attr': 'maxdepth',
            'type': 'int',
            'name': 'Max. depth',
            'default': -1,
            'save_in_preset': True
        },
        {
            'attr': 'maxprimsperleaf',
            'type': 'int',
            'name': 'Max. prims per leaf',
            'default': 8,
            'save_in_preset': True
        },
        {
            'attr': 'fullsweepthreshold',
            'type': 'int',
            'name': 'Full sweep threshold',
            'default': 16,
            'save_in_preset': True
        },
        {
            'attr': 'skipfactor',
            'type': 'int',
            'name': 'Skip factor',
            'default': 1,
            'save_in_preset': True
        },
    ]

    def api_output(self):
        """
        Format this class's members into a LuxRender ParamSet

        Returns tuple
        """

        params = ParamSet()

        if self.advanced:
         
            if self.accelerator == 'tabreckdtree':
                params.add_integer('intersectcost', self.intersectcost)
                params.add_integer('traversalcost', self.traversalcost)
                params.add_float('emptybonus', self.emptybonus)
                params.add_integer('maxprims', self.maxprims)
                params.add_integer('maxdepth', self.maxdepth)

            if self.accelerator == 'qbvh':
                params.add_integer('maxprimsperleaf', self.maxprimsperleaf)
                params.add_integer('fullsweepthreshold', self.fullsweepthreshold)
                params.add_integer('skipfactor', self.skipfactor)
            
            if self.accelerator == 'bvh':
                params.add_integer('intersectcost', self.intersectcost)
                params.add_integer('traversalcost', self.traversalcost)
                params.add_float('emptybonus', self.emptybonus)
                params.add_integer('costsamples', self.costsamples)

        return self.accelerator, params
