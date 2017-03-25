# Whisper is a library for anonymous communication between two nodes on a network

import sys
import time
import socket
import random
import os
from server import init_server
from util import printc, CHRS, style
from thread import start_new_thread

KEYS = []

def main():
    global KEYS
    
    printc("\n    ~~whisper a.3", style.bold)
    printc(  "  silent communication\n", style.bold, style.purple)
    printc("Legal Disclaimer: It is the end user's responsibility to obey all local, state, and federal laws. The developer assumes no liability for any misuse or damages caused by this software.\n\n", style.yellow)
    
    listen = False
    verbose = False
    serve = False
    
    their_addr = ''
    port = 9504
    destport = 9504
    keyfile = 'whisp'
    
    gen_file = ''
    gen_num = 100000
    gen_len = 1024
    
    mod_file = ''
    filt = ''
    out_filt = ''
    i = 1
    
    if len(sys.argv) < 2:
        help()
        return
    
    while i < len(sys.argv):
        o = sys.argv[i]
        if o == "-h" or o == "--help":
            help()
            return
        elif o == "--listen":
            listen = True
        elif o == "--serve":
            serve = True
        elif o == "-s":
            filt = sys.argv[i + 1]
            i += 1
        elif o == '-d':
            their_addr = sys.argv[i + 1]
            i += 1
        elif o == '-w':
            keyfile = sys.argv[i + 1]
            i += 1
        elif o == '-p':
            port = int(sys.argv[i + 1])
            i += 1
        elif o == '-dp':
            destport = int(sys.argv[i + 1])
            i += 1
        elif o == '-g':
            gen_file = sys.argv[i + 1]
            i += 1
        elif o == '-m':
            gen_file = sys.argv[i + 1]
            i += 1
        elif o == '-f':
            out_filt = sys.argv[i + 1]
            i += 1
        elif o == '-k':
            gen_num = int(sys.argv[i + 1])
            i += 1
        elif o == '-l':
            gen_len = int(sys.argv[i + 1])
            i += 1
        elif o == '-v':
            verbose = True
        else:
            printc("Warning: Ignoring unknown parameter %s" % o, style.yellow)
        i += 1
    
    if gen_file != '':
        generate(gen_num, gen_len, gen_file, filt=out_filt, verbose=verbose)
    elif mod_file != '':
        modify(mod_file, filt=out_filt, verbose=verbose)
    
    load_keys(keyfile, verbose=verbose)
    
    if serve:
        init_server(port, KEYS, tencrypt, tdecrypt, getdate, their_addr, destport, filt)
    elif listen:
        dolisten(port, filt=filt, verbose=verbose)
    else:
        do_chat(their_addr, destport, filt=filt, verbose=verbose)

def modify(filename, filt='', verbose=False):
    global CHRS
    
    apath = os.path.abspath(filename)
    if verbose:
        printc("Modifying %s with new filter ..." % apath, style.blue)
    
    if filt == '':
        return
    
    lines = []
    cl, fl = len(CHRS), len(filt)
    
    if verbose:
        printc("Sanitizing..." % apath, style.blue)
    
    with open(apath, "r") as obj:
        lines = obj.read().split("\n")
        
        for i, line in enumerate(lines):
            for j, c in enumerate(line):
                lines[i][j] = (CHRS.index(c) + CHRS.index(filt[j % fl])) % cl
    
    if verbose:
        printc("Writing new sanitization to file..." % apath, style.blue)
    
    with open(apath, "w+") as obj:
        obj.write('\n'.join(lines))

