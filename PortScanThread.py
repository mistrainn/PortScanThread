import socket
import threading
from queue import Queue
import argparse
import sys

name_art = r"""
 ██▓     █    ██     ███▄ ▄███▓ ██▓ ███▄    █   ▄████      █████▒▓█████  ██▓
▓██▒     ██  ▓██▒   ▓██▒▀█▀ ██▒▓██▒ ██ ▀█   █  ██▒ ▀█▒   ▓██   ▒ ▓█   ▀ ▓██▒
▒██░    ▓██  ▒██░   ▓██    ▓██░▒██▒▓██  ▀█ ██▒▒██░▄▄▄░   ▒████ ░ ▒███   ▒██▒
▒██░    ▓▓█  ░██░   ▒██    ▒██ ░██░▓██▒  ▐▌██▒░▓█  ██▓   ░▓█▒  ░ ▒▓█  ▄ ░██░
░██████▒▒▒█████▓    ▒██▒   ░██▒░██░▒██░   ▓██░░▒▓███▀▒   ░▒█░    ░▒████▒░██░
░ ▒░▓  ░░▒▓▒ ▒ ▒    ░ ▒░   ░  ░░▓  ░ ▒░   ▒ ▒  ░▒   ▒     ▒ ░    ░░ ▒░ ░░▓  
░ ░ ▒  ░░░▒░ ░ ░    ░  ░      ░ ▒ ░░ ░░   ░ ▒░  ░   ░     ░       ░ ░  ░ ▒ ░
  ░ ░    ░░░ ░ ░    ░      ░    ▒ ░   ░   ░ ░ ░ ░   ░     ░ ░       ░    ▒ ░
    ░  ░   ░               ░    ░           ░       ░               ░  ░ ░  

"""


def welcome_message():
    print("\n\n\n\n")
    print("-----------欢迎使用批量扫描目标端口脚本！-----------")
    print(name_art)
    print("\n")
    print("使用 -u 参数扫描单个网站")
    print("使用 -f 参数扫描文件中的网站")
    print("使用 -t 参数设置扫描的线程")
    print("\n")


def scan_port(url, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET代表 ipv4，SOCK_STREAM代表 TCP连接
    server.settimeout(5)  # 设置超时时间，以免卡死
    try:
        connection = server.connect_ex((url, port))  # 与connect用法类似，区别为返回错误时不引发错误异常，而是返回错误码
        if connection == 0:  # 返回值为 0 时，正常连接
            result = f"{url}的{port}端口开放！\n"
            print(result)
            with open('./result.txt', "a+") as f:
                f.write(result)
        else:
            print(f"{url}的{port}端口不开放！\n")
    except Exception as e:
        print(f"Error scanning port {port}: {e}")
    finally:
        server.close()


def worker(url, port_queue):
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(url, port)
        port_queue.task_done()


def main(url, num_threads=20):
    port_queue = Queue()
    for i in range(1, 1001):
        port_queue.put(i)

    # 启动用户输入线程数的线程，进行队列的扫描
    for _ in range(num_threads):  # 用_作变量，代表在循环中不会使用。
        t = threading.Thread(target=worker, args=(url, port_queue))
        t.daemon = True  # 设置守护线程，确保主进程在所有子线程执行完成后退出
        t.start()

    port_queue.join()  # 这个方法会阻塞主线程，直到队列中的所有任务都已经完成。


def process_file(file_path, num_threads):
    with open(file_path, 'r') as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()
        print(f"扫描 {url}:")
        main(url, num_threads)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        welcome_message()
        args_str = input("请输入参数（例如：'-u 127.0.0.1'）：")
        args = args_str.split()
    else:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="端口扫描器")
    parser.add_argument("-t", "--threads", type=int, default=20, help="线程数量，默认为20")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", type=str, help="包含URL的文件")
    group.add_argument("-u", "--url", type=str, help="单个URL地址")

    args = parser.parse_args(args)     # 读取命令行中输入的参数

    if args.file:
        process_file(args.file, args.threads)
    else:
        main(args.url, args.threads)
