#
# HTTP webserver and REST endpoint.
# Requires Microdot to run.
#

from microdot import Microdot,send_file
from wurthless.clock.common.upy import RUNNING_UNDER_UPY, reboot as _reboot

GIT = "undefined"
try:
    import git
    GIT = git.GIT
except:
    pass

if RUNNING_UNDER_UPY:
    import machine
    from machine import Pin,PWM

server = Microdot()


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
    if l[0] in [ '\u0021',  '\u0023',  '\u003B', '\u0020' ]:
        return False
    
    for i in l:
        if (i == '\u0020' or \
             i == '\u0021' or \
             i == '\u0023' or \
             ('\u0025' <= i and i <= '\u002A') or \
             ('\u002C' <= i and i <= '\u003E') or \
             ('\u0040' <= i and i <= '\u005A') or \
             ('\u005E' <= i and i <= '\u007E')) is False:
            return False
        
    # catch trailing space
    if l[len(l)-1] == '\u0020':
        return False
    
    return True

def _client_supports_gzip(request):
    headers = request.headers
    if "Accept-Encoding" not in headers:
        return False
    return "gzip" in headers["Accept-Encoding"]

@server.get('/index.html')
async def indexhtml(request):
    if _client_supports_gzip(request):
        return send_file("www/index.html.gz", content_type="text/html", content_encoding="gzip")
    return send_file("www/index.html")

@server.get('/')
async def index(request):
    if _client_supports_gzip(request):
        return send_file("www/index.html.gz", content_type="text/html", content_encoding="gzip")
    return send_file("www/index.html")

@server.get('/rest/settings')
async def settingsGet(request):
    # do NOT send password back to the client, ever. EVER.
    return {
        'wifi_ap_name': g_tot.cvars().get("config.nic","wifi_ap_name"),
        'dst_active': g_tot.cvars().get("config.clock","dst_active"),
        'dst_disable': g_tot.cvars().get("config.clock","dst_disable"),
        'utc_offset_seconds': g_tot.cvars().get("config.clock","utc_offset_seconds"),
        'dst_is_dipswitch': g_tot.inputs().is_dst_dipswitch(),
        'display_12hr_time': g_tot.cvars().get("config.clock", "display_12hr_time"),
        'git': GIT
    },200

@server.get('/rest/reboot')
async def reboot(request):
    request.app.shutdown()
    return ''

@server.post('/rest/settings')
async def settingsPost(request):
    restdata = request.json
    if restdata is None:
        return {
            'result': 'error',
            'message': 'no-post-data'
        },400

    dst_is_dipswitch = g_tot.inputs().is_dst_dipswitch()

    required_fields = [ 'wifi_ap_name', 'wifi_ap_password', 'utc_offset_seconds', 'display_12hr_time' ]

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
    display_12hr_time = restdata['display_12hr_time']
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

    g_tot.cvars().set("config.nic","wifi_ap_name", ap_name )
    g_tot.cvars().set("config.nic","wifi_ap_password", ap_password )
    g_tot.cvars().set("config.clock","utc_offset_seconds", utc_offset_seconds)
    if dst_is_dipswitch is False:
        g_tot.cvars().set("config.clock","dst_disable", dst_disable)
        g_tot.cvars().set("config.clock","dst_active", dst_active)

    g_tot.cvars().set("config.clock", "display_12hr_time", display_12hr_time)

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
        if status_pin != -1 and RUNNING_UNDER_UPY is True:
            PWM(Pin(status_pin,Pin.OUT), freq=1, duty=512)

    # set to true to debug statistics on micropython.
    # very important for diagnosing memory crunch issues that cause the webserver to lock up
    if RUNNING_UNDER_UPY:
        import gc
        gc.collect()
        print(f"{gc.mem_alloc()} bytes wired, {gc.mem_free()} bytes free")

    server.run(port=80)
    _reboot()
