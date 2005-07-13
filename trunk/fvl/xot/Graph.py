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

from __future__ import generators


def uniq():
    u=0
    while True:
        yield u
        u=u+1
    raise Exception, "Can't happen"

class magic(dict):
    def __init__(self, name, **args):
        super(magic, self).__init__()

        self.__dict__.setdefault('name', name)

        for k, v in args.items():
            setattr(self, k, v)

    #def __repr__(self):
    #    return object.__repr__(self)

    def strs(self):
        return [str(self)]

    def __getattr__(self, attr):
        return self._attrs[attr]

    def __setattr__(self, attr, val):
        if attr not in self._attrs:
            raise AttributeError, attr
        return super(magic, self).__setattr__(attr, val)

    def attrs(self):
        attrs = {}
        for attr in self._attrs:
            attrs[attr] = getattr(self, attr)
        return attrs

    def dup(self):
        new = self.__new__(self.__class__)
        new.__init__(self.name, **(self.attrs()))
        return new

class node(magic):

    def __str__(self):
        str = '%s' % self.name
        attrs = filter(lambda _: _ != 'name', self.__dict__)
        if attrs:
            str += ' [%s]' % ", ".join(['%s="%s"' % (i, getattr(self, i))
                                        for i in attrs ])
        str += ';'
        return str

    _attrs = { 'URL': None,
               'bottomlabel': '',
               'color': 'black',
               'comment': '',
               'distortion': 0.0,
               'fillcolor': 'lightgrey',
               'fixedsize': 'false',
               'fontcolor': 'black',
               'fontname': 'Times-Roman',
               'fontsize': 14.0,
               'group': '',
               'height': 0.5,
               'label': '\n',
               'layer': '',
               'orientation': 0.0,
               'peripheries': 0,
               'pin': None,
               'pos': None,
               'rects': None,
               'regular': 'false',
               'shape': 'ellipse',
               'shapefile': '',
               'showboxes': 0,
               'sides': 4,
               'skew': 0.0,
               'style': None,
               'toplabel': '',
               'vertices': None,
               'width': 0.75,
               'z': 0.0,
               }

class edge(magic):

    def __str__(self):
        str = '%s -> %s' % self.name
        attrs = filter(lambda _: _ != 'name', self.__dict__)
        if attrs:
            str += ' [%s]' % ", ".join(['%s=%s' % (i, `getattr(self, i)`)
                                        for i in attrs ])
        str += ';'
        return str


    _attrs = { 'URL': None,
               'arrowhead': 'normal',
               'arrowsize': 1.0,
               'arrowtail': 'normal',
               'color': 'black',
               'comment': '',
               'constraint': 'true',
               'decorate': 'false',
               'dir': None,
               'fontcolor': 'black',
               'fontname': 'Times-Roman',
               'fontsize': 14.0,
               'headURL': '',
               'headlabel': '',
               'headport': 'center',
               'label': '',
               'labelangle': -25.0,
               'labeldistance': 1.0,
               'labelfloat': 'false',
               'labelfontcolor': 'black',
               'labelfontname': 'Times-Roman',
               'labelfontsize': 11.0,
               'layer': '',
               'len': 1.0,
               'lhead': '',
               'lp': None,
               'ltail': '',
               'minlen': 1,
               'pos': None,
               'samehead': '',
               'sametail': '',
               'showboxes': 0,
               'style': None,
               'tailURL': '',
               'taillabel': '',
               'tailport': 'center',
               'w': 1.0,
               'weight': 1.0,
               }

