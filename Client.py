# coding=utf-8
import socket
import logging
from sys import argv, stdout, exit
from threading import Thread

logging.basicConfig(level = logging.INFO, filename = 'Client_History.log',
                    format = '[%(levelname)s] %(asctime)s %(threadName)s %(message)s', )
BUFF_SIZE = 2048

def Send_To_Server(sock):
    try:
        while 1:
            msg = raw_input()

            # 若client要傳送檔案
            if ('3' == msg[0]):
                sock.send(msg) # 首先將命令送出去給server! e.g., 3 jay /usr/file.txt

                token = msg.split()
                #user_name = token[1]
                file_path = token[2]
                file = open(file_path, 'rb')

                fr = file.read(BUFF_SIZE)
                while(fr):
                    sock.sendall(fr)
                    fr = file.read(BUFF_SIZE)
                file.close()

                print '客戶端檔案傳輸成功!'
                sock.sendall('END OF FILE') # 告訴接收端伺服器，檔案傳輸結束! 否則伺服器不知道何時結束寫檔!

            # 正常傳送指令
            else:
                sock.send(msg)

    except:
        print('傳送時發生未知錯誤!')
        logging.warning('傳送時發生未知錯誤!')
        sock.close()
        exit(1)

def Recv_From_Server(sock):
    try:
        print sock.recv(BUFF_SIZE) # 進入聊天室
        while 1:
            msg = sock.recv(BUFF_SIZE)
            print msg
            logging.info(msg)
            stdout.flush()

    except:
        print('接收時發生未知錯誤!')
        logging.warning('接收時發生未知錯誤!')
        sock.close()
        exit(1)


def main():
    HOST = '127.0.0.1'
    PORT = 9999

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    connected = True

    recv_thread = Thread(target = Recv_From_Server, args = (sock, ))  # Start receive thread from server
    recv_thread.start()
    send_thread = Thread(target = Send_To_Server, args = (sock, ))  # Start send thread to server
    send_thread.start()

    try:
        while True:
            if (not connected):
                exit(1)                                         #Exit on Keyboard Interrupt
    except (KeyboardInterrupt, SystemExit):
        stdout.flush()
        print '\n與伺服器連線中斷'                  #Close server
        logging.warning("與伺服器連線中斷")
        sock.close()

main()
