#
# Stub NIC which just says "look, just try accessing the network as-is" rather than returning its actual status.
#

from wurthless.clock.api.nic import Nic

class StubNic(Nic):
    def initAsClient(self):
        pass
    
    def initAsServer(self):
        pass

    def isUp(self):
        return True