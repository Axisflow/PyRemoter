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
            #######################################################
            # receive user data with plen size
            #######################################################
            msgfromserver,addr = conn.recvfrom(65500)
            #######################################################
            # convert bytes to string to json
            #######################################################
            user_id = ''
            for i in msgfromserver:
                if i != ';':
                    user_id += chr(i)
            cur.execute("SELECT * FROM user_table WHERE IP = '" + str(addr[0]) + "," + str(addr[1])  + "'")
            rows = cur.fetchone()
            
            print('Data fetched successfully')
            user_from = rows[1].encode('utf-8') + msgfromserver[len(user_id):]
            print(rows[1])
            #######################################################
            # two field <type> or <status>
            #######################################################
            #######################################################
            # client2
            # 1.Grab screenshot and uuid1 and another_user as image data
            # 1.send to another client
            #######################################################
            cur.execute("SELECT * FROM user_table WHERE IP = '" + user_id + "'")
            rows = cur.fetchone()
            
            print('Data fetched successfully')
            conn.sendto(user_from,tuple(rows[0].split(',')))  
        except OSError:
            break
    return


if __name__ == '__main__':
    #######################################################
    # localIP: serverIP
    # localPort: server run TCP_server on
    #######################################################
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
        try:
            #######################################################
             # receive user data with plen size
             #######################################################
            print("wait for msg")
            msgfromserver,addr = UDPServerSocket.recvfrom(65500)
            print(msgfromserver)
            print(addr)
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
    
