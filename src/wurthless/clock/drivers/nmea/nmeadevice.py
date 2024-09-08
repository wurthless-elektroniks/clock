#
# Generic NMEA device driver
#
# NMEA devices communicate over serial cables and thus this implementation
# assumes we'll be talking to the device over I/O streams.
#
# High-level stuff happens in here. Low-level protocol wrangling happens in nmeaprot.py.
#

from wurthless.clock.drivers.nmea.nmeaprot import nmeaParseBytes,nmeaParseGsv,nmeaParseZda
from wurthless.clock.common.timestamp import timeTupleToTimestamp
import _thread

class NmeaDevice(object):
    '''
    Generic NMEA device driver.
    '''
    def __init__(self, uart):
        self.uart = uart
        self.mappers = self._getMappers()

        # tuple [ yyyy, mm, dd, hh, mm, ss ] - assumes UTC
        self.dt = [ 0, 0, 0, 0, 0, 0 ]
        self.sats_up = 0

    def _handleGnzda(self, message):
        gsv = nmeaParseZda(message)
        if gsv is None:
            return
        d = [ gsv[5], gsv[4], gsv[3], gsv[0], gsv[1], gsv[2] ]
        self.dt = d

    def _handleGpgsv(self, message):
        gsv = nmeaParseGsv(message)
        if gsv is None:
            return
        self.sats_up = gsv[2]

    def _getMappers(self):
        mappers = {}
        
        mappers["GNZDA"] = lambda msg: self._handleGnzda(msg)
        mappers["GPGSV"] = lambda msg: self._handleGpgsv(msg)
        
        return mappers
    
    def _pollUart(self):
        lines = []
        l = None
        while True:
            l = self.uart.readline()
            if l is None:
                break
            lines.append(l)
            if len(lines) >= 32:
                break

        for line in lines:
            nmeaParseBytes(line, self.mappers)

    def isUp(self):
        '''
        Return True if device is initialized and receiving valid GNSS data.
        '''
        self._pollUart()
        return self.sats_up > 0 and self.dt[0] > 2022
    
    def getSatellitesVisible(self):
        return self.sats_up
    
    def getUtcTime(self):
        '''
        Query for current UTC timestamp.
        '''
        self._pollUart()

        d = self.dt
        if d[0] is None:
            return 0
        
        packed_time = ( d[0], d[1], d[2], d[3], d[4], d[5], 0, 0, 0 )
        return timeTupleToTimestamp(packed_time)