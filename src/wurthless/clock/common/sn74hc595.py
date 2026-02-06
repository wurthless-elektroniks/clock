'''
Generic SN74HC595 shift register driver
'''

from machine import Pin

def sn74hc595_shift_bits_out( num_bits: int,
                              bits: int,
                              serial_data_pin: Pin,
                              serial_clock_pin: Pin,
                              shiftreg_reset_pin: Pin,
                              shiftreg_latch_pin: Pin):
    
    # pull shiftregister reset pin low (clears all shift register bits to 0)
    shiftreg_reset_pin.value(0)

    # pull everything else low while we wait for reset to happen
    shiftreg_latch_pin.value(0)
    serial_data_pin.value(0)
    serial_clock_pin.value(0)

    # de-assert shift register reset (it's ready for data to be clocked in now)
    shiftreg_reset_pin.value(1)

    for i in range(num_bits):
        # one bit out at a time, left-to-right
        serial_data_pin.value( (bits & (1 << (num_bits - (i + 1)))) != 0 )
        
        # pulse clock bit (data line only sampled on rising edge of clock)
        serial_clock_pin.value(1)
        serial_clock_pin.value(0)
    
    # latch the data into place
    shiftreg_latch_pin.value(1)
    shiftreg_latch_pin.value(0)
