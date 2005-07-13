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

def new(table, name, node=None):
    return Index(table, name, node)

class Index(object):
    def __init__(self, table, name, node=None):
        self.table = table
        self.name = name
        self.fields = []
        if node:
            self.from_node(node)

    def from_node(self, node):
        self.type = node.prop('type')
        self.method = node.prop('method')
        self.where = node.prop('where')
        self.function = node.prop('function')
        for field in node.xpathEval('index_field'):
            self.fields.append(self.table.fields[field.prop('name')])
        if self.type == 'primary_key':
            self.table.primary_keys = self.fields
