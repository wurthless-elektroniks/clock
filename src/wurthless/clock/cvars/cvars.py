from wurthless.clock.cvars.cvarwriter import CvarWriter

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
def registerCvar(registrant: str, name: str, datatype: str, description: str, default: Any):
    '''
    Register a cvar.
    - registrant: name of the module to which this cvar belongs
    - name: name of the cvar itself. This is unique to that module.
    - datatype: String indicating datatype, which must be a primitive: Int, Double, String, etc.
    - description: Documentation about what that cvar is.
    - default: Default value for this cvar.

    Cvars are registered internally as "registrant:name".
    '''
    defn = CvarDefinition(registrant, name, datatype, description, default)
    key = registrant + u':' + name
    known_cvars[ registrant + u':' + name ] = defn
    print(u"registered cvar: %s" % (key))

class Cvars(object):
    '''
    Config variables registry.
    '''
    def __init__(self):
        # this will point "registrant:name" -> cvar
        self.cvars = {}

        for i in known_cvars.values():
            key = i.registrant + u":" + i.name
            self.cvars[key] = i.instantiate()

        self.writer = None

    def _find(self, registrant: str, name: str) -> Cvar:
        key = registrant + u":" + name
        if key in self.cvars:
            return self.cvars[key]

        raise RuntimeError(u"cvar not registered/recognized: %s\n\nentire cvar table is: %s" %(key, self.cvars))

    def setWriter(self, writer: CvarWriter):
        self.writer = writer

    def get(self, registrant: str, name: str) -> Any:
        '''
        Get value of the given cvar. If cvar not found, panic.
        '''
        key = registrant + u":" + name
        return self._find(registrant, name).getValue()
    
    def set(self, registrant: str, name: str, value: Any):
        '''
        Set value of the given cvar. If cvar not found, panic.
        '''
        self._find(registrant, name).setValue(value)

    def configure(self, registrant: str, kvmappings: dict[str,Any]):
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