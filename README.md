# 北京交通大学校园网自动登录器

一个自动监控和重新连接北京交通大学校园网的Python工具。当网络连接断开时，程序会自动触发重新认证，无需手动干预。

## 功能特性

- ✅ 自动监控网络连接状态
- ✅ 网络断开时自动重新认证
- ✅ 可配置检查间隔
- ✅ 详细的运行日志记录
- ✅ 异常处理和错误报告

## 环境要求

- Python 3.6 或更高版本
- 依赖库：
  - `requests` - HTTP请求库

## 安装和配置

### 1. 克隆或下载项目

```bash
git clone https://github.com/wulingfeng321/bjtu-campus-login.git
cd bjtu-campus-login
```

### 2. 安装依赖

```bash
pip install requests
```

### 3. 配置文件

编辑 `config.json` 文件，填入你的学号和密码：

```json
{
    "username": "你的学号",
    "password": "你的密码",
    "check_interval": 60
}
```

**配置参数说明：**

| 参数             | 说明               | 类型   | 默认值 |
| ---------------- | ------------------ | ------ | ------ |
| `username`       | 你的学号/账号      | 字符串 | 必填   |
| `password`       | 你的密码           | 字符串 | 必填   |
| `check_interval` | 网络检查间隔（秒） | 整数   | 60     |

## 使用方法（Windows）

### 方法一（自启动脚本）

#### 1. 创建启动脚本

创建文件：

```text
start_login.bat
```

内容如下：

```bat
@echo off

cd /d D:\bjtu-campus-login

python login.py
```

> 请将 `D:\bjtu-campus-login` 修改为实际项目目录。
> 该文件已创建好，可使用记事本进行编辑

#### 2. 添加到启动文件夹

按下：

```text
Win + R
```

输入：

```text
shell:startup
```

打开 Windows 启动文件夹后，将：

```text
start_login.bat
```

复制到该目录。

以后每次：

```text
开机
↓
用户登录 Windows
↓
自动启动 login.py
```

### 方法二（后台运行）

#### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

#### 2. 打包为 exe

在项目目录执行：

```bash
pyinstaller -F login.py
```

生成：

```text
dist/login.exe
```

#### 3. 创建计划任务

打开：

```text
任务计划程序
```

创建任务：

##### 触发器

```text
登录时
```

##### 操作

```text
启动程序
```

选择：

```text
dist/login.exe
```

##### 勾选

```text
无论用户是否登录都运行
```

完成后程序将在后台自动运行。

## 使用方法（树莓派）

### 1. 安装依赖

更新系统：

```bash
sudo apt update
```

安装 requests：

```bash
pip3 install requests
```

假设项目目录为：

```text
/home/pi/bjtu-campus-login
```

---

### 2. 创建 systemd 服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/bjtu-campus.service
```

内容如下：

```ini
[Unit]
Description=BJTU Campus Login
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/bjtu-campus-login

ExecStart=/usr/bin/python3 /home/pi/bjtu-campus-login/login.py

Restart=always

User=pi

[Install]
WantedBy=multi-user.target
```

保存退出。

---

### 3. 启用服务

刷新 systemd：

```bash
sudo systemctl daemon-reload
```

设置开机自启：

```bash
sudo systemctl enable bjtu-campus.service
```

立即启动：

```bash
sudo systemctl start bjtu-campus.service
```

---

### 4. 查看运行状态

查看服务状态：

```bash
sudo systemctl status bjtu-campus.service
```

查看实时日志：

```bash
journalctl -u bjtu-campus.service -f
```

停止服务：

```bash
sudo systemctl stop bjtu-campus.service
```

重启服务：

```bash
sudo systemctl restart bjtu-campus.service
```

禁止开机启动：

```bash
sudo systemctl disable bjtu-campus.service
```

## 文件说明

| 文件          | 说明                         |
| ------------- | ---------------------------- |
| `login.py`    | 主程序文件                   |
| `config.json` | 配置文件，包含账号密码等配置 |
| `campus.log`  | 运行日志文件（程序自动生成） |
| `README.md`   | 本说明文档                   |

## 工作原理

1. **启动阶段**：程序读取配置文件中的用户信息
2. **监控循环**：程序进入无限循环
3. **网络检测**：每个间隔周期内，程序尝试访问百度来检测网络连接
4. **重新认证**：
   - 若网络正常，则继续等待
   - 若网络断开，程序会：
     - 获取本地IP地址
     - 向校园网认证服务器发送登录请求
     - 记录认证结果
5. **日志记录**：所有操作都会记录在 `campus.log` 文件中

## 日志示例

```
[2026-06-07 14:30:15] 北京交通大学校园网自动登录器启动
[2026-06-07 14:31:20] 网络断开，开始重新认证
[2026-06-07 14:31:22] 认证成功
[2026-06-07 14:32:25] 登录异常：Connection timeout
```

## 常见问题

### Q: 程序启动后没有反应？

A: 这是正常的。程序会在后台持续运行。可以查看 `campus.log` 文件来验证程序是否正在运行。

### Q: 如何查看程序的运行状态？

A: 打开 `campus.log` 文件，查看最近的日志记录。

### Q: 提示"认证失败"是什么原因？

A: 常见原因包括：

- 学号或密码错误，请检查 `config.json` 配置
- 网络问题，尝试手动登录校园网
- 服务器问题，稍后重试

### Q: 怎样停止程序？

A: 在运行程序的终端中按 `Ctrl + C` 或关闭终端窗口。

### Q: 如何修改掉线检查间隔？

A: 修改 `config.json` 中的 `check_interval` 值（单位：秒）。

## 故障排除

### 导入错误：`ModuleNotFoundError: No module named 'requests'`

**解决方案**：安装requests库

```bash
pip install requests
```

### 连接超时错误

**解决方案**：

- 检查网络连接是否正常
- 尝试增加 `check_interval` 值
- 确认校园网服务器是否可访问

### 认证服务器返回异常

**解决方案**：

- 检查认证服务器地址是否正确
- 查看 `campus.log` 获取详细错误信息
- 尝试手动访问 `http://10.10.42.3` 测试服务器

## 其他

**最后更新**：2026年6月7日

