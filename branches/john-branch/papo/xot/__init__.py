import libxml2

class Table(object):
    def __init__(self):
        self.fields = {}
        self.indexes = {}

class Xot(object):
    def __init__(self):
        self.tables = {}
    def load(kls, xmlfile):
        x = kls()
        ts = x.tables
        doc = libxml2.parseFile(xmlfile)
        for t in doc.xpathEval('/database/tables/table'):
            fs = ts[t.prop('name')] = Table()
            for f in t.xpathEval('fields/field'):
                fs.fields[f.prop('name')] = 1
            fs.indexes = [t.xpathEval('indexes/index')]
        return x
    load = classmethod(load)
        

load = Xot.load
