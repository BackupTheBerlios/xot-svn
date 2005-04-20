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
    if (node and node.prop('references')):
        return Reference(table, name, node)
    else:
        return Field(table, name, node)

class Field(object):
    def __init__(self, table, name, node=None):
        self.table = table
        self.name = name
        if node:
            self.from_node(node)

    def from_node(self, node):
        null = node.prop('null')
        auto = node.prop('auto_increment')
        classProp= node.prop ('is_class_property')

        self.type = node.prop('type')
        self.externalType= node.prop('external_type')
        self.default= node.prop('default')

        self.auto_increment = auto and auto.lower() == 'true'

        self.displayLabel= node.prop('display_label')
        self.null = not(null and null.lower() == 'false')
        self.classProp= classProp and classProp.lower() == 'true'
        docs= node.xpathEval ('doc')
        self.doc= '\n'.join ([doc.getContent() for doc in docs])

class Reference(Field):
    def from_node(self, node):
        null = node.prop('null')
        classProp= node.prop ('is_class_property')

        self.symbolic = node.prop('references')
        self.default = node.prop('default')
        self.inverse= node.prop ('inverse')
        self.deleteRule= node.prop ('delete_rule')
        self.joinSemantic= node.prop ('join_semantic')

        # yeap, is just like the one above
        self.displayLabel= node.prop('display_label')
        self.null = not(null and null.lower() == 'false')
        self.classProp= classProp and classProp.lower() == 'true'
        docs= node.xpathEval ('doc')
        self.doc= '\n'.join ([doc.getContent() for doc in docs])

    def get_reference(self):
        tg = self.table.group.xot.table_groups[self.symbolic]
        if len(tg.tables)>1:
            ref_hooks = tg.get_ref_hooks()
            assert ref_hooks, \
                   "More than one member found in a referred table group %s: please set a ref hook" % self.symbolic
            ref = None
            for ref_hook in ref_hooks:
                ref = ref_hook.sub(globals(), locals())
                if ref:
                    break
            assert ref, "ref hooks failed to find a reference"
            return ref
        else:
            return tg.tables.values()[0]
        raise "Can't happen"

    def get_type(self):
        pkey = self.reference.primary_keys
        if len(pkey)>1:
            pkey_hooks = self.table.get_pkey_hooks()
            assert pkey_hooks, \
                   "More than one primary key found in a referred table group: please set a pkey hook"
            pk=None
            for pkey_hook in pkey_hooks:
                pk = pkey_hook.sub(globals(), locals())
                if pk:
                    break
            assert pk, "key hooks failed to find a primary key"
            pkey=pk
        else:
            pkey = pkey[0]
        return pkey.type
    reference = property(get_reference)
    type = property(get_type)
    auto_increment = property(lambda self:None)
