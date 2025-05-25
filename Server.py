"""服务端程序"""

from socket import *

IP = '0.0.0.0'

PORT = 2525

BUFLEN = 512

# 实例化socket对象
listenSocket = socket(AF_INET, SOCK_STREAM)

# 绑定地址和端口
listenSocket.bind((IP, PORT))

# 允许客户端连接
listenSocket.listen(3)
print(f'服务端启动成功，在{PORT}端口等待客户端连接...')

dataSocket, addr = listenSocket.accept()
print('接受一个客户端连接：', addr)

while True:
    recved = dataSocket.recv(BUFLEN)

    # 返回为空，关闭连接
    if not recved:
        break
    info = recved.decode()
    print(f'收到客户端信息:{info}')

    dataSocket.send(f'服务端接收信息{info}'.encode())

dataSocket.close()
listenSocket.close()
