### 功能介绍
bilibili媒体下载工具
- 视频下载
- 封面下载
- 关注列表
- 支持交互式命令方式和http服务器方式使用
- 可以打包成windows可执行文件使用

#### 交互式命令使用
直接运行[bilitool-console.py](bilitool-console.py)，按照提示操作即可
- 需要python运行环境
- 首次运行需要下载ffmpeg(自动完成)

#### 使用http服务器
运行[bilitool-server.py](bilitool-server.py)，打开浏览器访问http://localhost:5000
- 需要python运行环境
- 首次运行需要下载ffmpeg(自动完成)

### 打包成windows可执行文件使用
1. 如果没有server.spec需要首先生成 `pyi-makespec --add-data "config/*.conf:config" --add-data "static:static" --add-data "templates:templates" --add-data "download:download" --icon=static/favicon.ico --windowed bilitool.py`
2. 编写server.spec
3. `pyinstaller bilitool.spec`
在dist目录可以找到可执行文件，不需要python环境，可以直接使用打包好的发布版本

### 技术选型
- flask: web服务器
- requests: 发送http请求
- beautiful soup: 解析html响应
- axois: 前端异步请求发送
- Vue: 前端框架
- tailwindcss: css框架，无需编译
- daisyui: 对tailwindcss的封装
- pywebview: 跨平台的桌面应用框架
- pyinstaller: 制作exe文件
### 免责声明
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