#
# Config variables registry
#
# cvars are represented in json as follows (an example):
#
# registrant:  String. Indicates file that registered this cvar. 
#              If cvar not yet registered, attempts to force import that file.
#              If that fails, or if the cvar never gets registered, throw exception.
# name:        String. Name of the cvar.
# datatype:    String. Python datatype. Must be primitive: Int, Double, String, etc.
# description: String. Describes what the cvar is.
# default:     Value matching datatype. If set, cvar defaults to this. If not, cvar defaults to None. 
#

known_cvars = {}

#
# class Cvar: Single cvar instance
#
class Cvar(object):
    def __init__(self, registrant, name, datatype, description, default):
        self.registrant = registrant
        self.name = name
        self.datatype = datatype
        self.description = description
        self.default = default
        self.setValue(default)

    def changedFromDefault(self):
        pass

    def setValue(self, value):
        if self.datatype == u"Int":
            self.value = int(value)
        elif self.datatype == u"Boolean":
            self.value = value == u"True" or value is True
        elif self.datatype == u"String":
            self.value = str(value)
        else:
            raise RuntimeError(u"unrecognized datatype: %s"%(self.datatype))
        
    def getValue(self):
        return self.value


class CvarDefinition(object):
    def __init__(self, registrant, name, datatype, description, default):
        self.registrant = registrant
        self.name = name
        self.datatype = datatype
        self.description = description
        self.default = default
    
    def instantiate(self):
        return Cvar(self.registrant, self.name, self.datatype, self.description, self.default)

# registerCvar(): Registers cvar.
def registerCvar(registrant, name, datatype, description, default):
    defn = CvarDefinition(registrant, name, datatype, description, default)
    key = registrant + u':' + name
    known_cvars[ registrant + u':' + name ] = defn
    print(u"registered cvar: %s" % (key))

class Cvars(object):
    def __init__(self):
        # this will point "registrant:name" -> cvar
        self.cvars = {}

        for i in known_cvars.values():
            key = i.registrant + u":" + i.name
            self.cvars[key] = i.instantiate()

        self.writer = None

    def _find(self, registrant, name):
        key = registrant + u":" + name
        if key in self.cvars:
            return self.cvars[key]

        raise RuntimeError(u"cvar not registered/recognized: %s\n\nentire cvar table is: %s" %(key, self.cvars))

    def setWriter(self, writer):
        self.writer = writer

    def get(self, registrant, name):
        key = registrant + u":" + name
        return self._find(registrant, name).getValue()
    
    def set(self, registrant, name, value):
        self._find(registrant, name).setValue(value)

    def configure(self, registrant, kvmappings):
        '''
        Given dict of name->value, bulk set cvars for the given registrant.
        '''
        for name,value in kvmappings.items():
            self.set(registrant,name,value)

    def load(self):
        if self.writer is not None:
            self.writer.load(self.cvars)

    def save(self):
        if self.writer is not None:
            self.writer.save(self.cvars)