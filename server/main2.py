import json
import socket
import threading
import mysql.connector
from mysql.connector import Error

if __name__ == '__main__':
    #######################################################
    # localIP: serverIP
    # localPort: server run TCP_server on
    #######################################################
    info = dict()
    try:
        with open("database_info.json","r") as file:
            DB_NAME,DB_USER,DB_PASS,DB_HOST = json.load(file).values()
    except FileNotFoundError:
        pass
    try:
        conn = mysql.connector.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST
                                )
        print("Database connected successfully")
        cur = conn.cursor()
        try:
            with open("serverIP.json","r") as file:
                localIP,localUDPPort,localTCPPort = json.load(file).values()
        except FileNotFoundError:
            pass
        #######################################################
        # Create a TCP socket
        #######################################################
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #######################################################
        # Bind to address and ip
        #######################################################
        UDPServerSocket.bind((localIP, localUDPPort))
        #######################################################
        #
        #######################################################
        print("TCP server up and listening")
        #######################################################
        # Listen for incoming client
        #######################################################
        while True:
            #######################################################
            # receive user data length from socket
            #######################################################
            #######################################################
            # receive user data with plen size
            #######################################################
            print("wait for msg")
            msg_From_Control_End,addr = UDPServerSocket.recvfrom(65500)
            #######################################################
            # convert bytes to string to json
            #######################################################
            header = ''
            #######################################################
            # find header in message fromat => header;message
            #######################################################
            for i in msg_From_Control_End:
                if i == ord(';'):
                    break
                header += chr(i)
            if header == 'Hello':
                user_id = msg_From_Control_End[len(header) + 1:len(header) + 9]
                info[user_id] = addr
                print(msg_From_Control_End[0:100])
                print("-------msg1----------")
                print(info)
                print("---------------------")
                print(addr)
                print("---------------------")
            else:
                user_id = ''
                print(msg_From_Control_End[0:100])
                print("-------msg2----------")
                print(info)
                print("---------------------")
                print(addr)
                print("---------------------")
                for key,value in info.items():
                    if value == addr:
                        user_id = key
                        break
                msg_From_Control_End = user_id + msg_From_Control_End[len(header):]
                print('Control end Data append msgfromserver')
                #######################################################
                # two field <type> or <status>
                #######################################################
                #######################################################
                # client2
                # 1.Grab screenshot and uuid1 and another_user as image data
                # 1.send to another client
                #######################################################
                print('OK')
                UDPServerSocket.sendto(msg_From_Control_End,info[bytes(header, 'utf-8')])  
    except Error as e:
        print("Error while connecting to MySQL", e)
    
