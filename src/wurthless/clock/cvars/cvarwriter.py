#
# Cvar writer interface. This loads/unloads cvars.
#

import binascii
import os

class CvarWriter(object):
    def __init__(self):
        pass

    def load(self, cvardict):
        pass

    def save(self, cvardict):
        pass

class TokenedCvarWriter(CvarWriter):
    def __init__(self):
        self.preflights = [
            # factory settings
            u"secrets/factory.ini",

            # stuff specific to this individual device (currently unused)
            u"secrets/guid.ini"
        ]
        self.path = u'secrets/secrets.ini'

    def _load_optionals(self, cvardict, filenames):
        for p in self.preflights:
            try:
                self.loadFrom(cvardict, p)
            except Exception as e:
                # suppress - preflights aren't 100% necessary
                pass

    def _scan_overrides(self) -> list:
        result = []
        for f in os.listdir("secrets/"):
            if f.startswith("ext_") and f.endswith(".ini"):
                result.append(f)
        return result

    def addPreflight(self, path):
        self.preflights.append(path)

    def loadFrom(self, cvardict, path):
        with open(path, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                # preserve base64 nonsense
                line = line.split(u"=",1)
                print(u"handling: %s"%(line))
                value = str( binascii.a2b_base64(bytearray(line[1], 'utf-8')), 'utf-8' )
                if line[0] not in cvardict:
                    raise RuntimeError(u"cvardict doesn't know cvar: %s"%(line[0]))
                cvardict[line[0]].setValue(value)
                print(u"handled: %s"%(line))

    def load(self, cvardict):
        self._load_optionals(cvardict, self.preflights)
        self._load_optionals(cvardict, self._scan_overrides())
        
        try:
            self.loadFrom(cvardict, self.path)
        except OSError as e:
            self.save(cvardict)

    def save(self, cvardict):
        with open(self.path, "w") as f:
            f.write(u"# tmucitw config, do not modify this as values will get overwritten\n")
            for cvar in cvardict.values():
                # any cvar that is not user-configurable does not get saved.
                if cvar.registrant.startswith(u"config"):
                    f.write(u"%s:%s=%s"%(cvar.registrant,cvar.name, str( binascii.b2a_base64(bytearray(str(cvar.getValue()),'utf-8')), 'utf-8') ) )
