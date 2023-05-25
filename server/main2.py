import json
import socket
import threading
import mysql.connector
from mysql.connector import Error


def client_handler(conn, addr):
    print("-----------------------------------------")
    print(repr(conn) + " " + repr(addr) + "\nhandler start")
    print("-----------------------------------------")
    
    while True:
        #######################################################
        # receive user data length from socket
        #######################################################
        try:
            conn.settimeout(5)
            size_bytes = conn.recvfrom(4)
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
            user_id = ''
            for i in msgfromserver:
                if i != ';':
                    user_id += chr(i)
            cur.execute("SELECT * FROM user_table WHERE IP = '" + addr + "'")
            rows = cur.fetchone()
            
            print('Data fetched successfully')
            user_from = rows[1] + msgfromserver[len(user_id):]
            #######################################################
            # two field <type> or <status>
            #######################################################
            #######################################################
            # client2
            # 1.Grab screenshot and uuid1 and another_user as image data
            # 1.send to another client
            #######################################################
            conn.send(user_from)
        except OSError:
            break
    return


if __name__ == '__main__':
    #######################################################
    # localIP: serverIP
    # localPort: server run TCP_server on
    #######################################################
    DB_NAME = "pyremote"
    DB_USER = "asddzxcc1856"
    DB_PASS = "asddzxcc1857"
    DB_HOST = "127.0.0.1"
    DB_PORT = "3306"
    
    try:
        conn = mysql.connector.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)
        print("Database connected successfully")
        cur = conn.cursor()
        localIP = "127.0.0.1"
        localUDPPort = 20002
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
        try:
            while True:
                #######################################################
                # receive user data length from socket
                #######################################################
                size_bytes, addr = UDPServerSocket.recvfrom(4)
                #######################################################
                # length of packet
                #######################################################
                plen = int.from_bytes(size_bytes, byteorder='little')
                #######################################################
                # receive user data with plen size
                #######################################################
                msgfromserver = UDPServerSocket.recv(plen)
                #######################################################
                # convert bytes to string to json
                #######################################################
                try:
                    json_obj = json.loads(msgfromserver.decode('utf-8'))
                except json.decoder.JSONDecodeError:
                    continue
                print(repr(addr) + " " + str(json_obj))
                #######################################################
                # declare thread for a client
                #######################################################
                thread = threading.Thread(target=client_handler, args=(UDPServerSocket, addr))
                #######################################################
                # start handle client event
                #######################################################
                thread.start()
                #######################################################
                # close handle client event
                #######################################################
                thread.join()
        finally:
            #######################################################
            # close all connection
            #######################################################
            print("Closing server socket")
            UDPServerSocket.close()
            conn.close()
    except Error as e:
        print("Error while connecting to MySQL", e)
    
