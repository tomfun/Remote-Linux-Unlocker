# -*- coding: utf-8 -*-
import socket, sys, json, subprocess, os

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True


def is_locked():
    # Method 1: Check loginctl sessions
    # try:
    #     p = subprocess.Popen(['loginctl', 'list-sessions', '--no-legend'],
    #                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     output, _ = p.communicate()
    #     if output:
    #         lines = output.decode('utf-8').strip().split('\n')
    #         for line in lines:
    #             if line.strip():
    #                 session_id = line.split()[0]
    #                 # Check if session is locked
    #                 p2 = subprocess.Popen(['loginctl', 'show-session', session_id, '-p', 'LockedHint'],
    #                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #                 output2, _ = p2.communicate()
    #                 if b'LockedHint=yes' in output2:
    #                     return True
    #                 return False
    # except FileNotFoundError:
    #     pass
    # Method 2: Try gnome-screensaver-command (if available)
    try:
        p = subprocess.Popen(['gnome-screensaver-command', '--query'], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = p.communicate()
        if b'is active' in output:
            return True
    except FileNotFoundError:
        pass
    
    # Method 3: Check for GNOME session lock via dbus (fallback)
    try:
        import os
        if 'DISPLAY' in os.environ: # it must be systemd daemon (not sure user or system). will it work??
            p = subprocess.Popen(['gdbus', 'call', '-e', '-d', 'org.gnome.ScreenSaver', 
                                '-o', '/org/gnome/ScreenSaver', '-m', 'org.gnome.ScreenSaver.GetActive'], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = p.communicate()
            if b'true' in output:
                return True
            return False
    except:
        pass
            
    try:
        users = [i.split(':') for i in open('/etc/shadow').readlines()]
        user = [i[0] for i in users if i[1] not in ('!', '*')][0]
        
        commands = 'su ' + user + ' -c -- "gdbus call -e -d com.canonical.Unity -o /com/canonical/Unity/Session -m com.canonical.Unity.Session.IsLocked"'
        p = subprocess.Popen(commands,stdout=subprocess.PIPE, shell=True)
        if "true" in str(p.communicate()):
            return True
        else:
            return False
    except:
        pass
    # If all methods fail, assume unlocked
    return False

def authenticate_key(key):
    with open(os.path.dirname(os.path.realpath(__file__)) + '/keys.db') as file:
        for line in file:
            if line.strip() == key:
                return True

    return False


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ('', 61599)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection', file=sys.stderr)
    connection, client_address = sock.accept()

    try:
        print('connection from', client_address, file=sys.stderr)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(256).strip().decode('utf-8')
            print('received "%s"' % data, file=sys.stderr)
            if is_json(data):
                data = json.loads(data)
                if data["command"] == "lock" and data["key"] and authenticate_key(data["key"]):
                    print('client requesting lock', file=sys.stderr)
                    exit_code = subprocess.call(["loginctl", "lock-sessions"], timeout=30)
                    if exit_code == 0:
                        connection.sendall(b'{"status":"success"}')
                    else:
                        connection.sendall(b'{"status":"error","message":"Failed to lock sessions"}')
                    break
                elif data["command"] == "unlock" and data["key"] and authenticate_key(data["key"]):
                    print('client requesting unlock', file=sys.stderr)
                    exit_code = subprocess.call(["loginctl", "unlock-sessions"], timeout=30)
                    if exit_code == 0:
                        connection.sendall(b'{"status":"success"}')
                    else:
                        connection.sendall(b'{"status":"error","message":"Failed to unlock sessions"}')
                    break
                elif data["command"] == "status" and data["key"] and authenticate_key(data["key"]):
                    print('client requesting echo', file=sys.stderr)
                    response = '{"status":"success","hostname":"' + socket.gethostname() +  '","isLocked":"' + str(is_locked()) + '"}';
                    print(response, file=sys.stderr)
                    connection.sendall(response.encode('utf-8'))
                    break

            else:
                print('no more data from', client_address, file=sys.stderr)
                break

    finally:
        # Clean up the connection
        connection.close()