def dolisten(port, filt='', verbose=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if verbose:
        printc("Attempting to bind server socket to localhost...", style.blue)
    
    try:
        sock.bind(('', port))
    except:
        printc("Error: Could not bind server socket to localhost. Perhaps a zombie process is already running?", style.bold, style.highlightred)
        exit(1)
    
    if verbose:
        printc("Successfully bound socket to localhost...", style.green)
    
    start_new_thread(log_chat, (sock, verbose, filt))
    _receive_message(sock, verbose=verbose)

def log_chat(sock, verbose=False, filt=''):
    last_count = 0
    
    printc("Listening...", style.bold)
    
    while True:
        if not os.path.exists("log"):
            with open("log", "w+") as obj:
                obj.write("")
        
        with open("log", "r") as obj:
            lines = obj.read().split("\n")
            llen = len(lines)
            
            if llen != last_count:
                for i in range(last_count, llen):
                    if lines[i].replace(' ', '') == '':
                        continue
                    log_message(tdecrypt(lines[i], filt=filt))
                last_count = llen
        
        time.sleep(3)

def log_message(m):
    print(m)

def do_chat(addr, dport, filt='', verbose=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if verbose:
        printc("Connecting to %s:%d ..." % (addr, dport), style.blue)
    
    sock.connect((addr, dport))
    
    if verbose:
        printc("Successfully connected to %s:%d" % (addr, dport), style.bold, style.green)
    
    while True:
        m = raw_input(style.bold + "Message: \033[0m")
        _send_message(sock, m, filt=filt, verbose=verbose)

def write_message(addr, m, filt=''):
    ip = "[%s]" % addr[0] if addr[1] == 0 else "[%s:%d]" % (addr[0], addr[1])
    
    if not os.path.exists("log"):
        with open("log", "w+") as obj:
            obj.write("")
    
    with open("log", "a") as obj:
        obj.write("\n" + tencrypt("%s %s" % (ip, m), filt=filt))

def client_thread(conn, addr):
    buffer = []
    
    while True:
        data = conn.recv(8192)
        if not data:
            break
        
        write_message(addr, data)
    
    printc("Client [%s:%d] has dropped their connection" % (addr[0], addr[1]), style.red)
    
    conn.close()

def _receive_message(sock, verbose=False):
    sock.listen(5)
    
    while True:
        conn, addr = sock.accept()
        if verbose:
            printc("Client %s:%d has connected and may or may not be able to read and send messages" % (addr[0], addr[1]), style.blue)
        
        start_new_thread(client_thread, (conn, addr))
    
    conn.close()

def _send_message(sock, m, filt='', verbose=False):
    try:
        sock.send(m)
        write_message(('localhost', 0), m, filt=filt)
        if verbose:
            printc("Message sent successfully", style.green)
    except:
        if verbose:
            printc("Error: Message failed to send. Retrying...", style.highlightred)
        return _send_message(sock, m, verbose=verbose)

def do_listen(verbose=False):
    pass

def help():
    print("Usage: python whisper.py [options]                         ")
    print("                                                           ")
    print("  ~~All in One                                             ")
    print("       --serve        Create a server for GUI interaction  ")
    print("                                                           ")
    print("  ~~Main Options                                           ")
    print("       -d their_addr  IP address I'm communicating with    ")
    print("       -dp their_port Port I'm communicating over          ")
    print("       -p PORT        What communication port to use       ")
    print("       -w FILE        File to load one-time-pads from      ")
    print("       -s IN_FILTER   De-sanitize all keys with a filter   ")
    print("       -v             Verbose mode                         ")
    print("                                                           ")
    print("  ~~Watching the Chat                                      ")
    print("       --listen       Listen and log the chat              ")
    print("                                                           ")
    print("  ~~Maintaining Security                                   ")
    print("       -g FILE        Generate keys and write to file      ")
    print("       -k KEYS        Number of one-time-pads to generate  ")
    print("       -l LENGTH      Length of each one-time-pad          ")
    print("                                                           ")
    print("       -m FILE        Modify a key file that already exists")
    print("       -f OUT_FILTER  Sanitize all keys with a filter      ")
    print("                                                           ")

def load_keys(filename, verbose=False):
    global KEYS
    if verbose:
        printc("Loading one-time-pads from %s" % (os.path.abspath(filename)), style.blue)
    
    with open(os.path.abspath(filename), "r") as obj:
        KEYS = obj.read().split("\n")
    
    printc("Successfully loaded keys", style.bold)

# Generates a list of K keys with length N and stores them in a file
def generate(K, N, filename, filt='', verbose=False):
    apath = os.path.abspath(filename)
    if verbose:
        printc("Writing %d keys of length %d to %s" % (K, N, apath), style.blue)
    
    r = [gen_str(N, filt=filt) for i in range(K)]
    
    with open(apath, "w+") as obj:
        obj.write('\n'.join(r))

# Generates a random string with length 'l'
def gen_str(l, filt=''):
    global CHRS
    
    r, cl = "", len(CHRS)
    for i in range(l):
        ind = int(random.random() * cl)
        if filt != '':
            ind += CHRS.index(filt[i % len(filt)])
        r += CHRS[ind % cl]
    
    return r

def tencrypt(m, filt=''):
    global KEYS
    
    kl = len(KEYS)
    
    T = int(time.time() * 10000)
    P = encrypt("{:014d}".format(T), KEYS[-1], filt=filt)
    r = P + encrypt(m, KEYS[T % kl], filt=filt)
    return r

def getdate(m, filt=''):
    global KEYS
    if m == '':
        return 0
    
    kl = len(KEYS)
    return int(decrypt(m[:14], KEYS[-1], filt=filt))

def tdecrypt(m, filt=''):
    global KEYS
    
    kl = len(KEYS)
    
    T = int(decrypt(m[:14], KEYS[-1], filt=filt))
    r = decrypt(m[14:], KEYS[T % kl], filt=filt)
    
    return r

def encrypt(m, k, filt=''):
    global CHRS
    cl, kl, fl = len(CHRS), len(k), len(filt)
    
    if m == "":
        return m
    r = ""
    
    for i, c in enumerate(m):
        a = CHRS.index(c)
        b = CHRS.index(k[i % kl])
        c = CHRS.index(filt[i % fl]) if filt != '' else 0
        
        r += CHRS[unmod(a + (b - c), cl)]
    
    return r

def decrypt(m, k, filt=''):
    global CHRS
    cl, kl, fl = len(CHRS), len(k), len(filt)
    
    if m == "":
        return m
    r = ""
    
    for i, c in enumerate(m):
        a = CHRS.index(c)
        b = CHRS.index(k[i % kl])
        c = CHRS.index(filt[i % fl]) if filt != '' else 0
        
        r += CHRS[unmod(a - (b - c), cl)]
    
    return r

def unmod(value, length):
    if value >= 0:
        return value % length
    else:
        return length - ((-value) % length)

# Begin
main()