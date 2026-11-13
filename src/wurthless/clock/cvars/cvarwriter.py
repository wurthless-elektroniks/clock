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

def _file_exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False

class TokenedCvarWriter(CvarWriter):
    def __init__(self):
        self.preflights = [
            # factory settings
            "secrets/factory.ini",

            # stuff specific to this individual device (currently unused)
            "secrets/guid.ini"
        ]
        self.path = 'secrets/secrets.ini'

    def _load_optionals(self, cvardict, filenames):
        for p in filenames:
            try:
                self.loadFrom(cvardict, p)
            except Exception:
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
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                # preserve base64 nonsense
                line = line.split("=",1)
                print(f"handling: {line}")
                value = str( binascii.a2b_base64(bytearray(line[1], 'utf-8')), 'utf-8' )
                if line[0] not in cvardict:
                    raise RuntimeError(f"cvardict doesn't know cvar: {line[0]}")
                cvardict[line[0]].setValue(value)
                print(f"handled: {line}")

    def load(self, cvardict):
        self._load_optionals(cvardict, self.preflights)
        self._load_optionals(cvardict, self._scan_overrides())

        for path in [ self.path, f"{self.path}.bak"]:
            if _file_exists(path) is False:
                continue

            try:
                self.loadFrom(cvardict, path)
                return # load success
            except Exception:
                pass

        # failed to load config, so try writing defaults
        self.save(cvardict)

    def save(self, cvardict):
        if _file_exists("cvars.tmp"):
            os.remove("cvars.tmp")

        with open("cvars.tmp", "w", encoding="utf-8") as f:
            f.write("# tmucitw config, do not modify this as values will get overwritten\n")
            for cvar in cvardict.values():
                # any cvar that is not user-configurable does not get saved.
                if cvar.registrant.startswith("config"):
                    f.write("%s:%s=%s"%(cvar.registrant,cvar.name, str( binascii.b2a_base64(bytearray(str(cvar.getValue()),'utf-8')), 'utf-8') ) )

        if _file_exists(f"{self.path}.bak"):
            os.remove(f"{self.path}.bak")

        if _file_exists(f"{self.path}"):
            os.rename(self.path, f"{self.path}.bak")

        os.rename("cvars.tmp", self.path)

        if _file_exists(f"{self.path}.bak"):
            os.remove(f"{self.path}.bak")
