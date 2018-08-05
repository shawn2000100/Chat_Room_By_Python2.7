# coding=utf-8
import socket
import logging
import threading
from sys import argv, stdout, exit


logging.basicConfig(level = logging.INFO, filename = 'Client_History.log',
                    format = '[%(levelname)s] %(asctime)s %(threadName)s %(message)s', )
BUFF_SIZE = 2048
connected = False

def Send_To_Server(sock):
    try:
        while 1:
            msg = raw_input()

            # 若client要傳送檔案
            if ('3' == msg[0]):
                sock.send(msg) # 首先將命令送出去給server!! e.g., 3 /usr/file.txt dest_user

                token = msg.split()
                file_path = token[1]
                file = open(file_path, 'rb')

                fr = file.read(BUFF_SIZE)
                while(fr):
                    sock.sendall(fr)
                    fr = file.read(BUFF_SIZE)
                file.close()

                print '客戶端檔案傳輸成功! 請輸入 \'END OF FILE\' 來結束傳輸'
            # 正常傳送指令
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
        print sock.recv(BUFF_SIZE) # 進入聊天室
        while 1:
            recv_msg = sock.recv(BUFF_SIZE)
            print recv_msg

            if(recv_msg == '你的連線已被伺服器中斷'):
                connected = False
                break

            logging.info(recv_msg)
            stdout.flush()

    except socket.error:
        print('客戶端接收時發生未知錯誤!')
        print(socket.error)
        logging.warning('客戶端接收時發生未知錯誤!')
        logging.warning(socket.error)
        connected = False
        exit(1)


def main(a, addr, p, port, u, user):
    HOST = addr
    PORT = int(port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    connected = True

    sock.send(user)  # 送出user_name

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
        print '\n與伺服器連線中斷'                  #Close server
        logging.warning("與伺服器連線中斷")
        sock.close()


main(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6])
