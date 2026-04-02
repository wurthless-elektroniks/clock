'''
Manual configuration mode, so people don't need to connect over WiFi
'''

import time
import os


from wurthless.clock.api.tot import ToT
from wurthless.clock.api.display import Display
from wurthless.clock.api.inputs import Inputs
from wurthless.clock.drivers.input.debouncedinputs import DebouncedInputs
from wurthless.clock.common.prompt import promptMenu, promptConfirm, promptBoolean
from wurthless.clock.common.messages import messagesDisplaySyncMenuItem, \
                                            messagesDisplayNet, \
                                            messagesDisplayFact, \
                                            messagesDisplay12Hr, \
                                            messagesDisplayOn, \
                                            messagesDisplayOff, \
                                            messagesDisplayDone
from wurthless.clock.common.brightness import BRIGHTNESS_MAXIMUM_VALUE, BRIGHTNESS_TOTAL_STEPS, decrement_brightness

from wurthless.clock.common.upy import reboot       

def handle_nots(tot):
    tot.cvars().set("config.clock", "")

def handle_factory_reset(tot):
    if promptConfirm(tot.inputs(), tot.display()):
        os.remove("secrets/secrets.ini")
        os.sync()

        tot.display().shutdown()

        reboot()

def handle_sync(tot):
    force_manual = tot.cvars().get("config.clock", "force_manual")

    direct_inputs = tot.inputs()
    display = tot.display()
    inputs = DebouncedInputs(direct_inputs)

    while direct_inputs.strobe():
        pass

    # inputs are inverted because we're prompting the user to turn
    # sync on and off, but sync on disables force_manual and sync off enables it
    response = promptBoolean(display,
                             inputs,
                             message_false=messagesDisplayOn,
                             message_true=messagesDisplayOff,
                             default_selection=force_manual)

    if promptConfirm(direct_inputs, display):
        tot.cvars().set("config.clock", "force_manual", response)
        tot.cvars().save()

        # display "DONE"
        messagesDisplayDone(display)
        while direct_inputs.strobe():
            pass

def handle_net(tot):
    net_enabled = tot.cvars().get("config.nic", "enable")

    direct_inputs = tot.inputs()
    display = tot.display()
    inputs = DebouncedInputs(direct_inputs)

    while direct_inputs.strobe():
        pass

    response = promptBoolean(display,
                             inputs,
                             message_false=messagesDisplayOff,
                             message_true=messagesDisplayOn,
                             default_selection=net_enabled)

    if promptConfirm(direct_inputs, display):
        tot.cvars().set("config.nic", "enable", response)
        tot.cvars().save()

        # display "DONE"
        messagesDisplayDone(display)
        while direct_inputs.strobe():
            pass

def handle_12hr(tot):
    is_12hr = tot.cvars().get("config.clock", "display_12hr_time")

    direct_inputs = tot.inputs()
    display = tot.display()
    inputs = DebouncedInputs(direct_inputs)

    while direct_inputs.strobe():
        pass
    
    response = promptBoolean(display,
                             inputs,
                             message_false=messagesDisplayOff,
                             message_true=messagesDisplayOn,
                             default_selection=is_12hr)

    if promptConfirm(direct_inputs, display):
        tot.cvars().set("config.clock", "display_12hr_time", response)
        tot.cvars().save()

        # display "DONE"
        messagesDisplayDone(display)
        while direct_inputs.strobe():
            pass


def nop(tot):
    pass

def config_mode(tot: ToT):
    direct_inputs = tot.inputs()
    display = tot.display()
    inputs = DebouncedInputs(direct_inputs)

    has_nic = tot.nic() is not None

    items = [
        messagesDisplaySyncMenuItem,
        messagesDisplayNet if has_nic else None,
        messagesDisplay12Hr,
        messagesDisplayFact,
    ]

    handlers = [
        handle_sync,
        handle_net,
        handle_12hr,
        handle_factory_reset
    ]


    last_selection = 0
    while True:
        display.blank()
        while direct_inputs.strobe():
            pass

        last_selection = promptMenu(display, inputs, items, last_selection)
        handlers[last_selection](tot)
