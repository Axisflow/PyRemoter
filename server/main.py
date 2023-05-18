import json
import secrets
import socket
import string
import uuid
import threading


def client_handler(conn, addr):
    user_id = ''
    while True:
        #######################################################
        # receive user data length from socket
        #######################################################
        size_bytes = conn.recv(4)
        #######################################################
        # length of packet
        #######################################################
        plen = int.from_bytes(size_bytes, byteorder='little')
        #######################################################
        # receive user data with plen size
        #######################################################
        msgfromserver = conn.recv(plen)
        #######################################################
        # bytes to string to json
        #######################################################
        try:
            json_obj = json.loads(msgfromserver.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            continue
        #######################################################
        # two field <type> or <status>
        #######################################################
        if json_obj.get('type') is not None:
            #######################################################
            # interaction with one another client
            #######################################################
            # from user data -> get type to send a packet to another one
            #######################################################
            msg_type = json_obj['type']
            #######################################################
            # from user data -> get another one id
            #######################################################
            another_user = json_obj['to']
            if msg_type == 'screen':
                #######################################################
                # client2
                # 1.Grab screenshot and uuid1 and another_user as image data
                # 1.send to another client
                #######################################################
                dict1[another_user][1].send(msgfromserver)
            elif msg_type == 'MouseEvent':
                #######################################################
                # client2
                # 1.Grab mouse and uuid1 and another_user as image data
                # 1.send to another client
                #######################################################
                dict1[another_user][1].send(msgfromserver)
            elif msg_type == 'MousePoint':
                #######################################################
                # client2
                # 1.Grab mouse(x,y) and uuid1 and another_user as image data
                # 1.send to another client
                #######################################################
                dict1[another_user][1].send(msgfromserver)
            elif msg_type == 'Key':
                #######################################################
                # client2
                # 1.Grab key and uuid1 and another_user as image data
                # 1.send to another client
                #######################################################
                dict1[another_user][1].send(msgfromserver)
            elif msg_type == 'audio':
                #######################################################
                # client2
                # 1.Grab audio and uuid1 and another_user as image data
                # 1.send to another client
                #######################################################
                dict1[another_user][1].send(msgfromserver)
        else:
            #######################################################
            # interaction with one client
            #######################################################
            msg_type = json_obj['status']
            if msg_type == 'GetID':
                #######################################################
                # client send:
                # {status:"GetID", mac:<MAC address>}
                #######################################################
                # client rece:
                # {status:<"GetIDSuccess"/"GetIDFail">[, id:<ID number>, pwd:<password> reason:<Why Fail?>]}
                #######################################################

                #######################################################
                # from client data
                #######################################################
                mac_data = json_obj['mac']
                if mac_data not in dict2:
                    #######################################################
                    # generate random user_uuid
                    #######################################################
                    user_uuid = uuid.uuid4()
                    #######################################################
                    # mac -> uuid
                    #######################################################
                    dict2[mac_data] = str(user_uuid)
                    #######################################################
                    # generate random length of 8 password
                    #######################################################
                    alphabet = string.ascii_lowercase + string.digits
                    password = ''.join(secrets.choice(alphabet) for i in range(8))
                    #######################################################
                    # user_uuid -> [mac_data, conn, addr,password,permanent]
                    #                  0        1    2      3         4
                    #
                    #######################################################
                    dict1[str(user_uuid)] = [mac_data, conn, addr, password, False]
                    user_id = str(user_uuid)
                    #######################################################
                    # reply message
                    #######################################################
                    j = {'status': "GetIDSuccess", 'id': str(user_uuid), 'pwd': password}
                else:
                    #######################################################
                    # Fail
                    # reply message
                    #######################################################
                    j = {'status': "GetIDFail", 'id': dict2[mac_data], 'pwd': dict1[dict2[mac_data]][3],
                         'reason': 'mac has one id'}
                    user_id = dict2[mac_data]
                # send message
                j = json.dumps(j).encode('utf-8')
                conn.send(j)
            elif msg_type == 'Login':
                #######################################################
                # client send:
                # {status:"Login", id:<ID number>, pwd:<old password>}
                #######################################################
                # client rece:
                # {status:<"LoginSuccess"/"LoginFail">[, pwd:<new password>, reason:<Why Fail?>]}
                #######################################################

                #######################################################
                # from client data
                #######################################################
                user_uuid = json_obj['id']
                if user_uuid in dict1:
                    if dict1[user_uuid][4] is False:
                        #######################################################
                        # generate random length of 8 password
                        #######################################################
                        alphabet = string.ascii_lowercase + string.digits
                        password = ''.join(secrets.choice(alphabet) for i in range(8))
                        #######################################################
                        # reply message
                        #######################################################
                        j = {'status': "LoginSuccess", 'pwd': password}
                    elif dict1[user_uuid][4] is True:
                        #######################################################
                        # reply no new password
                        # reply message
                        #######################################################
                        j = {'status': "LoginSuccess"}
                else:
                    #######################################################
                    # Fail
                    # reply message
                    #######################################################
                    j = {'status': "LoginFail", 'reason': 'id is not exist'}
                #######################################################
                # send message
                #######################################################
                j = json.dumps(j).encode('utf-8')
                conn.send(j)
            elif msg_type == 'Register':
                #######################################################
                # client send:
                # {status:"Register",
                #  mac:<MAC address>,
                #  id:<ID number>,
                #  pwd:<password>,
                #  permenant:<True/False>
                # }
                #######################################################
                # client rece:
                # {status:<"RegisterSuccess"/"RegisterFail">[, reason:<Why Fail?>]}
                #######################################################
                # from client data
                #######################################################
                user_uuid = json_obj['id']
                mac_data = json_obj['mac']
                password = json_obj['pwd']
                ispermenant = json_obj['permenant']

                if str(user_uuid) not in dict1:
                    #######################################################
                    # reply message
                    #######################################################
                    dict2[mac_data] = str(user_uuid)
                    dict1[str(user_uuid)] = [mac_data, conn, addr, password, ispermenant]
                    user_id = str(user_uuid)
                    j = {'status': "RegisterSuccess"}
                else:
                    #######################################################
                    # Fail
                    # reply message
                    #######################################################
                    j = {'status': "RegisterFail", 'reason': 'id is not exist'}
                #######################################################
                # send message
                #######################################################
                j = json.dumps(j).encode('utf-8')
                conn.send(j)
            elif msg_type == 'AskConn':
                #######################################################
                # client send: {status:"AskConn",
                #               to:<{ID1, ID2, ...}>,
                #               pwd:<{"pwd1", "pwd2", ...}>
                #               } # 密碼若是空字串則代表使用詢問模式，否則使用直接連接模式
                #######################################################
                # client rece: {status:<"AskConnSuccess"/"AskConnFail">,
                #               from:<ID number>[, reason:<Why Fail?>,
                #               UDPip:<IP address or alias name>,
                #               UDPport:<port number>,
                #               TCPip:<格式一樣>,
                #               TCPport:<格式一樣>]
                #               } # 傳回影音傳輸伺服器、鍵鼠控制伺服器位置
                #######################################################
                # client rece: {status:"NeedConn",
                #               from:<ID number>,
                #               directly:<True/False>,
                #               UDPip:<IP address or alias name>,
                #               UDPport:<port number>,
                #               TCPip:<格式一樣>,
                #               TCPport:<格式一樣>}
                #               directly: True 直接連接模式， False 詢問模式
                #######################################################
                # client send: {status:<"NeedConnAccept"/"NeedConnRefuse">,
                #               to:<ID number>[,
                #               reason:<Why Refuse?>]} # 有可能被加入黑名單，或在詢問模式被拒絕了之類的
                #######################################################
                user = dict(zip(json_obj['to'],json_obj['pwd']))
                user_uuid = json_obj['id']
                for key, value in user.items():
                    if value == "":
                        j = {'status': "NeedConn", 'from': user_uuid, 'directly': False, 'TCPip': localIP,
                             'TCPport': localPort, 'UDPip': '', 'UDPport': ''}
                    else:
                        j = {'status': "NeedConn", 'from': user_uuid, 'directly': True, 'TCPip': localIP,
                             'TCPport': localPort, 'UDPip': '', 'UDPport': ''}
                    j = json.dumps(j).encode('utf-8')
                    dict1[key][1].send(j)
            elif msg_type == 'NeedConnAccept':
                another_user = json_obj['from']
                j = {'status': "AskConnSuccess", 'from': another_user, 'TCPip': localIP,
                     'TCPport': localPort, 'UDPip': '', 'UDPport': ''}
                j = json.dumps(j).encode('utf-8')
                dict1[user_id][1].send(j)
            elif msg_type == 'NeedConnRefuse':
                another_user = json_obj['from']
                j = {'status': "AskConnFail", 'reason': json_obj['reason'], 'from': another_user, 'TCPip': localIP,
                     'TCPport': localPort, 'UDPip': '', 'UDPport': ''}
                j = json.dumps(j).encode('utf-8')
                dict1[user_id][1].send(j)
            elif msg_type == 'AskMonitor':
                #######################################################
                # client send: {status:"AskMonitor",
                #               to:<ID number>,
                #               question:<Anything>
                #               }
                #######################################################
                # client rece: {status:<"AskMonitorSuccess/AskMonitorFail">,
                #               from:<ID number>,
                #               question:<Anything>[,
                #               answer:<Anything>,
                #               reason:<Why Fail?>]
                #               }
                #######################################################
                # client rece: {status:"NeedMonitor",
                #               from:<ID number>,
                #               question:<Anything>
                #               }
                #######################################################
                # client send: {status:<"NeedMonitorAccept/NeedMonitorRefuse">,
                #               to:<ID number>,
                #               question:<Anything>[,
                #               answer:<Anything>,
                #               reason:<Why Refuse?>]
                #               }
                #######################################################
                another_user = json_obj['to']
                j = {'status': "NeedMonitor", 'from': user_id, 'question': json_obj['question']}
                j = json.dumps(j).encode('utf-8')
                dict1[another_user][1].send(j)
            elif msg_type == 'NeedMonitorAccept':
                another_user = json_obj['to']
                j = {'status': "AskMonitorSuccess", 'from': user_id, 'question': json_obj['question'],
                     'answer': json_obj['answer']}
                j = json.dumps(j).encode('utf-8')
                dict1[another_user][1].send(j)
            elif msg_type == 'NeedMonitorRefuse':
                another_user = json_obj['to']
                j = {'status': "AskMonitorSuccess", 'from': user_id, 'question': json_obj['question'],
                     'answer': json_obj['answer'], 'reason': json_obj['reason']}
                j = json.dumps(j).encode('utf-8')
                dict1[another_user][1].send(j)
            elif msg_type == 'AbortNeedConn':
                another_user = json_obj['to']
                #######################################################
                # close connection
                #######################################################
                dict1[another_user][1].send(msgfromserver)
                conn.close()
                break
            elif msg_type == 'AbortAskConn':
                another_user = json_obj['to']
                #######################################################
                # close connection
                #######################################################
                dict1[another_user][1].send(msgfromserver)
                conn.close()
                break

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
            thread = threading.Thread(target=client_handler, args=(conn, addr))
            thread.start()
    finally:
        # 关闭服务器套接字
        print("Closing server socket")
        TCPServerSocket.close()
