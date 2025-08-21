"""
项目名称：WSBGen
作者：Bruce Lu
联系：https://luxiaoyou.com/contact.html
描述：这是一个用于生成Windows Sandbox WSB文件的工具。
"""
import sys
import os
import compileall
import sqlite3
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QSpinBox,
                               QCheckBox, QPushButton, QMessageBox, QTableWidget,
                               QTableWidgetItem, QHeaderView, QToolBar, QFileDialog,QDialog)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Sandbox WSB 生成器")
        self.resize(700, 600)

        # 初始化程序所在目录路径
        self.root = Path(__file__).parent

        # 初始化数据库
        self.db_path = self.root / "config.db"
        self.init_db()
        self.load_cfg_from_db()
        self.init_logon_command_file()

        self.init_ui()

    def init_db(self):
        """初始化数据库，创建表并加载默认配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT
                )
            """)
            # 插入默认配置
            default_cfg = {
                "audio": "True",
                "video": "False",
                "vgpu": "True",
                "memory": "8192",
                "logon": r"C:\LogonCommand\wsb-setup.cmd",
                "clipboard_redirection": "True",  
                "printer_redirection": "False",  
                "protected_client": "True",  
                "networking": "True",
                "folder_host_0": "LogonCommand",
                "folder_sandbox_0": r"C:\LogonCommand",
                "folder_readonly_0": "True"
            }
            for key, value in default_cfg.items():
                cursor.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
    def init_logon_command_file(self):
        """初始化LogonCommand目录和执行文件"""

        # 定义文件路径
        cmd_file_path = self.root / r"LogonCommand\wsb-setup.cmd"
        reg_file_path = self.root / r"LogonCommand\ipconfig.reg"
        ps1_file_path = self.root / r"LogonCommand\wsb-setup.ps1"

        cmd_file_content=r'''powershell.exe -executionpolicy bypass -file C:\LogonCommand\wsb-setup.ps1
reg import C:\LogonCommand\ipconfig.reg'''

        reg_file_content=r'''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\background\shell\Get Sandbox IPv4\command]
@="cmd.exe /k ipconfig"'''
        
        ps1_file_content=r'''$LanguageList = Get-WinUserLanguageList;
$LanguageList.Add("zh-Hans-CN")
Set-WinUserLanguageList $LanguageList -Force'''

        # 判断文件是否存在
        if not os.path.exists(cmd_file_path):
            # 如果文件不存在，则创建文件夹路径（如果需要）
            os.makedirs(os.path.dirname(cmd_file_path), exist_ok=True)
            # 创建文件并写入内容
            with open(cmd_file_path, "w") as file:
                file.write(cmd_file_content)
            with open(reg_file_path, "w") as file:
                file.write(reg_file_content)
            with open(ps1_file_path, "w") as file:
                file.write(ps1_file_content)
        else:
            pass

    def load_cfg_from_db(self):
        """从数据库加载配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            rows = cursor.fetchall()
            self.cfg = {row[0]: row[1] for row in rows}

    def save_cfg_to_db(self):
        """将配置保存到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            self.cfg["audio"] = str(self.chk_audio.isChecked())
            self.cfg["video"] = str(self.chk_video.isChecked())
            self.cfg["vgpu"] = str(self.chk_vgpu.isChecked())
            self.cfg["memory"] = str(self.spin_mem.value())
            self.cfg["logon"] = self.edit_cmd.text()
            self.cfg["clipboard_redirection"] = str(self.chk_clipboard.isChecked())  
            self.cfg["printer_redirection"] = str(self.chk_printer.isChecked())  
            self.cfg["protected_client"] = str(self.chk_protected.isChecked())  
            self.cfg["networking"] = str(self.chk_networking.isChecked())  
            for key, value in self.cfg.items():
                cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def init_ui(self):
        central = QWidget()
        lay = QVBoxLayout(central)

        # 工具栏
        bar = QToolBar()
        self.addToolBar(bar)
        bar.addAction("导出WSB文件", self.export_wsb)
        bar.addAction("联系作者", self.show_about_me_dialog)

        # 基本设置
        base = QVBoxLayout()
        self.chk_audio = QCheckBox("启用音频输入")
        self.chk_audio.setChecked(self.cfg["audio"] == "True")
        self.chk_video = QCheckBox("启用视频输入")
        self.chk_video.setChecked(self.cfg["video"] == "True")
        self.chk_vgpu = QCheckBox("启用 vGPU")
        self.chk_vgpu.setChecked(self.cfg["vgpu"] == "True")
        self.spin_mem = QSpinBox()
        self.spin_mem.setRange(512, 32768)
        self.spin_mem.setValue(int(self.cfg["memory"]))
        self.edit_cmd = QLineEdit(self.cfg["logon"])

        self.chk_clipboard = QCheckBox("启用剪贴板重定向")
        self.chk_clipboard.setChecked(self.cfg["clipboard_redirection"] == "True")
        self.chk_printer = QCheckBox("启用打印机重定向")
        self.chk_printer.setChecked(self.cfg["printer_redirection"] == "True")
        self.chk_protected = QCheckBox("启用受保护客户端")
        self.chk_protected.setChecked(self.cfg["protected_client"] == "True")
        self.chk_networking = QCheckBox("启用网络功能")
        self.chk_networking.setChecked(self.cfg["networking"] == "True")

        base.addWidget(QLabel("基本选项"))
        base.addWidget(self.chk_audio)
        base.addWidget(self.chk_video)
        base.addWidget(self.chk_vgpu)
        base.addWidget(self.chk_clipboard)  
        base.addWidget(self.chk_printer)  
        base.addWidget(self.chk_protected)  
        base.addWidget(self.chk_networking)  
        base.addWidget(QLabel("内存(MB，1024M=1G):"))
        base.addWidget(self.spin_mem)
        base.addWidget(QLabel("启动脚本:"))
        base.addWidget(self.edit_cmd)
        lay.addLayout(base)

        # 映射文件夹表格
        lay.addWidget(QLabel("映射文件夹"))
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["主机路径", "沙盒路径", "只读"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.table)

        btn_lay = QHBoxLayout()
        btn_add = QPushButton("添加")
        btn_del = QPushButton("删除")
        btn_add.clicked.connect(self.add_row)
        btn_del.clicked.connect(self.del_row)
        btn_lay.addWidget(btn_add)
        btn_lay.addWidget(btn_del)
        lay.addLayout(btn_lay)

        self.setCentralWidget(central)

        # 加载映射文件夹
        self.load_folders_from_db()

    def load_folders_from_db(self):
        """从数据库加载映射文件夹"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config WHERE key LIKE 'folder_%'")
            rows = cursor.fetchall()
            folders = {}
            for row in rows:
                key, value = row
                if key.startswith("folder_host_"):
                    folder_id = key[11:]
                    folders[folder_id] = {"host": value}
                elif key.startswith("folder_sandbox_"):
                    folder_id = key[14:]
                    folders[folder_id]["sandbox"] = value
                elif key.startswith("folder_readonly_"):
                    folder_id = key[15:]
                    folders[folder_id]["readonly"] = value == "True"

        self.table.setRowCount(len(folders))
        for row, folder in enumerate(folders.values()):
            self.table.setItem(row, 0, QTableWidgetItem(folder["host"]))
            self.table.setItem(row, 1, QTableWidgetItem(folder["sandbox"]))
            chk = QTableWidgetItem()
            chk.setCheckState(Qt.Checked if folder["readonly"] else Qt.Unchecked)
            self.table.setItem(row, 2, chk)

    def save_folders_to_db(self):
        """将映射文件夹保存到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM config WHERE key LIKE 'folder_%'")
            for row in range(self.table.rowCount()):
                host = self.table.item(row, 0).text()
                sandbox = self.table.item(row, 1).text()
                readonly = self.table.item(row, 2).checkState() == Qt.Checked
                cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (f"folder_host_{row}", host))
                cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (f"folder_sandbox_{row}", sandbox))
                cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (f"folder_readonly_{row}", str(readonly)))
            conn.commit()

    def export_wsb(self):
        self.save_cfg_to_db()
        self.save_folders_to_db()
        xml = self.build_xml()
        out_path, _ = QFileDialog.getSaveFileName(self, "保存 WSB 文件", str(Path.cwd() / "FileName.wsb"),
                                                  "WSB Files (*.wsb)")
        if not out_path:
            return
        try:
            Path(out_path).write_text(xml, encoding="utf-8")
            QMessageBox.information(self, "成功", f"已生成：{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def build_xml(self) -> str:
        """生成 WSB XML"""
        folders_xml = "\n".join(
            f"""        <MappedFolder>
                <HostFolder>{Path(self.root / f['host']).resolve()}</HostFolder>
                <SandboxFolder>{f['sandbox']}</SandboxFolder>
                <ReadOnly>{str(f['readonly']).lower()}</ReadOnly>
            </MappedFolder>"""
            for f in self.collect_folders()
        )

        def bool_str(b): return "Enable" if b else "Disable"

        return f"""<Configuration>
        <MappedFolders>
    {folders_xml}
        </MappedFolders>
        <AudioInput>{bool_str(self.chk_audio.isChecked())}</AudioInput>
        <VideoInput>{bool_str(self.chk_video.isChecked())}</VideoInput>
        <MemoryInMB>{self.spin_mem.value()}</MemoryInMB>
        <LogonCommand>
            <Command>{self.edit_cmd.text()}</Command>
        </LogonCommand>
        <vGPU>{bool_str(self.chk_vgpu.isChecked())}</vGPU>
        <ClipboardRedirection>{bool_str(self.chk_clipboard.isChecked())}</ClipboardRedirection>
        <PrinterRedirection>{bool_str(self.chk_printer.isChecked())}</PrinterRedirection>
        <ProtectedClient>{bool_str(self.chk_protected.isChecked())}</ProtectedClient>
        <Networking>{bool_str(self.chk_networking.isChecked())}</Networking>
</Configuration>"""

    def collect_folders(self):
        """从表格收集映射文件夹信息"""
        folders = []
        for row in range(self.table.rowCount()):
            host = self.table.item(row, 0).text()
            sandbox = self.table.item(row, 1).text()
            readonly = self.table.item(row, 2).checkState() == Qt.Checked
            folders.append({"host": host, "sandbox": sandbox, "readonly": readonly})
        return folders

    def add_row(self):
        """添加一行到表格"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(""))
        self.table.setItem(row, 1, QTableWidgetItem(""))
        chk = QTableWidgetItem()
        chk.setCheckState(Qt.Unchecked)
        self.table.setItem(row, 2, chk)

    def del_row(self):
        """删除选中的行"""
        for idx in sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True):
            self.table.removeRow(idx)

    def show_about_me_dialog(self):
        """显示一个关于我的对话框"""
        # 创建一个对话框
        dialog = QDialog()
        dialog.setWindowTitle("联系作者")
        dialog.resize(300, 100)

        # 创建布局
        layout = QVBoxLayout()

        # 添加一些个人信息
        email_label = QLabel('电子邮件：<a href="mailto:xiaoyou.lu@luxiaoyou.com">xiaoyou.lu@luxiaoyou.com</a>')
        email_label.setOpenExternalLinks(True)  # 允许打开外部链接
        home_page_label = QLabel('联系作者：<a href="https://luxiaoyou.com/contact.html">https://luxiaoyou.com/contact</a>')
        home_page_label.setOpenExternalLinks(True)

        # 设置文本对齐方式
        email_label.setAlignment(Qt.AlignLeft)
        home_page_label.setAlignment(Qt.AlignLeft)

        # 添加到布局中
        layout.addWidget(email_label)
        layout.addWidget(home_page_label)

        # 添加一个关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        # 设置布局到对话框
        dialog.setLayout(layout)

        # 显示对话框
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
