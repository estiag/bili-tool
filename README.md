# 📌 项目简介

BiliTool 是一款功能强大的哔哩哔哩媒体下载工具，支持多种使用方式，满足不同用户需求。Windows 用户可直接下载发行版使用，开发者也可基于源码进行二次开发。

# 🚀 主要功能

    视频下载 - 支持多种清晰度选择

    封面下载 - 一键保存视频封面图

    关注列表 - 查看关注UP主

    文件预览 - 下载前预览媒体内容

    多模式使用：

        交互式命令行界面

        HTTP 网页服务

        打包成独立Windows应用

# 安装与使用

## 直接使用（推荐普通用户）

    下载最新发行版本

    解压压缩包

    运行 bilitool.exe

    默认下载路径：_internal/download/bilibili/video（可在设置中修改）

## 开发者模式
### 注意
Linux用户需额外安装FFmpeg `sudo apt install ffmpeg`
MacOS用户需额外安装FFmpeg `brew install ffmpeg`, 如果没有homeBrew需要安装`/bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"`

### 克隆仓库

```bash
git clone https://github.com/your-repo/bilitool.git
cd bilitool
```

### 安装依赖

```bash
pip install -r requirements.txt
```

1. 命令行交互模式

```bash
python bilitool-console.py
```


2. HTTP服务器模式

```bash
python bilitool-server.py
```

访问 http://localhost:5000 使用网页界面

# 打包Windows应用
注意: 需要安装pyinstaller `pip install pyinstaller`

1. 生成spec文件
   `pyi-makespec --add-data "config/*.conf:config" --add-data "static:static" --add-data "templates:templates" --add-data "download:download" --add-data "ffmpeg:ffmpeg" --icon=static/favicon.ico --windowed bilitool.py`

2. 编译打包
   `pyinstaller bilitool.spec`

打包完成后，可在 dist 目录找到可执行文件。

可以使用[build.bat](build.bat)(Windows)、 [build.sh](build.sh)(Linux/Mac) 打包，会自动清除不必要文件

# 免责声明

1. 版权声明‌
   本工具仅供个人学习、研究和合法用途使用。下载的视频、音频等内容版权归哔哩哔哩（Bilibili）及原作者所有。
   请遵守《中华人民共和国著作权法》及相关法律法规，‌禁止用于商业用途或未经授权的传播‌。

2. 使用限制‌
   用户需确保下载的内容符合哔哩哔哩平台的《用户协议》和《社区规则》。
   禁止下载、传播涉及敏感、违法或侵权的内容（如盗版、暴力、色情等）。

3. 免责条款‌
   本工具为免费开源项目，开发者‌不承担‌因用户滥用导致的任何法律责任。
   使用本工具产生的所有行为及后果由用户自行负责，与开发者无关。
   哔哩哔哩官方若更新技术限制导致工具失效，开发者不保证长期兼容性。

4. 隐私保护‌
   本工具不会收集、存储或泄露用户的哔哩哔哩账号、密码等隐私信息。

5. 风险提示‌
   滥用下载工具可能导致哔哩哔哩账号封禁、IP限制或其他法律风险，请谨慎使用

# 技术栈

- flask: web服务器
- requests: 发送http请求
- beautiful soup: 解析html响应
- axois: 前端异步请求发送
- Vue: 前端框架
- tailwindcss: css框架，无需编译
- daisyui: 对tailwindcss的封装
- pywebview: 跨平台的桌面应用框架
- pyinstaller: 制作exe文件
- rivulet: 一个链式http处理库 https://gitee.com/estiag/rivulet.git

# 常见问题
### MacOS找不到命令`pyi-makespec` `pyinstaller`
需要安装pyinstaller后设置环境变量 ：执行`nano ~/.zshrc` 在文件末尾添加python的bin目录，执行`source ~/.zshrc`
### pyinstaller制作可执行文件时报错：ERROR: Unable to find '/Users/estiag/bili-tool/download' when adding binary and data files.
手动创建一个在项目根目录download目录
### pyinstaller制作可执行文件时报错：ModuleNotFoundError: No module named 'PIL'
安装 Pillow 库`pip install pillow`
### 出现无限调用main
https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing