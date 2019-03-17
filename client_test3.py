#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：client_test1.py
import socket
import queue
import threading
import time

data_size = 1024


class ClientNode:

    def __init__(self):
        """
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ready = False  # 准备状态
        self.send_q = queue.Queue(10)

    def connect(self, host, port):
        self.server_socket.connect((host, port))
        return self.server_socket

    def prepare_net(self):
        while not self.ready:
            data = self.server_socket.recv(1024)
            print(data.decode("utf-8"))
            if data.decode("utf-8") == "OK":
                self.ready = True

    def send_data(self, send_q):
        if self.ready:
            if not send_q.empty():
                # send_lock.acquire()
                loss = send_q.get()
                print("发送数据", loss)
                self.server_socket.send(str(loss).encode("utf-8"))
                time.sleep(0.1)
                # send_lock.release()

    def rec_data(self, rec_q):
        if self.ready:
            data = self.server_socket.recv(data_size)
            if data:
                p = data.decode("utf-8")
                rec_q.put(float(p))
                print("接受数据：", p)

    def close(self):
        self.server_socket.close()


class SendThread(threading.Thread):
    def __init__(self, name, send_client, send_q):
        threading.Thread.__init__(self)
        self.name = name
        self.send_client = send_client
        self.send_q = send_q

    def run(self):
        print("开启线程：" + self.name)
        send_thread_fun(self.send_client, self.send_q)
        print("退出线程：" + self.name)


class RecThread(threading.Thread):
    def __init__(self, name, rec_client, rec_q):
        threading.Thread.__init__(self)
        self.name = name
        self.rec_client = rec_client
        self.rec_q = rec_q

    def run(self):
        print("开启线程：" + self.name)
        while True:
            receive_thread_fun(self.rec_client, self.rec_q)


def send_thread_fun(send_client, send_q):
    while True:
        send_client.send_data(send_q)


def receive_thread_fun(rec_client, rec_q):
    while True:
        rec_client.rec_data(rec_q)

    """ 定义存放发送和接受的队列"""


send_data = queue.Queue()
rec_data = queue.Queue()

client = ClientNode()
client.connect("127.0.0.1", 12347)
client.prepare_net()
for index in range(10, 20):
    send_data.put(index)
send_thread = SendThread("客户端发进程", client, send_data)
send_thread.start()
rec_thread = RecThread("客户端收进程", client, rec_data)
rec_thread.start()