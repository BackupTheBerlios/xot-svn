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
zot exporter

No options yet.
"""

class exporter(object):
    def export(self, xot):
        txt=''
        for table in xot.tables.values():
            txt += table.name
            if table.group.parent:
                txt += "(%s)" % table.group.parent
            txt += ":\n"
            for field in table.fields.values():
                txt += "    %s " % field.name
                if hasattr(field, "symbolic"):
                    txt += "-> %s\n" % field.symbolic
                else:
                    txt += "(%s)\n" % field.type
            for hook in table.group.hooks:
                txt += "    :%s:\n" % hook

        return txt

