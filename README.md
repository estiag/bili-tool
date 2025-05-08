### 功能介绍
python写的工具包，功能有

基于requests的API测试框架
- 链式调用
- 并发请求

随机工具类
- 支持均匀分布和正态分布

bilibili工具
- 视频下载
- 封面下载
- 关注列表
- 支持交互式命令方式和http服务器方式使用
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
### 制作exe
1. 如果没有[server.spec](server.spec)需要首先生成 `pyi-makespec --add-data "config/*.conf:config" --add-data "static:static" --add-data "templates:templates" --add-data "download:download" --add-data "log:log" --windowed server.py`
2. 编写[server.spec](server.spec)
3. `pyinstaller server.spec`
### 参考链接
- bilibili API https://socialsisteryi.github.io/bilibili-API-collect/#%F0%9F%8D%B4%E7%9B%AE%E5%BD%95