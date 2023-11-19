#
# HTTP webserver stuff.
#
# GET /     - displays configuration form.
# POST /sub - sends configuration data.
#
# Requires Microdot to run, though this dependency will probably be removed in the future
#

from microdot import Microdot

server = Microdot()

# unfortunately, we have to store the ToT as a global...
global g_tot

utc_offsets = [
    [ u"UTC-12:00", int(-12 * 3600) ],
    [ u"UTC-11:00", int(-11 * 3600) ],
    [ u"UTC-10:00", int(-10 * 3600) ],
    [ u"UTC-09:30", int(-9.5 * 3600) ],
    [ u"UTC-09:00", int(-9 * 3600) ],
    [ u"UTC-08:00", int(-8 * 3600) ],
    [ u"UTC-07:00", int(-7 * 3600) ],
    [ u"UTC-06:00", int(-6 * 3600) ],
    [ u"UTC-05:00", int(-5 * 3600) ],
    [ u"UTC-04:00", int(-4 * 3600) ],
    [ u"UTC-03:30", int(-3.5 * 3600) ],
    [ u"UTC-03:00", int(-3 * 3600) ],
    [ u"UTC-02:00", int(-2 * 3600) ],
    [ u"UTC-01:00", int(-1 * 3600) ],
    [ u"UTC",       int(0) ],
    [ u"UTC+01:00", int(1 * 3600) ],
    [ u"UTC+02:00", int(2 * 3600) ],
    [ u"UTC+03:00", int(3 * 3600) ],
    [ u"UTC+03:30", int(3.5 * 3600) ],
    [ u"UTC+04:00", int(4 * 3600) ],
    [ u"UTC+04:30", int(4.5 * 3600) ],
    [ u"UTC+05:00", int(5 * 3600) ],
    [ u"UTC+05:30", int(5.5 * 3600) ],
    [ u"UTC+05:45", int(5.75 * 3600) ],
    [ u"UTC+06:00", int(6 * 3600) ],
    [ u"UTC+06:30", int(6.5 * 3600) ],
    [ u"UTC+07:00", int(7 * 3600) ],
    [ u"UTC+08:00", int(8 * 3600) ],
    [ u"UTC+08:45", int(8.75 * 3600) ],
    [ u"UTC+09:00", int(9 * 3600) ],
    [ u"UTC+09:30", int(9.5 * 3600) ],
    [ u"UTC+10:00", int(10 * 3600) ],
    [ u"UTC+10:30", int(10.5 * 3600) ],
    [ u"UTC+11:00", int(11 * 3600) ],
    [ u"UTC+12:00", int(12 * 3600) ],
    [ u"UTC+12:45", int(12.75 * 3600) ],
    [ u"UTC+13:00", int(13 * 3600) ],
    [ u"UTC+14:00", int(14 * 3600) ],
]

def generateUtcOffsetList():
    items = []
    current_timezone = g_tot.cvars().get(u"config.clock",u"utc_offset_seconds")

    for i in utc_offsets:
        if i[1] == current_timezone:
            items.append(u"""<option value="%d" selected="selected">%s</option>"""%(i[1],i[0]))
        else:
            items.append(u"""<option value="%d">%s</option>"""%(i[1],i[0]))

    return u"""<select name="utcoffset" id="utcoffset">"""+u"".join(items)+u"</select>"

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
        print(u"validateWifiAccessPointName(): too long")
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

def generateWifiAccessPoint():
    ap_name = g_tot.cvars().get(u"config.nic",u"wifi_ap_name" )
    if validateWifiAccessPointName(ap_name) is False:
        ap_name = u""

    return u"""<input type="text" id="ap_name" name="ap_name" value="%s"/>""" % (ap_name)

def generateWifiPassword():
    return u"""<input type="password" id="ap_password" name="ap_password"/>"""

def generateDstSelection():
    dst_disable = g_tot.cvars().get(u"config.clock",u"dst_disable")
    dst_active = g_tot.cvars().get(u"config.clock",u"dst_active")

    dst_off_item = u"""<input type="radio" id="dst_off" name="dst" value="off" checked />""" if dst_disable is False and dst_active is False else u"""<input type="radio" id="dst_off" name="dst" value="off" />"""
    dst_on_item = u"""<input type="radio" id="dst_on" name="dst" value="on" checked />""" if dst_disable is False and dst_active is True else u"""<input type="radio" id="dst_on" name="dst" value="on" />"""
    dst_disable_item = u"""<input type="radio" id="dst_disable" name="dst" value="disable" checked />""" if dst_disable is True else u"""<input type="radio" id="dst_disable" name="dst" value="disable" />"""

    return u"""
    %s
    <label for="dst_off">off</label>
    %s
    <label for="dst_on">on</label>
    %s
    <label for="dst_disable">disable dst</label>
    """%(dst_off_item,dst_on_item,dst_disable_item)

