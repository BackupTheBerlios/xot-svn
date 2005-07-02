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
        
        # title = opts.get('title', kind_name)
        kind_name= xmlObj.prop ('name')
        KindName= MakeFieldName (kind_name)
        kind = self.xot.tables[kind_name]
        title= getProp (xmlObj, 'title', kind_name)

        imports= []
        finders= []
        self.others= others= [xmlObj]
        
        child= xmlObj.children
        while child is not None:
            # man, do I miss haskell :)
            # don't be scared
            # converts 'model.country.State+model.country.Country'
            # to [('model.country', 'State'), ('model.country', 'Country')]
            # imports = [ ('.'.join(s[:-1]), s[-1])
            #             for s in [i.split('.')
            #                       for i in opts.get('import', '').split('+') ]]
            if child.name=='import':
                imports.append ((lambda s: ('.'.join(s[:-1]), s[-1])) (child.prop ('what').split ('.')))
        
            # finders= opts.get('find', 'name').split ('+')
            elif child.name=='finder':
                finders.append (child.prop ('attribute'))

            elif child.name=='class':
                # check for `class has that attr`?
                others.append (child)

            child= child.next

        # tabs_tables = [kind] + [i for i in kind.details]
        xml= libxml2.newDoc("1.0")

        # window
        crud= xml.newDocNode (None, 'CrUDController', None)
        crud.setProp ('title', title)
        crud.setProp ('klass', KindName)
        crud.setProp ('id', 'Crud')
        xml.setRootElement (crud)

        # imports
        if imports:
            for k, v in imports:
                imp= crud.newChild (None, 'import', None)
                imp.setProp ('from', k)
                imp.setProp ('what', v)
                imp.setProp ('id', v)

        search= crud.newChild (None, 'Search', None)
        search.setProp ('onAction', 'Crud.changeModel')
        search.setProp ('searcher', KindName)
        for i in finders:
            column= search.newChild (None, 'Column', None)
            column.setProp ('name', i)
            column.setProp ('read', KindName+'.get'+MakeFieldName (i))

        # tabs
        for other in others:
            self.makeTab (other, crud)
            
        return xml.serialize (encoding="utf-8", format=1)

    def makeTab (self, xmlObj, crud):
        # kind_name = opts['class']
        kind_name= xmlObj.prop ('name')
        KindName= MakeFieldName (kind_name)
        kind = self.xot.tables[kind_name]

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
            editor.setProp ('klass', KindName)

        for field_name in kind.fields:
            if field_name=='id':
                continue
            # label= editor.newChild (None, 'Label', None)
            # fuck the way to do these things
            # this module is too literal
            label= libxml2.newNode ('Label')
            label.setProp ('text', MakeFieldName (field_name))
            
            try:
                # reference; put a search entry
                search_field_name= kind.fields[field_name].reference.name
                if search_field_name in [ other.prop ('name') for other in self.others ]:
                    # skip those fields treated elsewhere
                    continue

                # warning: this part does not work
                SearchFieldName= MakeFieldName (search_field_name)
                entry= libxml2.newNode ('SearchEntry')
                for i in opts.get('search.'+search_field_name, 'name').split ('+'):
                    column= entry.newChild (None, 'Column', None)
                    column.setProp ('name', i)
                    column.setProp ('read', SearchFieldName+'.get'+MakeFieldName (i))
            except AttributeError:
                # normal field
                if kind.fields[field_name].type=="boolean":
                    entry= libxml2.newNode ('Checkbox')
                elif editor.name=='Grid':
                    # this king is edited through a Grid
                    # the fields must be Columns
                    entry= libxml2.newNode ('Column')
                    FieldName= MakeFieldName (field_name)
                    entry.setProp ('name', FieldName)
                    # these will be gone when Columns learn how to handle attrs
                    entry.setProp ('read', KindName+'.get'+FieldName)
                    entry.setProp ('write', KindName+'.set'+FieldName)
                    label= None
                else:
                    entry= libxml2.newNode ('Entry')
            entry.setProp ('attribute', makeFieldName (field_name))
    
            if label is not None:
                editor.addChild (label)
            editor.addChild (entry)
