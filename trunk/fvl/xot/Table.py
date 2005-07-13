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

import Field
import Index

def new(table_group, name, node=None):
    return Table(table_group, name, node)

class Table(object):
    def __init__(self, table_group, name, node=None):
        self.group = table_group
        self.name = name
        self.fields = {}
        self.constraints = {}
        self.indexes = {}
        if node:
            self.from_node(node)

    def from_node(self, node):
        uniq=0

        for field in node.xpathEval('fields/field'):
            name = field.prop('name')
            assert name
            self.fields[name] = Field.new(self, name, field)
        for constraint in node.xpathEval('constraints/constraint'):
            raise NotImplementedError('you used a constraint! please implement them...')
        for index in node.xpathEval('indexes/index'):
            name = index.prop('name')
            if not name:
                uniq += 1
                name = 'index_%04x' % uniq
            self.indexes[name] = Index.new(self, name, index)

        # the default for these are handled by Modeling itself
        self.className= node.prop ('class_name')
        self.moduleName= node.prop ('module_name')
        self.externalName= node.prop ('external_name')

        # of no use (yet)
        isAbstract= node.prop ('is_abstract')
        self.isAbstract= isAbstract and isAbstract.lower()=='true'
        ro= node.prop ('is_read_only')
        self.isReadOnly= ro and ro.lower()=='true'

        # self.doc= node.xpathEval ('doc').something ()

    def get_references(self):
        refs = []
        for ref in self.fields:
            if getattr(self.fields[ref], 'reference', None):
                refs.append(self.fields[ref])
        return refs

    references = property(get_references)

