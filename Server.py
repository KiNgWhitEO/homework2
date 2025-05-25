import socket
import threading


class ATMService:
    def __init__(self):
        # 初始化用户数据
        self.users = {
            'user': {'pin': '123456', 'balance': 500000.0}
        }
        # 线程锁保证账户操作安全
        self.lock = threading.Lock()

    def verify_user(self, account, pin):
        """验证用户身份"""
        user = self.users.get(account)
        return user and user['pin'] == pin

    def get_balance(self, account):
        """获取账户余额"""
        return self.users.get(account, {}).get('balance', 0.0)

    def withdraw(self, account, amount):
        """处理取款操作"""
        with self.lock:  # 保证线程安全
            if self.users[account]['balance'] >= amount:
                self.users[account]['balance'] -= amount
                return True
            return False

    def deposit(self, account, amount):
        """处理存款操作"""
        with self.lock:
            try:
                if amount <= 0:
                    return False
                self.users[account]['balance'] += amount
                return True
            except:
                return False


class ATMServer:
    def __init__(self, host='127.0.0.1', port=2525):
        self.host = host
        self.port = port
        self.service = ATMService()
        # 创建TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        """启动服务器"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"服务器已启动，监听地址：{self.host}:{self.port}")

        while True:
            # 接受客户端连接
            conn, addr = self.server_socket.accept()
            print(f"接收到来自 {addr} 的连接")
            # 为每个客户端创建新线程
            client_thread = threading.Thread(target=self.handle_client, args=(conn,))
            client_thread.start()

    def handle_client(self, conn):
        """处理客户端请求"""
        current_account = None  # 当前处理的账户
        authenticated = False  # 认证状态

        try:
            while True:
                # 接收客户端数据
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                parts = data.split()
                if not parts:  # 空命令处理
                    conn.sendall(b"401 sp ERROR!")
                    continue

                command = parts[0]  # 解析命令类型

                # 处理HELO命令
                if command == "HELO":
                    if len(parts) != 3 or parts[1] != "sp":
                        conn.sendall(b"401 sp ERROR!")
                        continue

                    current_account = parts[2]
                    # 检查账户是否存在
                    if current_account in self.service.users:
                        conn.sendall(b"500 sp AUTH REQUIRED")
                    else:
                        conn.sendall(b"401 sp ERROR!")
                        current_account = None

                # 处理PASS命令
                elif command == "PASS":
                    if not current_account or len(parts) != 3 or parts[1] != "sp":
                        conn.sendall(b"401 sp ERROR!")
                        continue

                    pin = parts[2]
                    # 验证PIN码
                    if self.service.verify_user(current_account, pin):
                        authenticated = True
                        conn.sendall(b"525 sp OK!")
                    else:
                        conn.sendall(b"401 sp ERROR!")
                        authenticated = False

                # 处理BALA命令
                elif command == "BALA":
                    if not authenticated:
                        conn.sendall(b"401 sp ERROR!")
                        continue

                    # 返回账户余额    
                    balance = self.service.get_balance(current_account)
                    conn.sendall(f"AMNT:{balance}".encode())

                # 处理WDRA命令
                elif command == "WDRA":
                    if not authenticated or len(parts) != 3 or parts[1] != "sp":
                        conn.sendall(b"401 sp ERROR!")
                        continue

                    try:  # 取款金额
                        amount = float(parts[2])
                        if amount <= 0:
                            raise ValueError
                    except:
                        conn.sendall(b"401 sp ERROR!")
                        continue

                    # 执行取款操作    
                    if self.service.withdraw(current_account, amount):
                        conn.sendall(b"525 sp OK!")
                    else:
                        conn.sendall(b"401 sp ERROR!")

                # 处理BYE命令
                elif command == "BYE":
                    conn.sendall(b"BYE")
                    break
                elif command == "DEPO":  # 存款命令处理
                    if not authenticated or len(parts) != 3 or parts[1] != "sp":
                        conn.sendall(b"401 sp ERROR!")
                        continue

                    try:
                        amount = float(parts[2])
                        if amount <= 0:
                            raise ValueError
                    except:
                        conn.sendall(b"401 sp ERROR!")
                        continue

                    if self.service.deposit(current_account, amount):
                        conn.sendall(b"525 sp OK!")
                    else:
                        conn.sendall(b"401 sp ERROR!")

        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            conn.close()
            print("连接已关闭")


if __name__ == "__main__":
    server = ATMServer()
    server.start()
