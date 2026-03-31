from wurthless.clock.cvars.cvarwriter import CvarWriter

known_cvars = {}

#
# class Cvar: Single cvar instance
#
class Cvar(object):
    def __init__(self, registrant, name, datatype, default):
        self.registrant = registrant
        self.name = name
        self.datatype = datatype
        self.default = default
        self.setValue(default)

    def changedFromDefault(self):
        pass

    def setValue(self, value):
        if self.datatype == "Int":
            self.value = int(value)
        elif self.datatype == "Boolean":
            self.value = value == "True" or value is True
        elif self.datatype == "String":
            self.value = str(value)
        else:
            raise RuntimeError(f"unrecognized datatype: {self.datatype}")
        
    def getValue(self):
        return self.value


class CvarDefinition(object):
    def __init__(self, registrant, name, datatype, default):
        self.registrant = registrant
        self.name = name
        self.datatype = datatype
        self.default = default
    
    def instantiate(self):
        return Cvar(self.registrant, self.name, self.datatype, self.default)

# registerCvar(): Registers cvar.
def registerCvar(registrant: str, name: str, datatype: str, default: any):
    '''
    Register a cvar.
    - registrant: name of the module to which this cvar belongs
    - name: name of the cvar itself. This is unique to that module.
    - datatype: String indicating datatype, which must be a primitive: Int, Double, String, etc.
    - default: Default value for this cvar.

    Cvars are registered internally as "registrant:name".
    '''
    defn = CvarDefinition(registrant, name, datatype, default)
    key = registrant + ':' + name
    known_cvars[ key ] = defn
    print(f"reg cvar: {key}")

class Cvars(object):
    '''
    Config variables registry.
    '''
    def __init__(self):
        # this will point "registrant:name" -> cvar
        self.cvars = {}

        for i in known_cvars.values():
            key = i.registrant + ":" + i.name
            self.cvars[key] = i.instantiate()

        self.writer = None

    def _find(self, registrant: str, name: str) -> Cvar:
        key = registrant + ":" + name
        if key in self.cvars:
            return self.cvars[key]

        raise RuntimeError(f"cvar not registered/recognized: {key}\n\nentire cvar table is: {self.cvars}")

    def setWriter(self, writer: CvarWriter):
        self.writer = writer

    def get(self, registrant: str, name: str) -> any:
        '''
        Get value of the given cvar. If cvar not found, panic.
        '''
        key = registrant + ":" + name
        return self._find(registrant, name).getValue()
    
    def set(self, registrant: str, name: str, value: any):
        '''
        Set value of the given cvar. If cvar not found, panic.
        '''
        self._find(registrant, name).setValue(value)

    def configure(self, registrant: str, kvmappings: dict[str,any]):
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