
from machine import Pin


def sn74hc595_shift_bits_out( num_bits: int,
                              bits: int,
                              serial_data_pin: Pin,
                              serial_clock_pin: Pin,
                              shiftreg_reset_pin: Pin,
                              shiftreg_latch_pin: Pin):
    
    shiftreg_reset_pin.value(0)
    shiftreg_latch_pin.value(0)
    serial_data_pin.value(0)
    serial_clock_pin.value(0)
    shiftreg_reset_pin.value(1)
    for i in range(num_bits):
        serial_data_pin.value( (bits & (1 << (num_bits - (i + 1)))) != 0 )
        serial_clock_pin.value(1)
        serial_clock_pin.value(0)
    
    shiftreg_latch_pin.value(1)
    shiftreg_latch_pin.value(0)
