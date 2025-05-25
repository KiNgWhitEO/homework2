import socket
import tkinter as tk
from tkinter import messagebox, ttk


class ATMClientGUI:
    def __init__(self, master):
        self.balance_label = None
        self.main_frame = None
        self.pin_entry = None
        self.account_entry = None
        self.login_frame = None
        self.master = master
        master.title("ATM 系统")
        master.geometry("400x300")

        # Socket连接配置
        self.host = '127.0.0.1'
        self.port = 2525
        self.sock = None
        self.current_account = None
        self.authenticated = False

        # 创建登录界面
        self.create_login_frame()

    def connect_server(self):
        """建立服务器连接"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            messagebox.showerror("连接错误", f"无法连接到服务器: {str(e)}")
            return False

    def create_login_frame(self):
        """登录界面"""
        self.login_frame = ttk.Frame(self.master)
        self.login_frame.pack(pady=50)

        # 账号输入
        ttk.Label(self.login_frame, text="账号:").grid(row=0, column=0, padx=5, pady=5)
        self.account_entry = ttk.Entry(self.login_frame)
        self.account_entry.grid(row=0, column=1, padx=5, pady=5)

        # 密码输入
        ttk.Label(self.login_frame, text="密码:").grid(row=1, column=0, padx=5, pady=5)
        self.pin_entry = ttk.Entry(self.login_frame, show="*")
        self.pin_entry.grid(row=1, column=1, padx=5, pady=5)

        # 登录按钮
        login_btn = ttk.Button(
            self.login_frame,
            text="登录",
            command=self.perform_login
        )
        login_btn.grid(row=2, columnspan=2, pady=10)

    def create_main_interface(self):
        """主操作界面"""
        self.login_frame.destroy()

        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(pady=30)

        # 余额显示
        self.balance_label = ttk.Label(
            self.main_frame,
            text="当前余额: 加载中...",
            font=('Arial', 12)
        )
        self.balance_label.pack(pady=10)

        # 取款按钮
        withdraw_btn = ttk.Button(
            self.main_frame,
            text="取款",
            command=self.show_withdraw_dialog
        )
        withdraw_btn.pack(pady=5)

        # 刷新余额按钮
        refresh_btn = ttk.Button(
            self.main_frame,
            text="刷新余额",
            command=self.update_balance
        )
        refresh_btn.pack(pady=5)

        # 存款按钮
        deposit_btn = ttk.Button(
            self.main_frame,
            text="存款",
            command=self.show_deposit_dialog
        )
        deposit_btn.pack(pady=5)
        # 退出按钮
        exit_btn = ttk.Button(
            self.main_frame,
            text="退出系统",
            command=self.exit_system
        )
        exit_btn.pack(pady=10)

        # 初始化余额
        self.update_balance()

    def perform_login(self):
        """执行登录操作"""
        if not self.connect_server():
            return

        account = self.account_entry.get()
        pin = self.pin_entry.get()

        # 发送HELO命令
        self.sock.sendall(f"HELO sp {account}".encode())
        helo_res = self.sock.recv(1024).decode()

        if helo_res == "500 sp AUTH REQUIRED":
            # 发送PASS命令
            self.sock.sendall(f"PASS sp {pin}".encode())
            pass_res = self.sock.recv(1024).decode()

            if pass_res == "525 sp OK!":
                self.current_account = account
                self.authenticated = True
                self.create_main_interface()
            else:
                messagebox.showerror("错误", "密码错误！")
        else:
            messagebox.showerror("错误", "无效账号！")

    def show_withdraw_dialog(self):
        """显示取款对话框"""
        dialog = tk.Toplevel(self.master)
        dialog.title("取款操作")

        ttk.Label(dialog, text="取款金额:").pack(pady=5)
        amount_entry = ttk.Entry(dialog)
        amount_entry.pack(pady=5)

        def confirm_withdraw():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError
                self.process_withdraw(amount)
                dialog.destroy()
            except:
                messagebox.showerror("错误", "无效金额！")

        ttk.Button(dialog, text="确认", command=confirm_withdraw).pack(pady=5)

    def process_withdraw(self, amount):
        """处理取款操作"""
        self.sock.sendall(f"WDRA sp {amount}".encode())
        res = self.sock.recv(1024).decode()

        if res == "525 sp OK!":
            messagebox.showinfo("成功", "取款操作成功！")
            self.update_balance()
        else:
            messagebox.showerror("错误", "取款失败，余额不足！")

    def show_deposit_dialog(self):
        """显示存款对话框"""
        dialog = tk.Toplevel(self.master)
        dialog.title("存款操作")

        ttk.Label(dialog, text="存款金额:").pack(pady=5)
        amount_entry = ttk.Entry(dialog)
        amount_entry.pack(pady=5)

        def confirm_deposit():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError
                self.process_deposit(amount)
                dialog.destroy()
            except:
                messagebox.showerror("错误", "无效金额！")

        ttk.Button(dialog, text="确认", command=confirm_deposit).pack(pady=5)

    def process_deposit(self, amount):
        """处理存款操作"""
        self.sock.sendall(f"DEPO sp {amount}".encode())
        res = self.sock.recv(1024).decode()

        if res == "525 sp OK!":
            messagebox.showinfo("成功", "存款操作成功！")
            self.update_balance()
        else:
            messagebox.showerror("错误", "存款操作失败！")

    def update_balance(self):
        """更新余额显示"""
        self.sock.sendall(b"BALA")
        res = self.sock.recv(1024).decode()

        if res.startswith("AMNT:"):
            balance = res.split(":")[1]
            self.balance_label.config(text=f"当前余额: {balance} 元")
        else:
            messagebox.showerror("错误", "获取余额失败！")

    def exit_system(self):
        """退出系统"""
        self.sock.sendall(b"BYE")
        self.sock.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ATMClientGUI(root)
    root.mainloop()
