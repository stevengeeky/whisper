# Server
# WARNING: serving a webpage on a filtered port is visible to port 
# scanners, be careful!

import socket
import os
import random
import time
import select
from thread import start_new_thread
from util import printc, style

KEYS = []
gport = 0
tencrypt = None
tdecrypt = None
getdate = None
filt = ''
dest = ''
destport = 0

remembrances = dict()
sent_remembrances = dict()

all_messages = []

def init_server(port, K=[], _tencrypt=None, _tdecrypt=None, _getdate=None, _dest='', _destport=0, _filt=''):
    global KEYS, tencrypt, tdecrypt, filt, dest, destport, gport, getdate
    gport = port
    KEYS = K
    tencrypt = _tencrypt
    tdecrypt = _tdecrypt
    getdate = _getdate
    filt = _filt
    dest = _dest
    destport = _destport
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    sock.bind(("localhost", 80))
    
    printc("Established server on %s:%d" % ("localhost", 80), style.bold, style.blue)
    
    sock.listen(1)
    
    # Message port
    msock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    msock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    host = '0.0.0.0'
    hport = port
    
    msock.bind((host, hport))
    
    printc("Filtered receive port established on %s:%d" % (host, hport), style.bold, style.blue)
    
    msock.listen(1)
    
    wait_for_connections([sock, msock])

def header(options=dict()):
    code = options["code"] if "code" in options else 200
    message = options["message"] if "message" in options else "OK"
    contenttype = options["content-type"] if "content-type" in options else "text/html"
    content = options["content"] if "content" in options else ""
    
    top = "%s %d %s" % ("HTTP/1.1", code, message)
    
    headers = {
        "Content-Type": contenttype,
        "Content-Length": len(content)
    }
    
    if "Access-Control-Allow-Origin" in options:
        headers["Access-Control-Allow-Origin"] = options["Access-Control-Allow-Origin"]
    
    head = (top + '\n') + '\n'.join("%s: %s" % (o[0], o[1]) for o in headers.iteritems())
    
    return head + '\n\n'

def get_file(filename):
    last = filename[:filename.rindex("/") + 1] if "/" in filename else filename
    while last.startswith(' ') or last.startswith('\t'):
        last = last[1:]
    
    if last.lower() in ['whisper.py', 'server.py', 'util.py'] or last.startswith('_'):
        return None
    else:
        text = ''
        with open(filename, "r") as obj:
            text = obj.read()
        
        return text

def request(conn, method, url, data):
    while url.startswith("/"):
        url = url[1:]
    
    noop_url = url[:url.index('?')] if '?' in url else url
    first_dir = noop_url[:noop_url.index('/')] if '/' in noop_url else noop_url
    
    if method == 'get':
        if first_dir == 'css':
            message = get_file(os.path.abspath('index.html'))
            if message != None:
                head = header({ 'content': message })
                
                conn.send(head)
                conn.send(message)
        elif first_dir == 'images' and first_dir != noop_url:
            d = _get_messages()
            head = header({ 'content': d })
            
            conn.send(head)
            conn.sendall(d)
    elif method == 'post':
        if first_dir == 'scripts' and first_dir != noop_url:
            queue_send(data)
            
            try:
                m = 'gf'
                conn.send(header({ 'content': m }))
                conn.send(m)
            except:
                pass
    
    try:
        conn.close()
    except:
        pass

def queue_send(data):
    global dest, destport, filt
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    sock.connect((dest, destport))
    sock.send(data)
    
    _write_message(data)

def _write_message(m):
    global filt, all_messages, getdate, remembrances
    
    gd = str(getdate(m, filt=filt))
    if gd in remembrances:
        return
    remembrances[gd] = True
    
    all_messages.append(tencrypt(m, filt=filt))

def _get_messages():
    global all_messages
    
    return '\n'.join(all_messages)

def client_thread(conn, addr):
    data = conn.recv(2048)
    
    if not data:
        conn.close()
        return
    
    if not data.startswith('GET') and not data.startswith('POST'):
        _write_message(data)
        try:
            m = 'gf'
            conn.send(header({ 'content': m }))
            conn.send(m)
            
            conn.close()
        except:
            pass
    else:
        lines = data.split("\n")
        main = lines[0].split(" ")
        
        method, url = main[0].lower(), main[1].lower()
        d = ''
        
        if '\n\n' in data:
            d = data[data.index('\n\n') + 2:]
        elif '\r\n\r\n' in data:
            d = data[data.index('\r\n\r\n') + 4:]
        
        request(conn, method, url, d)

def foreign_thread(conn, addr):
    data = conn.recv(2048)
    
    if not data:
        conn.close()
    
    _write_message(data)
    conn.close()

def wait_for_connections(socks):
    while True:
        ready,_,_ = select.select(socks, [], [])
        
        for sock in ready:
            conn, addr = sock.accept()
            if socket.gethostbyname(addr[0]) != "127.0.0.1":
                start_new_thread(foreign_thread, (conn, addr))
            else:
                start_new_thread(client_thread, (conn, addr))