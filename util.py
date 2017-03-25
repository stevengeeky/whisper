# Basic util

CHRS = "`1234567890-=~!@#$%^&*()_+qwertyuiop[]\\QWERTYUIOP{}|asdfghjkl;'ASDFGHJKL:\"zxcvbnm ,./ZXCVBNM<>?"

def encode(m):
    global CHRS
    r = ""
    
    for c in m:
        r += "%d#" % CHRS.index(c)
    
    return r

def decode(m):
    global CHRS
    r = ""
    
    while "#" in m:
        r += CHRS[int(m[:m.index("#")])]
        m = m[m.index("#") + 1:]
    
    return r

def printc(message, *modifiers, **options):
    start = ""
    end = "\033[0m"
    newline = bool(options["newline"]) if "newline" in options else True
    
    for m in modifiers:
        start += m
    
    if newline:
        print("%s%s%s" % (start, message, end))
    else:
        print("%s%s%s" % (start, message, end)),

class style:
    bold = "\033[1m"
    italic = "\033[3m"
    underline = "\033[4m"
    highlight = "\033[7m"
    slash = "\033[9m"
    darkgray = "\033[30m"
    darkred = "\033[31m"
    darkgreen = "\033[32m"
    darkyellow = "\033[33m"
    darkblue = "\033[34m"
    darkpurple = "\033[35m"
    darkcyan = "\033[36m"
    highlightgray = "\033[40m"
    highlightred = "\033[41m"
    highlightgreen = "\033[42m"
    highlightyellow = "\033[43m"
    highlightblue = "\033[44m"
    highlightpurple = "\033[45m"
    highlightcyan = "\033[46m"
    gray = "\033[90m"
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    blue = "\033[94m"
    purple = "\033[95m"
    cyan = "\033[96m"
