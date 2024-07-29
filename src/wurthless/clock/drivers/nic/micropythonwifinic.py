#
# Micropython Wifi network driver
#

import network
import time

from wurthless.clock.cvars.cvars import registerCvar
from wurthless.clock.api.nic import Nic

registerCvar(u"wurthless.clock.drivers.nic.micropythonwifinic",
             u"device_name",
             u"String",
             u"Defines device name on network, if possible. Default is blank (let network stack pick it for us)",
             u"")

registerCvar(u"wurthless.clock.drivers.nic.micropythonwifinic",
             u"server_ap_name",
             u"String",
             u"In server mode, defines accesspoint name. Default is TMUCITW.",
             u"TMUCITW")

registerCvar(u"wurthless.clock.drivers.nic.micropythonwifinic",
             u"server_ap_password",
             u"String",
             u"In server mode, defines accesspoint password. Default is wurthless.",
             u"wurthless")

registerCvar(u"wurthless.clock.drivers.nic.micropythonwifinic",
             u"max_wait",
             u"Int",
             u"Timeout when connecting to access point. Default is 10.",
             10)

class MicropythonWifiNic(Nic):
    def __init__(self, tot):
        self.tot = tot
        self._nic = None

    def assertNicNotUp(self):
        if self._nic is not None:
            raise RuntimeError(u"NIC already up. Shut it down first.")
        
    def isUp(self):
        return self._nic is not None

    def initAsClient(self):
        self.assertNicNotUp()
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        ssid = self.tot.cvars().get(u"config.nic",u"wifi_ap_name")
        password = self.tot.cvars().get(u"config.nic",u"wifi_ap_password")
        
        if ssid == u"" or password == u"":
            print(u"ERROR: wifi_ap_name and/or wifi_ap_password not set.")
            return

        wlan.connect(ssid, password)
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print('waiting for connection...')
            time.sleep(5)

        # occasionally wlan.status() returns something other than 3 even if the network is connected.
        # such behavior occurs on ESP32-based boards.
        if wlan.isconnected() is False and wlan.status() != 3:
            print(u"ERROR: cannot connect to accesspoint!")
            return
        else:
            print('connected')
            status = wlan.ifconfig()
            print( 'ip = ' + status[0] )
        
        self._nic = wlan
    
    def initAsServer(self):
        self.assertNicNotUp()
        
        ssid = self.tot.cvars().get(u"wurthless.clock.drivers.nic.micropythonwifinic",u"server_ap_name")
        password = self.tot.cvars().get(u"wurthless.clock.drivers.nic.micropythonwifinic",u"server_ap_password")
    
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=ssid, password=password) 
        ap.active(True)

        max_wait = 10
        while max_wait > 0:
            if ap.active is True:
                break
            max_wait -= 1
            print(u"Waiting for accesspoint to come up")
            time.sleep(1)

        if ap.active is False:
            raise RuntimeError(u"accesspoint didn't come up in time.")
        
        self._nic = ap
