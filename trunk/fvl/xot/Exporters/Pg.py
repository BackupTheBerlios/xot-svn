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
postgres >= 7.2 exporter

No options yet.
"""


import DB
import re
is_int = re.compile('int$')

class exporter(DB.exporter):
    def field(self, field):
        """return the column-specific fraction of the CREATE TABLE"""
        out = field.name + ' '
        type = field.type
        default = field.default
        if field.auto_increment:
            assert is_int.search(type)
            type = re.sub(is_int, 'serial', type)
        out += type
        if default is not None:
            out += ' DEFAULT ' + default
        if not field.null:
            out += ' NOT NULL'
        return out

    def index(self, index):
        """return the CREATE INDEX for the specified index"""
        func = index.function
        type = index.type
        name = index.name
        table = index.table.name
        where = index.where
        method = index.method

        sql = ''

        if type in ('unique', 'plain'):
            sql = 'CREATE '
            if type == 'unique':
                sql += 'UNIQUE '
            sql += "INDEX %s ON %s" % (name, table)
            if method:
                sql += "USING %s" % method
            sql += "("
            if func:
                sql += func + "("
            sql += ", ".join(map(lambda _: _.name, index.fields))
            if func:
                sql += ")"
            sql += ")"
            if where:
                sql += " WHERE " + where
            sql += ";\n"

        return sql

    def alter_table(self, table):
        """return the ALTER TABLE to create integrity constraints for the specified table"""
        sql=''
        for ref in table.references:
            sql += ('ALTER TABLE %s\n' +
                    '    ADD FOREIGN KEY (%s) REFERENCES %s\n' +
                    '    ON DELETE RESTRICT ON UPDATE RESTRICT;\n') % (
                ref.table.name, ref.name, ref.reference.name)
        return sql

