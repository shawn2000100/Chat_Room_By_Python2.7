# coding=utf-8
import socket
import logging
import thread
import time

logging.basicConfig(level = logging.INFO, filename = 'Server_History.log',
                    format='[%(levelname)s] %(asctime)s %(threadName)s %(message)s', )


BUFF_SIZE = 2048
list_of_clients = [] # [0]:conn, [1]:usr_name of that connection

# 把一開始建立的conn移出list_of_clients (登出)
def Log_Out(client):
    # 先檢查此連線是否已存在
    for sock in list_of_clients:
        if client == sock[0]:
            client.close()
            list_of_clients.remove(sock)
            #print list_of_clients

# 廣播功能
def Broadcast(user_info, message):

    msg_to_send = user_info + ':' + message
    for clients in list_of_clients:
        try:
            clients[0].sendall(msg_to_send)

        except:
            print('廣播時發生未知錯誤')
            logging.warning('廣播時發生未知錯誤')
            Log_Out(clients)

def Private_Message(from_usr, dest_usr, message):

    for clients in list_of_clients:
        if clients[1] == dest_usr or clients[1] == from_usr:
            try:
                msg_to_send = '[私訊]' + from_usr + ': ' + message + '\n'
                clients[0].sendall(msg_to_send)

            except:
                print('Unknown error occured when %s send file' % from_usr)
                logging.warning('Unknown error occured when % s send file' % from_usr)
                Log_Out(clients)

def Send_File(conn, from_user, file_path):
    new_file_name = 'file_' + str( int(time.time()) )
    new_file = open(new_file_name, 'wb')

    msg = '[' + from_user + ']' + '傳來了一個檔案，客戶端路徑:' + file_path # e.g., [Jay]傳來了一個檔案 客戶端路徑:/Users/JayChen.txt
    logging.info(msg)
    print msg

    f = conn.recv(BUFF_SIZE)
    while(f != 'END OF FILE'):
        new_file.write(f)
        f = conn.recv(BUFF_SIZE)
    new_file.close()

    conn.sendall('伺服器端接收成功!')
    tmpLog = '伺服器接收成功! 新檔名[' + new_file_name + ']'
    logging.info(tmpLog)
    print tmpLog


def Handle_Client(conn, addr):

    conn.send('進入聊天室，請輸入一個暱稱: ')
    reply = conn.recv(BUFF_SIZE)

    user_name = reply.strip()
    user_info = '[' + addr[0] + ':' + str(addr[1]) + ']' + user_name  # [xx.xx.xx.xx:yyy]usr
    list_of_clients.append((conn, user_name))

    conn.send('你好，%s \n' % user_name)
    conn.sendall('廣播:1 <message> 私訊:2 <dest_user> <message> 傳檔案:3 <your_name> <file_path> 誰在線上:4 登出:5 \n')

    for client in list_of_clients:
        if client[0] != conn:
            client[0].send('大家歡迎 ' + user_name + ' 加入群聊!\n')

    while 1:
        try:
            command = conn.recv(BUFF_SIZE)
            #conn.send('收到...' + command)

            if ('1' == command[0]):
                Broadcast(user_info, command[1:])

            elif ('2' == command[0]):
                msg = command.split() # 拆解字串
                dest_user = msg[1] # 拆出dest_name
                Private_Message(user_name, dest_user, command[1:])

            elif ('3' == command[0]):
                msg = command.split()
                from_name = msg[1]
                file_path = msg[2]
                Send_File(conn, from_name, file_path)

            elif ('4' == command[0]):
                conn.send('\n-----誰在線上-----\n')
                for client in list_of_clients:
                    conn.send('[' + client[1] + ']' + '\n')
                conn.send('-------------------\n')
            elif ('5' == command[0]):
                for client in list_of_clients:
                    if client[0] != conn:
                        client[0].send('[' + user_info + ']' + '已登出 \n')

                Log_Out(conn)

            
            else:
                conn.sendall('你輸入了無效的指令\n')

        except:
            print( '[%s:%s] 已中斷連線' % (addr[0], str(addr[1])) )
            logging.info( '[%s:%s] 已中斷連線' % (addr[0], str(addr[1])) )
            Log_Out(conn)
            break

    #conn.close()

def main():
    HOST = '127.0.0.1'
    PORT = 9999
    BACKLOG = 10
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(BACKLOG)
    print '伺服器listen on %s:%s' % (HOST, PORT)
    logging.info('伺服器listen on %s:%s' % (HOST, PORT))
    
    while 1:
        conn, addr = server.accept()
        print '客戶端連接成功 ' + addr[0] + ':' + str(addr[1])
        logging.info('客戶端連接成功 ' + addr[0] + ':' + str(addr[1]))

        thread.start_new_thread(Handle_Client, (conn, addr, ))

        # conn.close() 加這行會有 [Errno 9] Bad file descriptor ，千萬別加!
    server.close()
    

main()