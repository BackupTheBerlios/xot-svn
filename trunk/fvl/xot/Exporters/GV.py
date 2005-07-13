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

"""
Export to GraphViz's dot format

Accepts the following options:

option        default      description
============================================================================
fields        false      create nodes for fields
compact       false      show fields compactly
clustertable  false      group nodes of a table into clusters
clustergroup  false      group nodes of a table group into clusters

"""
import Graph

def _ggn(group):
    """ group graph name """
    return 'cluster_G_' + group.name

def _tgn(table):
    """ table graph name """
    return 'cluster_' + table.name

def _tnn(table):
    """ table node name """
    return table.name

def _fnn(table, field):
    """ field node name """
    return "%s_%s" % (table.name, field.name)

def _fpl(table, field):
    """ field port link """
    return "%s:%s" % (table.name, field.name)

def _tpl(table):
    """ table port link """
    return "%s:__TABLE__" % table.name

class exporter(object):
    def export(self, xot, fields=False, clustertable=False, clustergroup=False, compact=False):
        """generate a dot from a xot"""
        g=Graph.graph("xot")
        g.overlap='scale'
        for group in xot.table_groups.values():
            gsg = None
            if clustergroup:
                gsg = g.add_graph(_ggn(group))
                gsg.label = group.name
            else:
                gsg = g
            for table in group.tables.values():
                sg = None
                if clustertable:
                    sg = gsg.add_graph(_tgn(table))
                    sg.label = table.name
                else:
                    sg = gsg
                t = sg.add_node(_tnn(table))
                t.shape = 'box'
                if compact:
                    t.shape = 'record'
                    t.label = ["{<__TABLE__>%s|{" % table.name]
                for f in table.fields.values():
                    if compact:
                        t.label.append("<%s>%s" % (f.name, f.name))
                        if hasattr(f, 'reference'):
                            g.add_edge((_fpl(table, f), _tpl(f.reference)))
                    else:
                        if fields:
                            n = sg.add_node(_fnn(table, f))
                            n.label = f.name
                            sg.add_edge((_tnn(table), _fnn(table, f)))
                        if hasattr(f, 'reference'):
                            if fields:
                                g.add_edge((_fnn(table, f), _tnn(f.reference)))
                                n.shape = 'diamond'
                                n.fillcolor = 'gray'
                                n.style = 'filled'
                            else:
                                g.add_edge((_tnn(table), _tnn(f.reference)))
                if compact:
                    t.label = t.label[0] + "|".join(t.label[1:]) + "}}"

        if clustergroup:
            for sg in g.get_graphs().values():
                if len(sg['graphs']) == 1:
                    a = sg['graphs'].values()[0]
                    sg.del_graph(a)
                    sg = a
        return str(g)

