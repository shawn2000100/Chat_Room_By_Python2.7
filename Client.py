# coding=utf-8
import socket
import logging
import threading
from sys import argv, stdout, exit

# 在同個資料夾建立一個 Client 端的 LOG
logging.basicConfig(level = logging.INFO, filename = 'Client_History.log',
                    format = '[%(levelname)s] %(asctime)s %(threadName)s %(message)s', )
BUFF_SIZE = 2048
connected = False


def Send_To_Server(sock):
    try:
        while 1:
            # 隨時想送什麼就輸入什麼
            msg = raw_input()

            # 若client要傳送檔案
            if ('3' == msg[0]):
                sock.send(msg) # 首先將命令送出去給server!! e.g., 3 /usr/file.txt dest_user

                # 拆解指令，找出檔案路徑
                token = msg.split()
                file_path = token[1]

                # Binary開檔
                file = open(file_path, 'rb')

                # 讀檔並傳輸
                fr = file.read(BUFF_SIZE)
                while(fr):
                    sock.sendall(fr) # 有讀到檔案就傳給Server
                    fr = file.read(BUFF_SIZE) # 傳完再讀一次，若讀取完畢則跳出迴圈

                # 傳送結束，關閉檔案
                file.close()
                print '客戶端檔案傳輸成功! 請輸入 \'END OF FILE\' 來結束傳輸'

            # Client要傳送其他指令 (e.g., 廣播、私訊、查登入人數)
            else:
                sock.send(msg)

    except socket.error:
        print('客戶端傳送時發生未知錯誤!')
        print(socket.error)
        logging.warning('客戶端傳送時發生未知錯誤!')
        logging.warning(socket.error)
        connected = False
        exit(1)

def Recv_From_Server(sock):
    try:
        while 1:
            # 每一次都先印出從Server收到的訊息
            recv_msg = sock.recv(BUFF_SIZE)
            print recv_msg
            # print '收到...\n' + recv_msg # 這行Debug很好用! 當初靠這行找到 "糊" 在一起的文字

            # 出於不明原因，這行滿重要的! 沒有這行的話傳大一點的PDF檔案會出現不明錯誤 (Download端檔案打不開)
            stdout.flush()


            # 被Server踢了
            if ('你的連線已被伺服器中斷' in recv_msg):
                connected = False
                break

            # 準備開始接收伺服器的檔案傳輸
            elif ('START OF FILE:' in recv_msg):
                # 首先拆解訊息，找出要接收的檔案名稱
                token = recv_msg.split()
                transfer_mode_file_name = token[-1]

                # 在自己的Download目錄下建立一個新的Binary檔案
                recv_file = open('/Users/JayChen/Downloads/' + transfer_mode_file_name, 'wb')
                print '新空白檔案開啟成功! 路徑:/Users/JayChen/Downloads/' + transfer_mode_file_name

                file_data = sock.recv(BUFF_SIZE)
                while('END OF FILE' not in file_data):
                    # Debug跟測試用
                    # print ('這邊收到----------')
                    # print file_data
                    # print ('這邊收到++++++++++')
                    recv_file.write(file_data)
                    file_data = sock.recv(BUFF_SIZE)

                # 接收完畢 關閉檔案
                recv_file.close()
                print ('客戶端接收檔案[%s]成功!' % transfer_mode_file_name)
                logging.info('客戶端接收檔案[%s]成功!' % transfer_mode_file_name)

            # 其他狀況，正常接收聊天訊息，直接將訊息存入Client_History
            else:
                logging.info(recv_msg)

    except socket.error:
        print('客戶端接收時發生未知錯誤!')
        print(socket.error)
        logging.warning('客戶端接收時發生未知錯誤!')
        logging.warning(socket.error)
        connected = False
        exit(1)


'''
    a -> address   (e.g., 127.0.0.1)
    p -> port      (e.g., 8888)
    u -> user name (e.g., Jay)
'''
def main(a, addr, p, port, u, user):
    HOST = addr      # Host IP為字串型態
    PORT = int(port) # command line輸入為字串型態，記得要轉int!

    #宣告一個socket，並且連線到(HOST, PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    connected = True # 記錄連接成功

    # 連接成功後第一件事，送出user_name
    sock.send(user)

    # 做出接收及傳送方的Thread
    recv_thread = threading.Thread(target= Recv_From_Server, args = (sock, ))  # Start receive thread from server
    recv_thread.start()
    send_thread = threading.Thread(target = Send_To_Server, args = (sock, ))  # Start send thread to server
    send_thread.start()

    try:
        while True:
            if (not connected):
                exit(1)
    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        print('----------------------------------')
        print '[%s]與伺服器連線中斷!' % user
        logging.warning("[%s]與伺服器連線中斷" % user)
        sock.close()


# 接收命令列參數 (e.g., -a 127.0.0.1 -p 8888 -u Jay )
main(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6])
