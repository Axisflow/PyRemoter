import json
import secrets
import socket
import string
import uuid
import threading
import mysql.connector
from mysql.connector import Error

def client_handler(conn, addr):
    print("-----------------------------------------")
    print(repr(conn) + " " + repr(addr) + "\nhandler start")
    print("-----------------------------------------")
    user_id = ''
    try:
        
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
            # convert bytes to string to json
            #######################################################
            try:
                json_obj = json.loads(msgfromserver.decode('utf-8'))
            except json.decoder.JSONDecodeError:
                continue
            print(repr(addr) + " " + str(json_obj))
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
                    dict0[another_user].send(msgfromserver)
                elif msg_type == 'MouseEvent':
                    #######################################################
                    # client2
                    # 1.Grab mouse and uuid1 and another_user as image data
                    # 1.send to another client
                    #######################################################
                    dict0[another_user].send(msgfromserver)
                elif msg_type == 'MousePoint':
                    #######################################################
                    # client2
                    # 1.Grab mouse(x,y) and uuid1 and another_user as image data
                    # 1.send to another client
                    #######################################################
                    dict0[another_user].send(msgfromserver)
                elif msg_type == 'Key':
                    #######################################################
                    # client2
                    # 1.Grab key and uuid1 and another_user as image data
                    # 1.send to another client
                    #######################################################
                    dict0[another_user].send(msgfromserver)
                elif msg_type == 'audio':
                    #######################################################
                    # client2
                    # 1.Grab audio and uuid1 and another_user as image data
                    # 1.send to another client
                    #######################################################
                    dict0[another_user].send(msgfromserver)
                elif msg_type == 'AskUpdate':
                    ## 9-1 (2)控制端請求更新狀態
                    #    client send: {status:"AskUpdate", to:<ID number>, key:<Anything>, value:<Anything>}

                    ## 9-2 (2)被控端接收狀態更新
                    #    client rece: {status:"NeedUpdate", from:<ID number>, key:<Anything>, value:<Anything>}
                    j = {'type': "NeedUpdate", 'from': user_id, 'key': json_obj['key'], 'value': json_obj['value']}
                    j = json.dumps(j).encode('utf-8')
                    dict0[another_user].send(j)
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
                    if mac_data not in client_mac:
                        #######################################################
                        # generate random user_uuid
                        #######################################################
                        alphabet = string.digits
                        user_uuid = ''.join(secrets.choice(alphabet) for _ in range(8))
                        #######################################################
                        # mac -> uuid
                        ####################################################### 
                        client_mac[mac_data] = str(user_uuid)
                        with open("client_mac.json", "w") as file:
                            json.dump(client_mac, file)
                        #######################################################
                        # generate random length of 8 password
                        #######################################################
                        alphabet = string.ascii_lowercase + string.digits
                        password = ''.join(secrets.choice(alphabet) for _ in range(8))
                        #######################################################
                        # user_uuid -> [mac_data, addr,password,permanent]
                        #                  0        1      2         3        
                        #
                        #######################################################
                        dict0[str(user_uuid)] = conn
                        client_info[str(user_uuid)] = [mac_data, addr, password, False]
                        with open("client_info.json", "w") as file:
                            json.dump(client_info, file)
                        if user_id == '': 
                            sql = "INSERT INTO user_table (IP,ID,MAC) VALUES ('" + str(addr[0]) + "," + str(addr[1]) + "', '" + str(user_uuid) + "', '" + mac_data + "')"

                            cur.execute(sql)

                            conndb.commit()

                            print(cur.rowcount, "record(s) affected")
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
                        j = {'status': "GetIDFail", 'id': client_mac[mac_data], 'pwd': client_info[client_mac[mac_data]][2],
                            'reason': 'mac has one id'}
                        user_id = client_mac[mac_data]
                        cur.execute("SELECT * FROM user_table WHERE MAC = '" + mac_data + "'")
                        rows = cur.fetchone()
                        if rows is not None:
                            user_id = rows[1]
                            dict0[user_id] = conn
                        else:
                            user_id = ''
                        print(user_id)
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
                    j = {}
                    
                    if user_uuid in client_info:
                        if client_info[user_uuid][3] is False:
                            #######################################################
                            # generate random length of 8 password
                            #######################################################
                            alphabet = string.ascii_lowercase + string.digits
                            password = ''.join(secrets.choice(alphabet) for _ in range(8))
                            #######################################################
                            # reply message
                            #######################################################
                            j = {'status': "LoginSuccess", 'pwd': password}
                            

                        elif client_info[user_uuid][3] is True:
                            #######################################################
                            # reply no new password
                            # reply message
                            #######################################################
                            j = {'status': "LoginSuccess"}
                        
                        cur.execute("SELECT * FROM user_table WHERE MAC = '" + client_info[user_uuid][0] + "'")
                        rows = cur.fetchone()
                        if rows is not None:
                            user_id = rows[1]
                            dict0[user_id] = conn
                        else:
                            user_id = ''
                        print(user_id)
                        dict0[user_id] = conn
                        print(dict0)
                        sql = "UPDATE user_table SET IP = '" + str(addr[0]) + "," + str(addr[1]) + "' WHERE MAC = '" + client_info[user_uuid][0] + "'"

                        cur.execute(sql)

                        conndb.commit()

                        print(cur.rowcount, "record(s) affected")
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

                    if str(user_uuid) not in client_info:
                        #######################################################
                        # reply message
                        #######################################################
                        dict0[str(user_uuid)] = conn
                        client_mac[mac_data] = str(user_uuid)
                        with open("client_mac.json", "w") as file:
                            json.dump(client_mac, file)
                        client_info[str(user_uuid)] = [mac_data, addr, password, ispermenant]
                        with open("client_info.json", "w") as file:
                            json.dump(client_info, file)
                        user_id = str(user_uuid)
                        sql = "UPDATE user_table SET ID = '" + user_id + "' WHERE MAC = '" + client_info[user_uuid][0] + "'"

                        cur.execute(sql)

                        conndb.commit()

                        print(cur.rowcount, "record(s) affected")
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
                    user = dict(zip(json_obj['to'], json_obj['pwd']))
                    user_uuid = user_id
                    print(dict0)
                    for key, value in user.items():
                        if key in client_info and key in dict0:
                            if value == "":
                                j = {'status': "NeedConn", 'from': user_uuid, 'directly': False, 'TCPip': localIP,
                                    'TCPport': localTCPPort, 'UDPip': localIP, 'UDPport': localUDPPort}
                            else:
                                j = {'status': "NeedConn", 'from': user_uuid, 'directly': True, 'TCPip': localIP,
                                    'TCPport': localTCPPort, 'UDPip': localIP, 'UDPport': localUDPPort}
                            j = json.dumps(j).encode('utf-8')
                            dict0[key].send(j)
                elif msg_type == 'NeedConnAccept':
                    another_user = json_obj['to']
                    j = {'status': "AskConnSuccess", 'from': user_id, 'TCPip': localIP,
                        'TCPport': localTCPPort, 'UDPip': localIP, 'UDPport': localUDPPort}
                    j = json.dumps(j).encode('utf-8')
                    dict0[another_user].send(j)
                elif msg_type == 'NeedConnRefuse':
                    another_user = json_obj['to']
                    j = {'status': "AskConnFail", 'reason': json_obj['reason'], 'from': user_id, 'TCPip': localIP,
                        'TCPport': localTCPPort, 'UDPip': localIP, 'UDPport': localUDPPort}
                    j = json.dumps(j).encode('utf-8')
                    dict0[another_user].send(j)
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
                    dict0[another_user].send(j)
                elif msg_type == 'NeedMonitorAccept':
                    another_user = json_obj['to']
                    j = {'status': "AskMonitorSuccess", 'from': user_id, 'question': json_obj['question'],
                        'answer': json_obj['answer']}
                    j = json.dumps(j).encode('utf-8')
                    dict0[another_user].send(j)
                elif msg_type == 'NeedMonitorRefuse':
                    another_user = json_obj['to']
                    j = {'status': "AskMonitorSuccess", 'from': user_id, 'question': json_obj['question'],
                        'answer': json_obj['answer'], 'reason': json_obj['reason']}
                    j = json.dumps(j).encode('utf-8')
                    dict0[another_user].send(j)
                elif msg_type == 'AbortNeedConn':
                    another_user = json_obj['to']
                    #######################################################
                    # close connection
                    #######################################################
                    dict0[another_user].send(msgfromserver)
                    conn.close()
                    break
                elif msg_type == 'AbortAskConn':
                    another_user = json_obj['to']
                    #######################################################
                    # close connection
                    #######################################################
                    dict0[another_user].send(msgfromserver)
                    conn.close()
                    break
    except socket.timeout:
        return
    return


