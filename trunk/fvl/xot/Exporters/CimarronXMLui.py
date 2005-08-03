# -*- coding: ISO-8859-1 -*-
# Copyright 2005 Fundación Vía Libre
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

import libxml2
import re
import os

"""
Options are:

class: The main class for the window.
title: The title for the window. default: same value than class.
find:
search.<thing>:
"""

def makeFieldName (name):
    def __upper__ (letter):
        return letter.group (1).upper ()
    # some_thing
    name= re.sub (r'_([a-z])', __upper__, name)
    # someThing
    return name

def MakeFieldName (name):
    name= makeFieldName (name)
    # someThing
    name= name[0:1].upper ()+name[1:]
    # SomeThing
    return name

def getProp (xmlObj, name, default=None):
    value= xmlObj.prop (name)
    if value is None:
        value= default
    return value

class exporter(object):
    def export(self, xot, **opts):
        """return the xml document to create the screen represented by the xot"""
        self.xot= xot

        xmlFileName= opts['xin']
        if os.path.isfile(xmlFileName):
            xmlObj= libxml2.parseFile(xmlFileName).getRootElement ()
        else:
            raise OSError, "Unable to open file: %r" % xmlFileName
        
        if xmlObj.name!='class':
            raise ValueError, "root element shoud be 'class', not %s" % xmlObj.name
        
        kind_name= xmlObj.prop ('name')
        KindName= MakeFieldName (kind_name)
        kind = self.xot.tables[kind_name]
        kind.searchers= {}
        title= getProp (xmlObj, 'title', kind_name)

        imports= []
        finders= []
        self.others= others= [xmlObj]
        
        child= xmlObj.children
        while child is not None:
            if child.name=='import':
                imports.append ((lambda s: ('.'.join(s[:-1]), s[-1]))
                                (child.prop ('what').split ('.')))
        
            elif child.name=='finder':
                finders.append (child.prop ('attribute'))

            elif child.name=='class':
                # check for `class has that attr`?
                others.append (child)

            child= child.next

        xml= libxml2.newDoc("1.0")

        # window
        crud= xml.newDocNode (None, 'CrUDController', None)
        crud.setProp ('title', title)
        crud.setProp ('cls', KindName)
        crud.setProp ('id', 'Crud')
        xml.setRootElement (crud)

        # imports
        if imports:
            for k, v in imports:
                imp= crud.newChild (None, 'import', None)
                imp.setProp ('from', k)
                imp.setProp ('what', v)
                imp.setProp ('id', v)

        search= crud.newChild (None, 'SearchEntry', None)
        search.setProp ('onAction', 'Crud.changeModel')
        search.setProp ('cls', KindName)
        for i in finders:
            column= search.newChild (None, 'Column', None)
            column.setProp ('name', MakeFieldName(i))
            column.setProp('attribute', makeFieldName(i))

        # tabs
        for other in others:
            self.makeTab (other, crud)
            
        return xml.serialize (encoding="utf-8", format=1)

    def makeTab (self, xmlObj, crud):
        kind_name= xmlObj.prop ('name')
        KindName= MakeFieldName (kind_name)
        kind = self.xot.tables[kind_name]

        # process the xmlObj first
        kind.ignore = []
        child= xmlObj.children
        while child is not None:
            if child.name=='attribute':
                kind.searchers[child.prop ('name')]= []
                column= child.children
                while column:
                    if column.name=='finder':
                        kind.searchers[child.prop ('name')].append \
                                                  (column.prop ('attribute'))

                    column= column.next

            elif child.name=='ignore':
                kind.ignore.append(child.prop('attribute'))
                
            child= child.next
        
        editor= crud.newChild (None, 'Editor', None)
        editor.setProp ('label', "Edit")
        editor.setProp ('id', KindName+"Editor")

        attr= xmlObj.prop ('attribute')
        if attr is not None:
            # this kind must be a relative of the main kind
            editor.setProp ('attribute', attr)
            editor.setProp ('label', KindName)
            # the fields will be Columns
            editor= editor.newChild (None, 'Grid', None)
            editor.setProp ('cls', KindName)

        for field_name in kind.fields:
            if field_name=='id' or field_name in kind.ignore:
                continue
            # fuck the way to do these things
            # this module is too literal
            label= libxml2.newNode ('Label')
            label.setProp ('text', MakeFieldName (field_name))
            
            try:
                search_field_name= kind.fields[field_name].reference.name
            except AttributeError:
                # normal field
                if kind.fields[field_name].type=="boolean":
                    entry= libxml2.newNode ('Checkbox')
                elif editor.name=='Grid':
                    # this kind is edited through a Grid
                    # the fields must be Columns
                    entry= libxml2.newNode ('Column')
                    fieldName= makeFieldName (field_name)
                    FieldName= MakeFieldName (field_name)
                    entry.setProp('name', FieldName)
                    entry.setProp('attribute', fieldName)
                    label = None
                else:
                    entry = libxml2.newNode('Entry')
            else:
                # reference; put a search entry
                if search_field_name in [ other.prop('name') for other in self.others ]:
                    # skip those fields treated elsewhere
                    continue

                # warning: this part does not work
                SearchFieldName= MakeFieldName (search_field_name)
                entry= libxml2.newNode ('SearchEntry')
                for i in kind.searchers[search_field_name]:
                    column= entry.newChild (None, 'Column', None)
                    column.setProp ('name', i)
                    column.setProp ('read', SearchFieldName+'.get'+MakeFieldName (i))
                
            entry.setProp ('attribute', makeFieldName (field_name))
    
            if label is not None:
                editor.addChild (label)
            editor.addChild (entry)
