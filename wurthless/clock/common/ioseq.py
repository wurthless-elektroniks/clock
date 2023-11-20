#
# Generic I/O sequencer for systems that do not have a builtin statemachine.
#

from machine import Pin,Timer

OPCODE_WAIT = 1  # WAIT x  - wait number of states
OPCODE_WAA  = 2  # WAA - load wait counter with A
OPCODE_WAB  = 3  # WAB - load wait counter with B
OPCODE_BSR  = 4  # BSR     - discard LSB on shift register
OPCODE_ISR  = 5  # ISR x   - read from pin to MSB of shift register
OPCODE_OSR  = 6  # OSR x   - write LSB of shift register to pin
OPCODE_PM   = 7  # PM  x,x - change pin mode to given value
OPCODE_PV   = 8  # PV x,x  - explicitly set given pin to value
OPCODE_PUL  = 9  # PUL x   - change pin to input, pulled up


class IoSequencer(object):
    def __init__(self):
        self.program = []
        self.pins = {}

        self.program_counter = 0

        self.wait_states = 0

        # value the shift register will be reloaded with when the program resets
        self.shift_register_reload  = 0

        # whatever is being shifted out to the shift register
        self.shift_register_current = 0

        # last value of the shift register when the program stopped executing
        self.shift_register_last    = 0

        self.a = 0
        self.b = 0

        self.timer = Timer(0)

    '''
    Start the program, if it isn't started already.
    '''
    def exec(self):
        self.reset()
        self.timer.init(freq=10000,callback=self._tick)

    '''
    Stop executing the program
    '''
    def stop(self):
        self.timer.deinit()

    '''
    Clear existing program
    '''
    def clrprg(self):
        pass

    '''
    Store current value of shift register, reload shift register, and place the program counter at position 0.
    '''
    def reset(self):
        self.shift_register_last = self.shift_register_current
        self.shift_register_current = self.shift_register_reload
        self.program_counter = 0

    def _tick(self, t):
        if self.wait_states > 0:
            self.wait_states -= 1
            return

        # if past the end of the program, spend this tick resetting the statemachine
        if self.program_counter >= len(self.program):
            self.reset()
            return
 
        # BEWARE! Timing is VERY tight in here when the state machine is running!
        # Keep your code as simple and fast as possible so the tick can stop executing!
        op = self.program[self.program_counter]
        if op[0] == OPCODE_PM:
            self.pins[op[1]].init(mode=op[2])
        elif op[0] == OPCODE_PUL:
            self.pins[op[1]].init(mode=Pin.IN, pull=Pin.PULL_UP)
        elif op[0] == OPCODE_PV:
            self.pins[op[1]].value(op[2])
        elif op[0] == OPCODE_WAIT:
            self.wait_states = op[1]
        elif op[0] == OPCODE_WAA:
            self.wait_states = self.a
        elif op[0] == OPCODE_WAB:
            self.wait_states = self.b
        elif op[0] == OPCODE_BSR:
            self.shift_register_current >>= 1
        elif op[0] == OPCODE_ISR:
            self.shift_register_current >>= 1
            self.shift_register_current |= (self.pins[op[1]].value() << 31)
        elif op[0] == OPCODE_OSR:
            self.pins[op[1]].value( self.shift_register_current & 1 )
            self.shift_register_current >>= 1
        else:
            # don't have enough time for complaining about illegal opcodes, so do nothing
            pass
        self.program_counter += 1

    '''
    Assign pin to sequencer. Software simply adds it to a dict pointing pin -> Pin(pin).
    Pin direction, pullup, etc. is not configured.
    '''
    def assignPin(self, pin):
        self.pins[pin] = Pin(pin)

    '''
    Configure a pin already assigned to the statemachine.
    ONLY use this if the pin will not be reconfigured during program execution!
    '''
    def setPinMode(self, pin, mode, pull=-1):
        self.pins[pin].init(mode=mode,pull=pull)

    def setShiftRegisterValue(self, value):
        self.shift_register_reload = value

    def setA(self, a):
        self.a = a

    def setB(self, b):
        self.b = b        

    '''
    Advance shift register, discarding whatever bit is there.
    '''
    def assembleBurnShiftRegister(self):
        self.program.append( [ OPCODE_BSR ] )

    '''
    Output LSB on shift register to given pin and advance shift register.
    '''
    def assembleOutShiftRegister(self, pin):
        self.program.append( [ OPCODE_OSR, pin ] )

    '''
    Read from the given input, placing its value as MSB on shift register.
    '''
    def assembleInShiftRegister(self, pin):
        self.program.append( [ OPCODE_ISR, pin ] )

    '''
    Assemble wait state. State machine waits for the given amount of ticks before advancing.
    '''
    def assembleWait(self, wait):
        self.program.append( [ OPCODE_WAIT, wait ] )

    def assembleWAA(self):
        self.program.append( [ OPCODE_WAA ] )

    def assembleWAB(self):
        self.program.append( [ OPCODE_WAB ] )

    '''
    Explicitly set the given pin to the given value.
    '''
    def assemblePinValue(self, pin, value):
        self.program.append( [ OPCODE_PV, pin, value ] )

    '''
    Change pin to the current direction.
    '''
    def assemblePinMode(self, pin, direction):
        self.program.append( [ OPCODE_PM, pin, direction ] )

    '''
    Change pin to an input with internal pullup enabled.
    '''
    def assemblePinPullup(self, pin):
        self.program.append( [ OPCODE_PUL, pin ] )