if __name__ == '__main__':
    #######################################################
    # client_info: user_uuid -> [mac_data, conn, addr,password,permanent]
    # client_mac: mac -> user_uuid
    # localIP: serverIP
    # localPort: server run TCP_server on
    #######################################################
    
    dict0 = dict()
    try:
        with open("client_info.json","r") as file:
            client_info = json.load(file)
    except FileNotFoundError:
        client_info = dict()
    try:
        with open("client_mac.json","r") as file:
            client_mac = json.load(file)
    except FileNotFoundError:
        client_mac = dict()
    print(client_info)
    print(client_mac)
    try:
        with open("database_info.json","r") as file:
            DB_NAME,DB_USER,DB_PASS,DB_HOST = json.load(file).values()
    except FileNotFoundError:
        pass
    try:
        with open("serverIP.json","r") as file:
            localIP,localUDPPort,localTCPPort = json.load(file).values()
    except FileNotFoundError:
        pass
    try:
        conndb = mysql.connector.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST
                                )
        print("Database connected successfully")
        cur = conndb.cursor(buffered=True)
        #######################################################
        # Create a TCP socket
        #######################################################
        TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        #######################################################
        # Bind to address and ip
        #######################################################
        TCPServerSocket.bind((localIP, localTCPPort))
        #######################################################
        #
        #######################################################
        TCPServerSocket.listen()
        print("TCP server up and listening")
        #######################################################
        # Listen for incoming client
        #######################################################
        try:
            while True:
                #######################################################
                # establish connection
                #######################################################
                conn, addr = TCPServerSocket.accept()
                #######################################################
                # declare thread for a client
                #######################################################
                thread = threading.Thread(target=client_handler, args=(conn, addr))
                #######################################################
                # start handle client event
                #######################################################
                thread.start()
        finally:
            #######################################################
            # close all connection
            #######################################################
            print("Closing server socket")
            TCPServerSocket.close()
    except Error as e:
        print("Error while connecting to MySQL", e)