class graph(magic):

    graph_type = "digraph"

    def __init__(self, name='graph', **args):
        self['nodes'] = {}
        self['graphs'] = {}
        self['edges'] = {}
        super(graph, self).__init__(name, **args)

    def strs(self):
        s=[ '%s %s {' % (self.graph_type, self.name) ]
        for things in self.keys():
            for thing in self[things].keys():
                for str in self[things][thing].strs():
                    s.append("    " + str)
        attrs = filter(lambda _: _ != 'name', self.__dict__)
        if attrs:
            s.append('    graph [%s]' % ", ".join(['%s="%s"' % (i, getattr(self, i))
                                                   for i in attrs ]))
        s.append("}")
        return s

    def __str__(self):
        return "\n".join(self.strs())

    def get_node(self, name):
        return self['nodes'][name]

    def get_nodes(self):
        return self['nodes']

    def add_node(self, name=None, **args):
        if name is None:
            name=uniq()

        new = node(name, **args)
        self['nodes'][name] = new
        return new

    def del_node(self, n):
        if isinstance(n, node):
            n = n.name
        del self['nodes'][n]

    def copy_node(self, a, b):
        if not isinstance(a, node):
            a = self.get_node(a)
        if isinstance(b, node):
            b = b.name
            self.del_node(b)
        self.add_node(a.name, **(a.attrs()))


    def rename_node(self, a, name):
        if not isinstance(a, node):
            a = self.get_node(a)
        del self['nodes'][a.name]
        a.name = name
        self['nodes'][name] = a


    def get_edge(self, (a,b)):
        return self['edges'][(a,b)]

    def get_edges(self):
        return self['edges']

    def add_edge(self, (a,b), **args):
        if isinstance(a, node):
            a = a.name
        if isinstance(b, node):
            b = b.name
        new = edge((a,b), **args)
        self['edges'][(a,b)] = new
        return new

    def del_edge(self, (a,b)):
        if isinstance(a, node):
            a = a.name
        if isinstance(b, node):
            b = b.name
        del self['edges'][(a,b)]

    def copy_edge(self, (a,b), (c,d)):
        if isinstance(a, node):
            a = a.name
        if isinstance(b, node):
            b = b.name
        if isinstance(c, node):
            c = c.name
        if isinstance(d, node):
            d = d.name
        attrs = self['edges'][(a,b)].attrs()
        self['edges'][(c,d)] = edge(**attrs)

    def move_edge(self, (a,b), (c,d)):
        self.copy_edge((a,b),(c,d))
        self.del_edge((a,b))

    def get_graph(self, name):
        return self['graphs'][name]

    def get_graphs(self):
        return self['graphs']

    def add_graph(self, name, **args):
        new=None
        if name.startswith('cluster'):
            new=cluster(name, **args)
        else:
            new=subgraph(name, **args)
        self['graphs'][name] = new
        return new

    def del_graph(self, a):
        if isinstance(a, graph):
            a = a.name
        del self['graphs'][a]

    def copy_graph(self, a, b):
        if isinstance(a, graph):
            a = a.name
        if isinstance(b, graph):
            b = b.name
        old = self['graphs'][a]
        new=self.add_graph(b, **(old.attrs()))
        for things in self.keys():
            for thing in old[things].keys():
                new[things][thing] = old[things][thing].dup()

    _attrs = { 'Damping': 0.99,
               'Epsilon': None,
               'URL': None,
               'bb': None,
               'bgcolor': None,
               'center': 'false',
               'clusterrank': 'local',
               'comment': '',
               'compound': 'false',
               'concentrate': 'false',
               'fontcolor': 'black',
               'fontname': 'Times-Roman',
               'fontpath': '',
               'fontsize': 14.0,
               'label': '',
               'labelloc': 'b',
               'layers': '',
               'lp': None,
               'margin': None,
               'maxiter': 'MAXINT',
               'mclimit': 1.0,
               'model': '',
               'nodesep': 0.25,
               'normalize': 'false',
               'nslimit1': None,
               'ordering': '',
               'orientation': '',
               'overlap': '',
               'page': None,
               'pagedir': 'BL',
               'quantum': 0.0,
               'rankdir': 'TB',
               'ranksep': 0.5,
               'ratio': None,
               'remincross': 'false',
               'rotate': 0,
               'samplepoints': 8,
               'searchsize': 30,
               'sep': 0.01,
               'showboxes': 0,
               'size': None,
               'splines': 'false',
               'start': '',
               'styleheet': None,
               'voro_margin': 0.05,
               }

class subgraph(graph):
    _attrs = graph._attrs
    _attrs.update({ 'rank': None,
                    })
    graph_type = "subgraph"


class cluster(subgraph):
    _attrs = subgraph._attrs
    _attrs.update({ 'URL': None,
                    'color': 'black',
                    'fillcolor': 'black',
                    'fontcolor': 'black',
                    'fontname': 'Times-Roman',
                    'fontsize': 14.0,
                    'label': '',
                    'labeljust': '',
                    'labelloc': 't',
                    'lp': None,
                    'style': None,
                    })
