#
# Defines a platform. "root" is the default platform.
#

platforms = {}

class PlatformBuilder(object):
    def __init__(self, identifier, name, parent=None):
        self.identifier = identifier
        self.name = name
        self.cvar_overrides = []
        if parent is not None:
            # import settings from parent builder
            pass

    def displayDriver(self, cls):
        self.displayDriver = cls
        return self
    
    def decoratingDisplayDriver(self, decoratorCls):
        return self

    def inputDriver(self, cls):
        self.inputDriver = cls
        return self

    def decoratingInputDriver(self, decoratorCls):
        return self

    def rtcDriver(self, cls):
        self.rtcDriver = cls
        return self
    
    def decoratingRtcDriver(self, decoratorCls):
        return self

    def nicDriver(self, cls):
        self.nicDriver = cls
        return self

    def decoratingNicDriver(self, decoratorCls):
        return self

    def timesources(self, ts):
        self.timesources = ts
        return self

    def cvarOverride(self, registrant, name, value):
        return self

    '''
    Call to finish setup of the builder and to register it for later use.
    '''
    def done(self):
        pass

platforms[u"root"] = PlatformBuilder() \
                        .displayDriver(None) \
                        .inputDriver(None) \
                        .rtcDriver(None) \
                        .nicDriver(None) \
                        .timesources([]) \
                        .done()


def platformBuilder(identifier, name, parent=None):
    realParent = 'root' if parent is None else parent
    if realParent not in platforms:
        raise RuntimeError(u"platform not registered: %s"%(realParent))
    
    # TODO: catch circular references. for now assume coders are on their best behavior

'''
Initializes platform and related drivers.

Returns a ToT.
'''
def platformInit(identifier):
    
    pass