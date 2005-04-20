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

""" foo
"""
import sys, getopt, os, stat, cPickle, os.path
from xot import Exporters
#import Xot  <--  moved down for performance reasons

DefaultExporter = 'Pg'

def usage():
    print """Usage: exotic [options] xotfile
where the options are:
     -h --help           Show this message
     -H --exporter-help  Show the help of the selected exporter
 -Oopts --options=opts   Pass these options to the exporter. 'opts' is a
                         comma-separated list of key:value options (described
                         in --exporter-help)
     -j --just-pickle    Pickle and exit, no export
     -r --repickle       Force repickling
     -n --no-pickle      Don't pickle
  -khks --hooks=hks      Apply these hooks. 'hks' can be a comma-separated
                         list or the special name ':all:'
  -eexp --exporter=exp   Select an alternate exporter:"""
    for eng, desc in Exporters.desc.items():
        if eng == DefaultExporter:
            eng = "* "+eng
        print "%8s: %s" % (eng, desc)



def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hHO:jrne:k:", ["help",
                                                   "exporter-help",
                                                   "options="
                                                   "just-pickle",
                                                   "repickle",
                                                   "no-pickle",
                                                   "exporter=",
                                                   "hooks="])
    except getopt.GetoptError, err:
        print err
        usage()
        sys.exit(2)

    # default values for arguments:
    exporter = DefaultExporter
    repickle = False
    pickle = True
    export = True
    options = {}
    exporter_help = False
    hook_names = ''
    for o, a in opts:
        if o in ("-r", "--repickle"):
            repickle = True
        if o in ("-j", "--just-pickle"):
            export = False
        if o in ("-n", "--no-pickle"):
            pickle = False
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-H", "--exporter-help"):
            exporter_help = True
        if o in ("-e", "--exporter"):
            if a not in Exporters.desc:
                raise ImportError, "`%s' is not one of one of %s" % \
                      (a, ", ".join(Exporters.desc))
            exporter = a
        if o in ("-k", "--hooks"):
            hook_names = a
        if o in ("-O", "--options"):
            options = dict(map(lambda _: (_.split(':') + [1])[:2],
                               a.split(',')))

    Exporter = __import__('Exporters.%s' % exporter,
                          globals(), locals(), [exporter])
    if exporter_help:
        print Exporter.__doc__.strip()
        sys.exit()

    if not args:
        print "No xotfile supplied"
        usage()
        sys.exit(3)

    # Ok, we've actually got to do some work.
    from xot import Xot

    file = args[0]
    fs = os.stat(file)
    pickled = os.path.join(os.path.dirname(file),
                           '.%s.%s.pickle' % (os.path.basename(file),
                                              hook_names))
    ps = None
    try:
        ps = os.stat(pickled)
    except OSError:
        pass

    xot=None
    if pickle and not repickle and ps and ps[stat.ST_MTIME] > fs[stat.ST_MTIME]:
        p=open(pickled)
        xot=cPickle.load(p)
    else:
        xot=Xot.new(file, *(hook_names.split(',')))
        if pickle:
            p=open(pickled, 'w')
            cPickle.dump(xot, p, True)

    if export:
        xot.exporter = Exporter.exporter()
        print xot.export(**options)
