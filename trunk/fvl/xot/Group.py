# -*- coding: ISO-8859-1 -*-
# Copyright 2003, 2004 Fundación Vía Libre
#
# This file is part of Xot.
#
# Xot is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Xot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Xot; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import Table

def new(xot, name, node=None):
    return group(xot, name, node)

class group(object):
    def __init__(self, xot, name, node=None):
        self.xot = xot
        self.name = name
        self.tables = {}
        self.hooks = []
        if node:
            self.from_node(node)

    def root(self):
        if not hasattr(self, '__root'):
            parent = self
            while parent.parent:
                parent = parent.xot.table_groups[parent.parent]
            self.__root = parent
        return self.__root


    def from_node(self, node):
        self.parent = node.prop('inherits')
        for hook in node.xpathEval('hooks/hook'):
            name = hook.prop('name')
            assert name
            self.hooks.append(name)
        for table in node.xpathEval('table'):
            name = table.prop('name')
            self.tables[name] = Table.new(self, name, table)

    def get_ref_hooks(self):
        ref_hooks = []
        for rh in self.xot.hooks['ref']:
            if rh in self.hooks:
                ref_hooks.extend(self.xot.hooks['ref'][rh])
        return ref_hooks

    def get_pkey_hooks(self):
        pkey_hooks = []
        for kh in self.xot.hooks['key']:
            if kh in self.hooks:
                pkey_hooks.extend(self.xot.hooks['key'][kh])
        return pkey_hooks
