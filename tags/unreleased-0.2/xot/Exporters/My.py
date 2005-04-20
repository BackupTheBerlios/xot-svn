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
mysql exporter

No options yet.
"""

import DB

# xot uses postgres names for field types
translate = { "boolean": "bool",
              }

class exporter(DB.exporter):
    def field(self, field):
        """return the column-specific fraction of the CREATE TABLE"""
        out = field.name + ' '
        out += translate.setdefault(field.type, field.type)
        if field.auto_increment:
            out += " auto_increment"
        if not field.null:
            out += " NOT NULL"

        return out
    def index(self, index):
        """return the CREATE INDEX for the specified index"""
        out = ''
        types = { "unique": " UNIQUE ",
                  "fulltext": " FULLTEXT ",
                  "plain": " ",
                  "primary_key": 0,
                  }

        if types.get(index.type):
            out = "CREATE%sINDEX %s ON %s (%s);\n" % (
                types[index.type],
                index.name,
                index.table.name,
                ", ".join(map(lambda _: _.name, index.fields)),
                )
        return out

    def alter_table(field, table):
        """(mysql needs no alter table at this point)"""
        return ''
