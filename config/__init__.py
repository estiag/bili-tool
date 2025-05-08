# 获取当前脚本所在的目录
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# 找到项目根目录
project_dir = os.path.dirname(script_dir)

# user conf file
user_conf = f'{project_dir}/config/user.conf'
if not os.path.exists(user_conf):
    with open(user_conf, 'wb') as f:
        f.write(b'[user]\n')
        f.write(b'bilibili_cookie =\n')
        f.write(b'bilibili_current_vmid =\n')
