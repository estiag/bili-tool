from multiprocessing import freeze_support

from bilitool import start_server

if __name__ == "__main__":
    freeze_support()
    # 仅启动flask
    start_server()