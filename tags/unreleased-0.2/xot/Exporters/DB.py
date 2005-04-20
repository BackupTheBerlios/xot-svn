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
Base class for database exporters.

Basically, stuff is here if it's pretty much standard, and you should
override whatever isn't.


"""

class exporter(object):
    def export(self, xot):
        """return the sql statements to create the database represented by the xot"""
        txt="\n".join(map(self.create_table, xot.tables.values()))
        txt+="\n".join(map(self.alter_table, xot.tables.values()))
        return txt
    def create_table(self, table):
        """return the CREATE TABLE for the specified table"""
        sql = 'CREATE TABLE %s (\n    ' % table.name
        sql += ',\n    '.join(map(self.field, table.fields.values()))
        sql += ',\n    PRIMARY KEY (%s)\n);\n' % ', '.join(map(lambda _: _.name, table.primary_keys))
        sql += ''.join(map(self.index, table.indexes.values()))
        return sql
    def field(self, field):
        """return the column-specific fraction of the CREATE TABLE"""
        out = field.name + ' ' + type
        if not field.null:
            out += ' NOT NULL'
        return out
    def index(self, index):
        """return the CREATE INDEX for the specified index"""
        raise NotImplementedError, \
              "there is no standard CREATE INDEX construct (or is there? let me know!)"
    def alter_table(self, table):
        """return the ALTER TABLE to create integrity constraints for the specified table"""
        raise NotImplementedError, \
              "there is no standard ALTER TABLE construct (or is there? let me know!)"
