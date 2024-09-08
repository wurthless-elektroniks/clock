
class Nic(object):
    '''
    Interface to a network device.
    '''
    
    def initAsClient(self):
        '''
        Initialize the NIC as client.
        Returns after init happens regardless of outcome.
        '''
        pass

    def initAsServer(self):
        '''
        Initialize the NIC as server.
        '''
        pass

    def isUp(self) -> bool:
        '''
        Return true if interface up.
        '''
        return False

    def shutdown(self):
        '''
        Shuts down the NIC.
        '''
        pass

