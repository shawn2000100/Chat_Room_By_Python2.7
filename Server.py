# coding=utf-8
import socket
import logging
import thread
import time
from sys import argv

# 在同個資料夾建立一個 Server 端的 LOG
logging.basicConfig(level = logging.INFO, filename = 'Server_History.log',
                    format='[%(levelname)s] %(asctime)s %(threadName)s %(message)s', )
BUFF_SIZE = 2048
list_of_clients = [] # 記錄目前所有連線對 [0]:conn, [1]:usr_name of that connection


# 把一開始建立的conn移出list_of_clients (登出)
def Log_Out(client):
    # 先檢查此連線是否已存在
    if client in list_of_clients:
        # 檢查這個connection是否還在
        if client[0]:
            client[0].send('你的連線已被伺服器中斷\n')
            client[0].close()
            list_of_clients.remove(client)


# 廣播功能
def Broadcast(user_name, message):
    # 在送出的訊息前加上標頭訊息 (e.g., [Jay]: Hi)
    msg_to_send = '[' + user_name + ']:' + message # 注意這邊後面不用加上\n，因為傳過來時已經有\n了

    # 對所有人發相同訊息 (包含自己)
    for client in list_of_clients:
        try:
            client[0].send(msg_to_send)

        except socket.error:
            error_msg = '[' + user_name + ']廣播時發生未知錯誤'
            logging.warning(error_msg)
            print(error_msg)
            Log_Out(client)


# 私訊功能
def Private_Message(from_usr, dest_usr, message):
    # 依序遍歷每個連線對
    for client in list_of_clients:
        # 如果找到 訊息目的 或者 發送來源，都送訊息出去
        if client[1] == dest_usr or client[1] == from_usr:
            try:
                # 在訊息前加上標頭 (e.g., [私訊]Jay: hihi)
                msg_to_send = '[私訊]' + from_usr + ':' + message + '\n' # 記得要有最後的\n ，message傳過來時是沒有\n的
                client[0].send(msg_to_send)

            except socket.error:
                error_msg = '未知錯誤發生於 [' + from_usr + ']私訊時'
                logging.warning(error_msg)
                print(error_msg)
                Log_Out(client)


'''
    傳送檔案步驟：
    1. from_user 傳至 Server，Server接收完畢
    2. Server傳至dest_user
'''
def Send_File(conn, from_user, file_path, dest_user):
    try:
        # 通知Server，某Client要送檔案來了 (e.g., [Jay]傳來了一個檔案 客戶端路徑:/Users/JayChen.txt)
        msg = '[' + from_user + ']' + '傳來了一個檔案，客戶端路徑:' + file_path
        logging.info(msg)
        print msg

        # 首先拆解檔案路徑 (e.g., /Users/JayChen.txt)，抓出最後的檔案名稱及格式
        token = file_path.split('/')
        file_name = token[-1]

        # 伺服器端開啟一個新Binary檔案
        new_file = open(file_name, 'wb')

        # 首先接收客戶端所上傳來的檔案
        f = conn.recv(BUFF_SIZE)
        while('END OF FILE' not in f):
            new_file.write(f)
            f = conn.recv(BUFF_SIZE)

        # Server端接收完成，關閉檔案
        new_file.close()

        conn.send('伺服器接收成功! 檔名[' + file_name + ']\n')
        tmpLog = '伺服器接收成功! 檔名[' + file_name + ']\n'
        logging.info(tmpLog)
        print tmpLog


        # 接著將剛剛所接收的檔案轉傳給另一位使用者
        for client in list_of_clients:
            # 首先鎖定該位user
            if (client[1] == dest_user):
                # 猜測可能是因為傳送時間太近了，下面兩行在Client端收到時會 "黏" 在一起 (i.e. 被當作同時傳送的)
                client[0].sendall('[%s]傳給你一份檔案，客戶端路徑:%s' % (from_user, file_path) + '\n' )
                client[0].sendall('START OF FILE: ' + file_name + '\n')

                # 睡覺超重要!!!!! 沒加這行程式傳送的訊息會 "黏" 在一起 !!!!
                time.sleep(0.5)

                # Server端打開剛剛接收完成的檔案 (e.g., JayChen.txt)
                file = open(file_name, 'rb')
                fr = file.read(BUFF_SIZE)
                while(fr):
                    # Debug以及測試用
                    # print ('這邊傳了----------')
                    # print fr
                    # print ('這邊傳了++++++++++')
                    client[0].sendall(fr)
                    fr = file.read(BUFF_SIZE)

                # 傳送完畢，關閉檔案
                file.close()

                # 睡覺很重要!!! 防止END OF FILE與之前的讀檔資料 fr "糊" 在一起!!!
                time.sleep(0.5)

                # 告知接收端，檔案傳輸結束，他才知道要關閉那邊的檔案
                client[0].sendall('END OF FILE')
                tmpLog = '伺服器端傳送完畢! 檔名[' + file_name + ']\n'
                logging.info(tmpLog)
                print tmpLog

    except socket.error:
        error_msg = '未知錯誤發生於 [' + from_usr + ']傳檔時'
        logging.warning(error_msg)
        print(error_msg)
        Log_Out( (conn, from_user) )


''' 
    處理Client端的連線Thread
    1 msg
    2 dst  msg
    3 file_path  dst
    4
    5
'''
def Handle_Client(conn, addr):
    # 連線成功後馬上就會收到客戶端名字 (e.g., Jay)
    user_name = conn.recv(BUFF_SIZE).strip()
    print user_name

    # 歡迎新加入聊天室的user
    for client in list_of_clients:
        client[0].send('大家歡迎 [' + user_name + '] 加入群聊!') # 注意這邊不用加\n，因為Client端使用print會自動換行

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
                # 首先拆解字串，得出dest_name
                msg = command.split()
                dest_user = msg[1]

                # 再度拆解，將dest_user後面的message全部找出來，記得考慮到message有空白之情形
                msg_to_send = ' '.join(msg[2:]) # 這邊直接用msg[2]的話遇到空白會GG
                Private_Message(user_name, dest_user, msg_to_send)

            elif ('3' == command[0]):
                # 拆解字串，由於不會有額外空白，故可直接取值
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

    except socket.error:
        print( '[%s:%s] 已中斷連線' % (addr[0], str(addr[1])) )
        print(socket.error)
        logging.info( '[%s:%s]%s 已中斷連線' % (addr[0], str(addr[1]), user_name) )
        logging.info(socket.error)
        Log_Out( (conn, user_name) )


'''
    Server主程式，須於命令列執行 (e.g., -p 8888)
'''
def main(p, port):
    HOST = '127.0.0.1'
    PORT = int(port)
    BACKLOG = 10 # 最多接受的pending連線數 (不包含已連上的)

    # 首先宣告一個TCP Socket
    # 接著binding伺服器IP及PORT
    # 開始listen (接收Client連線)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(BACKLOG)
    logging.info('伺服器listen on %s:%s' % (HOST, PORT))
    print '伺服器listen on %s:%s' % (HOST, PORT)

    # 無窮迴圈，將會一直接收新的Client連線
    while 1:
        conn, addr = server.accept()
        logging.info('客戶端連接成功 ' + addr[0] + ':' + str(addr[1]))
        print '客戶端連接成功 ' + addr[0] + ':' + str(addr[1])

        # 每一個客戶連線成功後，都需要創造一個Thread來處理
        thread.start_new_thread(Handle_Client, (conn, addr, ))

    # Server端程式結束
    server.close()
    

main(argv[1], argv[2])
