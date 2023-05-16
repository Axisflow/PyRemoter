import json
import secrets
import socket
import string
import uuid
import threading


def client_handler(conn, addr):
    while True:
        # receive user data length from socket
        size_bytes = conn.recv(4)
        # length of packet
        plen = int.from_bytes(size_bytes, byteorder='little')
        # receive user data with plen size
        msgfromserver = conn.recv(plen)
        # bytes to string to json
        try:
            json_obj = json.loads(msgfromserver.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            continue
        # two field <type> or <status>
        if json_obj.get('type') is not None: # interaction with one another client
            # from user data -> get type to send a packet to another one
            msg_type = json_obj['type']
            # from user data -> get another one id
            uuid2 = json_obj['to']
            if msg_type == 'screen':
                # client2
                # 1.Grab screenshot and uuid1 and uuid2 as image data
                # 1.send to another client
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'MouseEvent':
                # client2
                # 1.Grab mouse and uuid1 and uuid2 as image data
                # 1.send to another client
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'MousePoint':
                # client2
                # 1.Grab mouse(x,y) and uuid1 and uuid2 as image data
                # 1.send to another client
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'Key':
                # client2
                # 1.Grab key and uuid1 and uuid2 as image data
                # 1.send to another client
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'audio':
                # client2
                # 1.Grab audio and uuid1 and uuid2 as image data
                # 1.send to another client
                dict1[uuid2][1].send(msgfromserver)
        else: # interaction with one client
            msg_type = json_obj['status']
            if msg_type == 'GetID':
                # client send:
                # {status:"GetID", mac:<MAC address>}
                # client rece:
                # {status:<"GetIDSuccess"/"GetIDFail">[, id:<ID number>, pwd:<password> reason:<Why Fail?>]}

                # from client data
                mac_data = json_obj['mac']
                if mac_data not in dict2:
                    # generate random user_uuid
                    user_uuid = uuid.uuid4()
                    # mac -> uuid
                    dict2[mac_data] = str(user_uuid)
                    # generate random length of 8 password
                    alphabet = string.ascii_lowercase + string.digits
                    password = ''.join(secrets.choice(alphabet) for i in range(8))
                    # user_uuid -> [mac_data, conn, addr,password,permanent]
                    #                  0        1    2      3         4
                    #
                    dict1[str(user_uuid)] = [mac_data, conn, addr, password, False]
                    # reply message
                    j = {'status': "GetIDSuccess", 'id': str(user_uuid), 'pwd': password}
                else:
                    # Fail
                    # reply message
                    j = {'status': "GetIDFail", 'id': dict2[mac_data], 'pwd': dict1[dict2[mac_data]][3], 'reason': 'mac has one id'}
                # send message
                j = json.dumps(j).encode('utf-8')
                conn.send(j)
            elif msg_type == 'Login':
                # client send:
                # {status:"Login", id:<ID number>, pwd:<old password>}
                # client rece:
                # {status:<"LoginSuccess"/"LoginFail">[, pwd:<new password>, reason:<Why Fail?>]}

                # from client data
                user_uuid = json_obj['id']
                if user_uuid in dict1:
                    if dict1[user_uuid][4] is False:
                        # generate random length of 8 password
                        alphabet = string.ascii_lowercase + string.digits
                        password = ''.join(secrets.choice(alphabet) for i in range(8))
                        # reply message
                        j = {'status': "LoginSuccess", 'pwd': password}
                    elif dict1[user_uuid][4] is True:
                        # reply no new password
                        # reply message
                        j = {'status': "LoginSuccess"}
                else:
                    # Fail
                    # reply message
                    j = {'status': "LoginFail", 'reason': 'id is not exist'}
                # send message
                j = json.dumps(j).encode('utf-8')
                conn.send(j)
            elif msg_type == 'Register':
                # client send:
                # {status:"Register", mac:<MAC address>, id:<ID number>, pwd:<password>, permenant:<True/False>}
                # client rece:
                # {status:<"RegisterSuccess"/"RegisterFail">[, reason:<Why Fail?>]}
                # {"id":"d0d7388e-4fc5-4c31-9db4-58b3bfea0a02","mac":"1C:1B:0D:85:20:0B","permenant":"True","pwd":"um3frfa6","status":"Register"}

                # from client data
                user_uuid = json_obj['id']
                mac_data = json_obj['mac']
                password = json_obj['pwd']
                ispermenant = json_obj['permenant']

                if str(user_uuid) not in dict1:
                    # reply message
                    dict2[mac_data] = str(user_uuid)
                    dict1[str(user_uuid)] = [mac_data, conn, addr, password, ispermenant]
                    j = {'status': "RegisterSuccess"}
                else:
                    # Fail
                    # reply message
                    j = {'status': "RegisterFail", 'reason': 'id is not exist'}
                # send message
                j = json.dumps(j).encode('utf-8')
                conn.send(j)
            elif msg_type == 'AbortNeedConn':
                uuid2 = json_obj['to']
                # close connection
                dict1[uuid2][1].send(msgfromserver)
                conn.close()
                break
            elif msg_type == 'AskConn':
                uuid2 = json_obj['to']
                j = {'status': "NeedConn", 'from': uuid2, 'directly': True, 'TCPip': localIP, 'TCPport': localPort}
                j = json.dumps(j).encode('utf-8')
                dict1[uuid2][1].send(j)
                pass
            elif msg_type == 'NeedConnAccept':
                uuid2 = json_obj['to']
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'NeedConnRefuse':
                uuid2 = json_obj['to']
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'AskMonitor':
                uuid2 = json_obj['to']
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'AbortAskConn':
                uuid2 = json_obj['to']
                dict1[uuid2][1].send(msgfromserver)
                conn.close()
                break
            elif msg_type == 'NeedMonitorAccept':
                uuid2 = json_obj['to']
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'NeedMonitorRefuse':
                uuid2 = json_obj['to']
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'AskMonitorSuccess':
                uuid2 = json_obj['to']
                dict1[uuid2][1].send(msgfromserver)
            elif msg_type == 'AskMonitorFail':
                uuid2 = json_obj['to']
                dict1[uuid2][1].send(msgfromserver)

    return


if __name__ == '__main__':
    dict1 = dict()
    dict2 = dict()
    localIP = "127.0.0.1"
    localPort = 20001
    # Create a tcp socket
    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    # Bind to address and ip
    TCPServerSocket.bind((localIP, localPort))
    TCPServerSocket.listen()
    print("TCP server up and listening")
    # Listen for incoming client
    try:
        while True:
            conn, addr = TCPServerSocket.accept()
            size_bytes = conn.recv(4)
            plen = int.from_bytes(size_bytes, byteorder='little')
            msgfromserver = conn.recv(plen)
            json_obj = json.loads(msgfromserver.decode('utf-8'))
            msg_type = json_obj['status']
            thread = threading.Thread(target=client_handler,args=(conn,addr))
            thread.start()
    finally:
        # 关闭服务器套接字
        print("Closing server socket")
        TCPServerSocket.close()




