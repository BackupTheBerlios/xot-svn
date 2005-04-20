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

"""Xot, a database description framework --- main file"""

__author__ = "John Lenton <john@vialibre.org.ar>"
__version__ = "$Revision: 1.5 $"
__date__ = "$Date: 2004/01/21 17:18:47 $"
__copyright__ = "Copyright (c) 2003 Fundación Vía Libre"
__license__ = "GPL"


import libxml2

import Hook, Group
import sys

def new(filename, *hooks):
    "Return a Xot."
    return Xot(filename, *hooks)

class Xot(object):
    """
    a Xot is a complete description of a database. It can be used to
    produce sql output, for example.
    """


    def __init__(self, filename, *hooks):
        """
        Given a filename and a list of hooks, parse the file (using
        libxml2) and generates the associated Xot structure.
        """

        apply_all_hooks = False

        if len(hooks) == 1 and hooks[0] == ':all:':
            apply_all_hooks = True

        self.hooks = {'xml': {},
                      'sql': {},
                      'dot': {},
                      'xot': {},
                      'ref': {},
                      'key': {},
                      }

        self.filename = filename
        self.table_groups = {}
        ctxt = libxml2.createFileParserCtxt(filename)
        ctxt.pedantic(True)
        #ctxt.validate(True)
        ctxt.parseDocument()
        if not ctxt.isValid():
            sys.exit(1)
        doc = ctxt.doc()

        # read in the hooks
        for hook_def in doc.xpathEval('/database/hook_defs/hook_def'):
            name = hook_def.prop('name')
            for hook_impl in hook_def.xpathEval('hook_impl'):
                target = hook_impl.prop('target')
                assert target in self.hooks
                hook = Hook.new(self, name, target, hook_impl)
                self.hooks[target].setdefault(name, []).append(hook)

        # the xot now has to restructure the xml slightly: all tables
        # must go in table groups, so that transformations brought on
        # by xml hooks that split individual tables into several (to
        # implement missing features in the db engine, for example)
        # don't wreak havoc with (symbolic) references other tables
        # might have

        tables = doc.xpathEval('/database/tables')[0]
        for table in tables.xpathEval('table'):
            name = table.prop('name')
            parent = table.prop('inherits')
            tg = libxml2.newNode('table_group')
            tg.setProp('name', name)
            if parent:
                tg.setProp('inherits', parent)
            table.replaceNode(tg)
            tg.addChild(table)
            h = table.xpathEval('hooks')
            if (h):
                table.addNextSibling(h[0])

        # done; now do the xml hooks requested (i.e. listed as
        # arguments to the constructor)

        g=globals()
        l=locals()
        for tg in tables.xpathEval('table_group'):
            l['self'] = tg
            for hook in tg.xpathEval('hooks/hook'):
                name = hook.prop('name')
                if self.hooks['xml'].has_key(name) and \
                       (apply_all_hooks or name in hooks):
                    for i in self.hooks['xml'][name]:
                        try:
                            i.sub(g, l)
                        except Exception, err:
                            print "while hooking table-group %s:" % tg.prop('name')
                            raise


        # xml transformations done; load the tree into objects

        for tg in tables.xpathEval('table_group'):
            name = tg.prop('name')
            self.table_groups[name] = Group.new(self, name, tg)

    def get_tables(self):
        """
        Return all the tables in the database (without having to go
        through the groups).
        """

        tables = {}
        for table_group in self.table_groups.values():
            tables.update(table_group.tables)
        return tables

    tables = property(get_tables)

    def export(self, **args):
        return self.exporter.export(self, **args)

    def get_hook(self, name):
        return dict([(i, self.hooks[i].setdefault(name, None)) for i in self.hooks])
