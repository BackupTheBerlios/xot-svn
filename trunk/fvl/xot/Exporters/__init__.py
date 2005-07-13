# Copyright 2003 Fundacion Via Libre
#
# This file is part of PAPO.
# 
# PAPO is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# PAPO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PAPO; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

desc = {'Pg': 'produces SQL statements to create the database on postgres (>=7.2)',
        'My': 'produces SQL statements to create the database on MySQL',
        'GV': 'produces output in GraphViz\'s dot format',
        'Zot': 'produces output suitable for zot',
        'Mod': 'produces a python script for Modeling',
        'CimarronXMLui': 'produces a Cimarron xml definition.',
       }
__all__ = desc.keys()
