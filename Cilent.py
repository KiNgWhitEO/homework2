from socket import *

IP = '192.168.43.115'

SERVER_PORT = 2525
BUFLEN = 1024

# 实例化socket
dataSocket = socket(AF_INET, SOCK_STREAM)

# 连接服务器socket
dataSocket.connect((IP, SERVER_PORT))

while True:
    # 从终端读入用户输入的字符串
    toSend = input('>>>')
    if toSend == '':
        break
    dataSocket.send(toSend.encode())

# 等待接收服务端的消息
    recved = dataSocket.recv(BUFLEN)
# 如果返回空
    if not recved:
        break

    print(recved.decode())

dataSocket.close()
