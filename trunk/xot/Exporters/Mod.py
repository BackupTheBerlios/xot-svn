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

from __future__ import nested_scopes
import re

from Plural import pluralize

class IdError (Exception):
    pass

class exporter (object):
    __doc__= """
Exporter for Modeling input. Options are:

noHierarchy: Entities don't honour the 'inherits' attribute.
             This will be needed when exporting the old database scheme.
database:    The name of the database. This will be used to name the database
             in the database engine and also the model name.
host:        The name of the host where the database engine runs.
             The default is 'localhost'.
user:        The user name that will be used to connect to the database engine.
             The default is 'papo'.
password:    The password that will be used to connect to the database engine.
             The default is ''.
adaptorName: The name of the Modeling adaptor to be used.

    """
    # import pdb; pdb.Pdb().set_trace()


    header="""# generated from %s - DO NOT EDIT!

from Modeling.PyModel import *

Entity.defaults['properties']= [
  APrimaryKey ('id', isClassProperty=0, isRequired=1, doc='Primary key!')
]

_connDict= {
    'database': '%s',
    'host': '%s',
    'user': '%s',
    'password': '%s'
}

model= Model ('%s', adaptorName='%s', connDict=_connDict)
model.version='0.1'

"""
    varchar= re.compile (r'(var)?char *\(([0-9]+)\)')
    numeric= re.compile (r'numeric *\(([0-9]+),([0-9]+)\)')

    def __tableName__ (self, name):
        # some_thing
        name= self.__fieldName__ (name)
        # someThing
        name= name[0:1].upper ()+name[1:]
        # SomeThing
        return name

    def __fieldName__ (self, name):
        def __upper__ (letter):
            return letter.group (1).upper ()
        # some_thing
        name= re.sub (r'_([a-z])', __upper__, name)
        # someThing
        return name

    def __pluralFieldName__ (self, name):
        # some_thing
        name= self.__fieldName__ (name)
        # someThing
        name= pluralize (name)
        # someThings
        return name

    def export (self, xot, **opts):
        try:
            withoutHierarchy= opts['noHierarchy']
        except KeyError:
            # default value
            withoutHierarchy= False
        try:
            database= opts['database']
        except KeyError:
            # better error handling
            raise
        try:
            host= opts['host']
        except KeyError:
            # default value
            host= 'localhost'
        try:
            user= opts['user']
        except KeyError:
            # default value
            user= 'papo'
        try:
            passwd= opts['password']
        except KeyError:
            # default value
            passwd= ''
        try:
            adaptor= opts['adaptorName']
        except KeyError:
            # better error handling
            raise

        code= self.header % (xot.filename, database, host, user, passwd, self.__tableName__ (database), adaptor)
        self.extendTables (xot.tables)
        code+= "model.entities= [\n"+"\n".join (map (lambda t: self.table (t, withoutHierarchy), xot.tables.values ()))+"]\n"
        # code+= "model.associations= [\n"+"\n".join (map (self.assoc, xot.tables.values ()))+"]\n"
        return code

    def extendTables (self, tables):
        # we assume that each reference is a m-to-1
        # so for this table would be a RToOne to the target
        # and for the target a RToMany to this one
        for table in tables.keys ():
            for ref in tables[table].get_references ():
                field= ref.inverse
                if field:
                    target= ref.get_reference ().name
                    try:
                        tables[target].backRefs[field]= (tables[table], ref.name)
                    except (AttributeError, KeyError):
                        tables[target].backRefs= {field: (tables[table], ref.name)}

    def table (self, table, withoutHierarchy):
        entity=  "    Entity ('%s',\n" % self.__tableName__ (table.name)
        for attr in ['className', 'moduleName', 'externalName', 'isAbstract', 'isReadOnly', 'doc']:
            try:
                value= getattr (table, attr)
                if value:
                    entity+= "            %s= %s,\n" % (attr, value)
            except AttributeError:
                pass
        entity+= "            properties= [\n"
        entity+= "".join (map (self.field, table.fields.values ()))
        try:
            entity+= "".join (map (self.backRef, table.backRefs.keys (), table.backRefs.values ()))
        except AttributeError:
            pass

        entity+= "            ],\n"
        if not withoutHierarchy and table.group.parent:
            entity+= "            parent= '%s',\n" % self.__tableName__ (table.group.parent)
        entity+= "    ),\n"
        return entity

    def field (self, field):
        fieldName= self.__fieldName__ (field.name)
        contents= ["'%s'" % fieldName]
        try:
            try:
                relation= field.get_reference ()
                type= 'RToOne'
                contents+= ["'%s'" % self.__tableName__ (relation.name)]
                if field.inverse:
                    # contents+= ["inverse='%s'" % self.__pluralFieldName__ (field.inverse)]
                    contents+= ["inverse='%s'" % self.__fieldName__ (field.inverse)]
                if field.deleteRule:
                    contents+= ["deleteRule='%s'" % field.deleteRule.upper ()]
                if field.joinSemantic:
                    if field.joinSemantic=='full':
                        js= 0
                    elif field.joinSemantic=='outer':
                        js= 1
                    elif field.joinSemantic=='left':
                        js= 2
                    elif field.joinSemantic=='right':
                        js= 3
                    contents+= ["joinSemantic=%d" % js]

            except AttributeError:
                type= field.type
                varchar= self.varchar.match (type)
                numeric= self.numeric.match (type)
                if field.name=='id':
                    raise IdError, "it already is a default property"
                elif type=='int' or type=='bigint' or type=='boolean' or type=='integer':
                    if type=='boolean':
                        field.default= int(field.default)
                    type= "AInteger"
                elif varchar:
                    type= "AString"
                    size= varchar.group (2)
                    contents+= ["width=%d" % int (size)]
                elif type=='text':
                    type= "AString"
                elif type=='timestamp' or type=='date':
                    type= "ADateTime"
                elif numeric:
                    size, prec= numeric.group (1, 2)
                    type= "AFloat"
                    contents+= ["width=%d" % int (size), "precision=%d" % int(prec)]
                else:
                    raise NotImplementedError
                if field.default:
                    contents+= ["defaultValue=%s" % field.default]

            if field.classProp:
                contents+= ["isClassProperty=%d" % int (field.classProp)]
            if field.displayLabel:
                contents+= ["displayLabel='%s'" % field.displayLabel]
            if field.doc:
                contents+= ["comment='%s'" % field.doc.replace ("\n", "\\n")]
            code= "                "+type+" ("+', '.join (contents)+"),\n"
            if hasattr (field, 'externalType') and field.externalType:
                code+= "                # externalType is not implementd. you should use the exporter ModPsql or similar (if it exists)"
        except Exception, e:
            code= "                # dunno how to handle %s (%s)\n" % (fieldName, e)

        return code

    def backRef (self, field, target):
        return             "                RToMany ('%s', '%s', inverse='%s'),\n" % (self.__fieldName__ (field), self.__tableName__ (target[0].name), self.__fieldName__ (target[1]))

    def assoc (self, table):
        return "# no assocs for table %s yet; any reference is done by a RToMany/RToOne pair." % table.name