@server.route('/')
def index(request):
    return u"""
    <html>
    <head>
    <title>the most useless clock in the world - config mode</title>
    </head>
    <body>
    <h1>the most useless clock in the world - configuration mode</h1>
    <p><i>presented in glorious 1998-era html because i am too lazy to write something modern</i></p>
    <p>please enter details that i will be selling to russian hackers for $10 a pop:</p>
    <form action="/sub" method="post">
    <table>
    <tr>
    <td>wifi accesspoint</td>
    <td>"""+generateWifiAccessPoint()+"""</td>
    </tr>
    <tr>
    <td>wifi password</td>
    <td>"""+generateWifiPassword()+"""</td>
    </tr>
    <tr>
    <td>timezone</td>
    <td>"""+generateUtcOffsetList()+"""</td>
    </tr>
    <tr>
    <td>dst adjust</td>
    <td>"""+generateDstSelection()+"""</td>
    </tr>
    </table>
    <p><b>please note:</b> your wifi network must be accessible over the 2.4 GHz band. unfortunately, i can't provide a dropdown of available wifi networks because of technical limitations.</p>
    <button action="submit">save settings</button>
    </form>
    </body>
    </html>
    """, 200, {'Content-Type': 'text/html'}

@server.route('/sub', methods=['POST'])
def sub(request):
    ap_name = request.form.get('ap_name')
    ap_password = request.form.get('ap_password')
    dst = request.form.get('dst')
    utcoffset = request.form.get('utcoffset')

    if ap_name is None or ap_name == u"" or ap_password is None or ap_password == u"" or dst is None or utcoffset is None:
        return u"""
        <html>
        <head>
        <title>oops</title>
        </head>
        <body>
        <h1>required field not set</h1>
        <p>all fields must be filled out. try again!!!</p>
        </body>
        </body>
        </html>
        """, 401, {'Content-Type': 'text/html'}
    
    # HTTP POST sucks and always replaces whitespace with + so handle that first.
    ap_name = ap_name.replace("+", " ")

    if validateWifiAccessPointName(ap_name) is False:
        return u"""
        <html>
        <head>
        <title>oops</title>
        </head>
        <body>
        <h1>your wifi accesspoint name sucks</h1>
        <p>according to <a href=https://www.cisco.com/assets/sol/sb/WAP321_Emulators/WAP321_Emulator_v1.0.0.3/help/Wireless05.html">this handy document</a>, your wifi accesspoint name is invalid. more specifically:<p>
        <ul>
        <li>the SSID must be between 2 and 32 characters long</li>
        <li>it can't start or end with whitespace</li>
        <li>it can't contain the characters: ?, ", $, [, \, ], and +</li>
        <li>it can't start with the characters: !, # and ;</li>
        <li>it has to be ASCII characters only (whatever the hell that means, i don't know, i'm not a technically apt person)</li>
        </ul>
        <p>go back and fix it and maybe i'll let you by.</p>
        <p>by the way, for debugging purposes, this is what you entered: %s</p>
        </body>
        </body>
        </html>
        """%(ap_name), 401, {'Content-Type': 'text/html'}

    g_tot.cvars().set(u"config.nic",u"wifi_ap_name", str(ap_name) )
    g_tot.cvars().set(u"config.nic",u"wifi_ap_password", str(ap_password) )
    g_tot.cvars().set(u"config.clock",u"dst_disable", dst == u"disable")
    g_tot.cvars().set(u"config.clock",u"dst_active", dst == u"on" )
    g_tot.cvars().set(u"config.clock",u"utc_offset_seconds", int(utcoffset) )

    g_tot.cvars().save()

    return u"""
    <html>
    <head>
    <title>stuff happened</title>
    </head>
    <body>
    <h1>hooray, settings saved successfully</h1>
    <p>please reboot your clock by pressing RESET. if you need to reconnect to this config page, hold SET while pressing RESET.</p>
    </body>
    </body>
    </html>
    """, 200, {'Content-Type': 'text/html'}

def serverMain(tot):
    tot.nic().initAsServer()
    global g_tot
    g_tot = tot
    server.run(port=80)
