#
# HTTP webserver and REST endpoint.
# Requires Microdot to run.
#

from microdot import Microdot,send_file
from wurthless.clock.cvars.cvars import registerCvar

global running_under_upy
try:
    import machine
    from machine import Pin,PWM
    running_under_upy = True
except:
    running_under_upy = False

server = Microdot()

registerCvar(u"wurthless.clock.webserver", u"disable_display_when_serving", u"Boolean", u"If True, shutdown display driver while running server. Default is False.", False)
registerCvar(u"wurthless.clock.webserver", u"server_active_pin", u"Int", u"I/O pin that will be pulled high when server mode is active. Default is -1 (disable).", -1)

# unfortunately, we have to store the ToT as a global...
global g_tot

#
# from https://www.cisco.com/assets/sol/sb/WAP321_Emulators/WAP321_Emulator_v1.0.0.3/help/Wireless05.html:
# - string length must be 2-32 characters
# - allowable characters are: ASCII 0x20, 0x21, 0x23, 0x25 through 0x2A, 0x2C through 0x3E, 0x40 through 0x5A, 0x5E through 0x7E. 
# - trailing and leading spaces are not permitted
# - string cannot start with 0x21, 0x23, 0x3B
#
def validateWifiAccessPointName(string):
    l = list(string)
    if ( 2 <= len(l) and len(l) <= 32) is False:
        return False

    # also catches precisely one leading space
    if l[0] in [ u'\u0021',  u'\u0023',  u'\u003B', u'\u0020' ]:
        return False
    
    for i in l:
        if (i == u'\u0020' or \
             i == u'\u0021' or \
             i == u'\u0023' or \
             (u'\u0025' <= i and i <= u'\u002A') or \
             (u'\u002C' <= i and i <= u'\u003E') or \
             (u'\u0040' <= i and i <= u'\u005A') or \
             (u'\u005E' <= i and i <= u'\u007E')) is False:
            return False
        
    # catch trailing space
    if l[len(l)-1] == u'\u0020':
        return False
    
    return True

@server.get('/index.html')
async def indexhtml(request):
    return send_file(u"www/index.html")

@server.get('/')
async def index(request):
    return send_file(u"www/index.html")

@server.get('/cfg.js')
async def cfgjs(request):
    return send_file(u"www/cfg.js")

@server.get('/cfg.css')
async def cfgcss(request):
    return send_file(u"www/cfg.css")

@server.get('/rest/settings')
async def settingsGet(request):
    # do NOT send password back to the client, ever. EVER.
    return {
        'wifi_ap_name': g_tot.cvars().get(u"config.nic",u"wifi_ap_name"),
        'dst_active': g_tot.cvars().get(u"config.clock",u"dst_active"),
        'dst_disable': g_tot.cvars().get(u"config.clock",u"dst_disable"),
        'utc_offset_seconds': g_tot.cvars().get(u"config.clock",u"utc_offset_seconds"),
        'dst_is_dipswitch': g_tot.inputs().is_dst_dipswitch()
    },200

@server.get('/rest/reboot')
async def reboot(request):
    if running_under_upy:
        # never returns
        machine.reset()
    else:
        print("reboot called but we're not in micropython land, so i'm not doing anything.")

    return {},200

@server.post('/rest/settings')
async def settingsPost(request):
    restdata = request.json
    if restdata is None:
        return {
            'result': 'error',
            'message': 'no-post-data'
        },400

    dst_is_dipswitch = g_tot.inputs().is_dst_dipswitch()

    required_fields = [ 'wifi_ap_name', 'wifi_ap_password', 'utc_offset_seconds' ]

    if dst_is_dipswitch is False:
        required_fields += [ 'dst_active', 'dst_disable' ]

    for f in required_fields:
        if f not in restdata:
            return {
                'result': 'error',
                'message': 'missing-required-field'
            }, 400

    ap_name = restdata['wifi_ap_name']
    ap_password = restdata['wifi_ap_password']
    utc_offset_seconds = restdata['utc_offset_seconds']
    if dst_is_dipswitch is False:
        dst_active = restdata['dst_active']
        dst_disable = restdata['dst_disable']

    if validateWifiAccessPointName(ap_name) is False:
        return {
            'result': 'error',
            'message': 'bad-ap-name'
        }, 400

    # check datatypes
    # dst_active/dst_disable must be booleans
    # utc_offset_seconds must be int
    # ap_name/ap_password must be strings

    g_tot.cvars().set(u"config.nic",u"wifi_ap_name", ap_name )
    g_tot.cvars().set(u"config.nic",u"wifi_ap_password", ap_password )
    g_tot.cvars().set(u"config.clock",u"utc_offset_seconds", utc_offset_seconds)
    if dst_is_dipswitch is False:
        g_tot.cvars().set(u"config.clock",u"dst_disable", dst_disable)
        g_tot.cvars().set(u"config.clock",u"dst_active", dst_active)

    g_tot.cvars().save()

    return {
        'result': 'success',
        'message': 'settings-saved'
    }, 200

def serverMain(tot):
    tot.nic().initAsServer()
    global g_tot
    g_tot = tot

    # on ESP32 (probably other boards) where the display is driven through software
    # there will not be enough CPU time to update the display and handle server logic
    if tot.cvars().get("wurthless.clock.webserver", "disable_display_when_serving") is True:
        tot.display().blank()
        tot.display().shutdown()

        status_pin = tot.cvars().get("wurthless.clock.webserver", "server_active_pin")
        if status_pin != -1 and running_under_upy is True:
            PWM(Pin(status_pin,Pin.OUT), freq=1, duty=512)

    server.run(port=80)
