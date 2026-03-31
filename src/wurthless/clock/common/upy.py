'''
Common Micropython-specific code and fallbacks if not running under Micropython.
'''

RUNNING_UNDER_UPY = False

try:
    from micropython import const
    import machine

    RUNNING_UNDER_UPY = const(True)
except:
    pass

def make_const(x):
    if RUNNING_UNDER_UPY:
        return const(x)
    return x

def reboot():
    if RUNNING_UNDER_UPY:
        # never returns
        machine.reset()
    else:
        print("reboot called but we're not in micropython land, so i'm not doing anything.")
