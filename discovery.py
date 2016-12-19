from socket import *
import threading
import json

IS_INIT = False
PORT = 5001
PACKET_SIZE = 1024
VERSION = '1.0'

def process_message(json, sender):
    message_type = json['type']
    if message_type == 'discovery':
        print('Received discovery request from', sender)
        response = { 'type': 'discovered', 'firmware': VERSION }
        response_str = json.dumps(response)
        send_to(sender, response_str)
    return

def receiver():
    print('Listening for discovery requests...')
    server = socket(AF_INET, SOCK_DGRAM)
    server.bind(('', PORT))
    global IS_INIT
    while IS_INIT:
        try:
            packet = server.recvfrom(PACKET_SIZE)
            message = packet[0].decode('utf-8')
            sender_addr = packet[1][0]
            message_json = json.loads(message)
            process_message(message_json, sender_addr)
        except json.decoder.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
    print('Ending discovery visibility!')
    return

THREAD = threading.Thread(target=receiver)

def init_visibility():
    global IS_INIT
    if IS_INIT:
        print('Already listening for discovery requests!')
        return
    IS_INIT = True
    THREAD.start()
    return

def deinit_visibility():
    global IS_INIT
    IS_INIT = False
    return

def send_broadcast(message):
    client = socket(AF_INET, SOCK_DGRAM)
    client.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    client.sendto(bytes(message, 'utf-8'), ('255.255.255.255', PORT))
    return

def send_to(addr, message):
    client = socket(AF_INET, SOCK_DGRAM)
    client.sendto(bytes(message, 'utf-8'), (addr, PORT))
    return
