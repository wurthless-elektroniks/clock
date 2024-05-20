
def unpackBcd(a,b):
    buf = [ 0,0,0,0 ]
    buf[1] = int(a % 10)
    buf[0] = int((a - buf[1]) / 10)
    buf[3] = int(b % 10)
    buf[2] = int((b - buf[3]) / 10)
    return buf