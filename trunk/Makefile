# Copyright 2003, 2004 Fundacion Via Libre
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

PREFIX=~/local
PYTHONVER=2.3
BINDIR=$(PREFIX)/bin
LIBDIR=$(PREFIX)/lib/python2.3/site-packages
SHAREDIR=$(PREFIX)/share/xot

SUBDIRS=xot
DATA=xot.dtd

pwd=$(shell pwd)
python=python$(PYTHONVER)
dir=xot

all:
	$(python) /usr/lib/$(python)/compileall.py .

install:
	mkdir -pv $(BINDIR)
	ln -sf $(pwd)/exotic $(BINDIR)
	mkdir -pv $(LIBDIR)
	ln -sf $(pwd)/$(dir) $(LIBDIR)
	mkdir -pv $(SHAREDIR)
	ln -sf $(pwd)/xot.dtd $(SHAREDIR)
	@echo "***** INSTALLED *****"
	@echo "make sure $(BINDIR) is in your path"
	@echo "and $(LIBDIR) is in you python path"

clean:
	rm -f *.pyc *.pyo
	$(foreach dir,$(SUBDIRS),make -C $(dir) clean)

country:
	@./exotic -n -eCimarronXMLui -Oclass:country,import:model.country.Country examples/country.xot

state:
	@./exotic -n -eCimarronXMLui -Oclass:state,import:model.country.Country+model.country.State examples/country.xot

person:
#	@./exotic -n -eCimarronXMLui -Oclass:person,\
		find:name+surname,\
		import:model.person.Person+model.person.Address,\
		more:addreses \
		examples/person.xot
	@./exotic -n -eCimarronXMLui -Oxin:examples/person.xin examples/person.xot
