#
# Base object.
#

class BaseObj(object):
    def __init__(self):
        pass

    '''
    __injects__(): return a list of dependency injections that need to be done when this object is instantiated.
    '''
    def __injects__(self):
        return []

    '''
    __postConstruct__(): called after injects have been performed.
    '''
    def __postConstruct__(self):
        pass

