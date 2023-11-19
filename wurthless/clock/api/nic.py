#
# NIC control.
#

class Nic:
    '''
    Initialize the NIC as client.
    Returns after init happens regardless of outcome.
    '''
    def initAsClient(self):
        pass

    '''
    Initialize the NIC as server.
    '''
    def initAsServer(self):
        pass

    '''
    Return true if interface up.
    '''
    def isUp(self):
        return False

    '''
    Shuts down the NIC.
    '''
    def shutdown(self):
        pass

