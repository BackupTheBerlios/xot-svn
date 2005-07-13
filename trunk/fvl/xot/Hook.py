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

"""Xot, a database description framework -- 'Hook' definitions"""

__author__ = "John Lenton <john@vialibre.org.ar>"
__version__ = "$Revision: 1.4 $"
__date__ = "$Date: 2004/01/21 17:18:47 $"
__copyright__ = "Copyright (c) 2003 Fundación Vía Libre"
__license__ = "GPL"

def new(xot, name, target, node=None):
    "Return a Hook object"
    return Hook(xot, name, target, node)

class Hook(object):
    """
    a Hook object is the description of a certain family of
    transformations to be applied to the database description at
    certain points in processing, to represent certain characteristics
    of tables.

    For example, if all the tables in a database have reference a
    certain table the visualization of those links would clutter up
    the database graph needlessly, so you could define a hook whose
    xml implementation added (or removed) the links to the table in
    question, and then selectivly apply the transformation depending
    on whether you want to see those links in your output or not.
    """

    def __init__(self, xot, name, target, node=None):
        """
        Set up the basic properties of the thingie. If the optional node
        argument is present, call from_node.
        """
        self.xot = xot
        self.name = name
        self.target = target
        if node:
            self.from_node(node)

    def from_node(self, node):
        """
        Set up the rest of the properties of the thingie from the
        information contained in the libxml2 node
        """
        self.lang = node.prop('lang')
        self.impl = node.content
        self.sub = UserFunction(self.impl,
                                "%s hook, %s target, %s" % (self.name,
                                                            self.target,
                                                            self.xot.filename))

class UserFunction(object):
    __safe_for_unpickling__ = True
    def __init__(self, prog, caller):
        self.prog = prog
        self.caller = caller
    def declare(self):
        self.code = compile(self.prog.rstrip()+"\n", self.caller, 'exec')
        def hook(g, l):
            l['RV']=None
            exec self.code in g, l
            return l['RV']
        self.func = hook
    def __call__(self, *args, **argvs):
        if not hasattr(self, 'func'):
            self.declare()
        return self.func(*args, **argvs)
    def __reduce__(self):
        if hasattr(self, 'func'):
            del self.func
        if hasattr(self, 'code'):
            del self.code
        return (UserFunction, (self.prog,self.caller))
