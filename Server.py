# coding=utf-8
import socket
import logging
import thread
import time
from sys import argv

logging.basicConfig(level = logging.INFO, filename = 'Server_History.log',
                    format='[%(levelname)s] %(asctime)s %(threadName)s %(message)s', )
BUFF_SIZE = 2048
list_of_clients = [] # [0]:conn, [1]:usr_name of that connection

# 把一開始建立的conn移出list_of_clients (登出)
def Log_Out(client):
    # 先檢查此連線是否已存在
    if client in list_of_clients:
        client[0].sendall('你的連線已被伺服器中斷')
        client[0].close()
        list_of_clients.remove(client)

# 廣播功能
def Broadcast(user_name, message):

    msg_to_send = '[' + user_name + ']:' + message
    for client in list_of_clients:
        try:
            client[0].sendall(msg_to_send)

        except socket.error:
            error_msg = '[' + user_name + ']廣播時發生未知錯誤'
            logging.warning(error_msg)
            print(error_msg)
            Log_Out(client)

def Private_Message(from_usr, dest_usr, message):

    for client in list_of_clients:
        if client[1] == dest_usr or client[1] == from_usr:
            try:
                msg_to_send = '[私訊]' + from_usr + ':' + message + '\n'
                client[0].sendall(msg_to_send)

            except socket.error:
                error_msg = '未知錯誤發生於 [' + from_usr + ']私訊時'
                logging.warning(error_msg)
                print(error_msg)
                Log_Out(client)

def Send_File(conn, from_user, file_path, dest_user):

    # e.g., [Jay]傳來了一個檔案 客戶端路徑:/Users/JayChen.txt
    msg = '[' + from_user + ']' + '傳來了一個檔案，客戶端路徑:' + file_path
    logging.info(msg)
    print msg

    token = file_path.split('/')
    file_name = token[-1]
    print 'test ' + file_name
    new_file = open(file_name, 'wb')

    try:
        f = conn.recv(BUFF_SIZE)
        while(f != 'END OF FILE'):
            new_file.write(f)
            f = conn.recv(BUFF_SIZE)
        new_file.close()

        conn.sendall('伺服器端接收成功!')
        tmpLog = '伺服器接收成功! 檔名[' + file_name + ']'
        logging.info(tmpLog)
        print tmpLog

    except socket.error:
        error_msg = '未知錯誤發生於 [' + from_usr + ']傳檔時'
        logging.warning(error_msg)
        print(error_msg)
        Log_Out( (conn, from_user) )

def Handle_Client(conn, addr):

    user_name = conn.recv(BUFF_SIZE).strip() #e.g., Jay
    print user_name

    # 歡迎新加入聊天室的user
    for client in list_of_clients:
        client[0].send('大家歡迎 [' + user_name + '] 加入群聊!\n')

    # 於list_of_clients中儲存所有連線對的 [0]:conn 以及 [1]:user_name
    list_of_clients.append((conn, user_name))

    # 傳送菜單給新user
    conn.sendall('你好，%s 歡迎進入聊天室\n<廣播>:1 msg <私訊>:2 dst_usr msg <傳檔案>:3 file_path dst_usr <誰在線上>:4 <登出>:5 \n' % user_name)

    try:
        while 1:
            command = conn.recv(BUFF_SIZE)
            #conn.send('收到...' + command) 方便debug用

            if ('1' == command[0]):
                Broadcast(user_name, command[2:])

            elif ('2' == command[0]):
                msg = command.split() # 拆解字串
                dest_user = msg[1] # 拆出dest_name
                msg_to_send = ' '.join(msg[2:])
                Private_Message(user_name, dest_user, msg_to_send)

            elif ('3' == command[0]):
                msg = command.split()
                file_path = msg[1]
                dest_user = msg[2]
                Send_File(conn, user_name, file_path, dest_user)

            elif ('4' == command[0]):
                conn.send('\n-----誰在線上-----\n')
                for client in list_of_clients:
                    conn.send('[' + client[1] + ']' + '\n')
                conn.send('-------------------\n')

            elif ('5' == command[0]):
                Log_Out((conn, user_name))
                for client in list_of_clients:
                    client[0].send('[' + user_name + ']' + '已登出 \n')

            else:
                conn.sendall('你輸入了無效的指令!\n')

    except:
        print( '[%s:%s] 已中斷連線' % (addr[0], str(addr[1])) )
        logging.info( '[%s:%s]%s 已中斷連線' % (addr[0], str(addr[1]), user_name) )
        Log_Out( (conn, user_name) )

def main(nothing, port):
    HOST = '127.0.0.1'
    PORT = int(port)
    BACKLOG = 10
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(BACKLOG)
    logging.info('伺服器listen on %s:%s' % (HOST, PORT))
    print '伺服器listen on %s:%s' % (HOST, PORT)

    while 1:
        conn, addr = server.accept()
        logging.info('客戶端連接成功 ' + addr[0] + ':' + str(addr[1]))
        print '客戶端連接成功 ' + addr[0] + ':' + str(addr[1])
        thread.start_new_thread(Handle_Client, (conn, addr, ))

    server.close()
    

main(argv[1], argv[2])
