这是一个用于生成Windows Sandbox WSB文件的脚本工具。

![](wsbgen.png)

# 编译启动器

## 编译

Windows下安装[MSYS2](https://www.msys2.org/),使用`MSYS2 UCRT64`终端

```
$ make
使用方法：
  make all       - 构建目标可执行文件。
  make clean     - 清理生成的文件。
  make help      - 显示此帮助菜单。
```

# 运行

## 环境依赖

```cmd
python -m venv env
env\Scripts\activate.bat
pip install -r requirements.txt
```

## 运行

### 方式一

如果您的python环境或者虚拟环境已经安装`python3`+`PySide6`

```cmd
pythonw WSBGen.py
```

### 方式二

编译启动器`make all`,然后双击编译出来的程序` WSBGen.exe`，启动器会优先调用当前目录下`env`虚拟环境，如果不存在此虚拟环境直接使用系统默认python环境

### 导出WSB文件

直接点击按钮`导出WSB文件`,默认的wsb直接可用，同时生成相应文件和目录。

```bash
$ tree
.
├── FileName.wsb      #沙盒启动文件，详细请查看文件
├── LogonCommand
│   ├── ipconfig.reg  #桌面右键添加：获取沙盒环境IPv4 地址，详细请查看文件
│   ├── wsb-setup.cmd #沙盒环境启动时运行的dos命令，详细请查看文件
│   └── wsb-setup.ps1 #沙盒环境启动时运行的powershell命令，详细请查看文件
├── WSBGen.exe		  #启动器，用于启动main.py，详细请查看文件
├── config.db         #程序配置数据存储在sqlite数据库中，默认文件，详细请查看文件,推荐使用DB Browser for SQLite
└── main.py			  #主程序，可以单独作为python脚本运行，也可以用WSBGen.exe启动，详细请查看文件

2 directories, 7 files
```



# 获取沙盒IP

`win`+`R` 运行`powershell`

```powershell
wsb ip --id (wsb list)
```



