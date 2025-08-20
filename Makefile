# Makefile for WSBGen

# 编译器
CC = x86_64-w64-mingw32-gcc

# 编译器和链接器的标志
CFLAGS = -static-libgcc -static-libstdc++ -static -mwindows
LDFLAGS = -lcomctl32

# 目录设置
SOURCEDIR = source
BUILDDIR = build

# 目标可执行文件
TARGET = $(BUILDDIR)/WSBGen.exe

# 源代码文件
SRCS = $(SOURCEDIR)/WSBGen.c
SRCS_PY_WSBGEN = $(SOURCEDIR)/py_wsbgen.c
SRCS_PY_WSBGEN_FILE = $(SOURCEDIR)/WSBGen.py

# 依赖文件
REQUIREMENTS_TXT = $(BUILDDIR)/requirements.txt

# 帮助
help:
	@echo "使用方法："
	@echo "  make all       - 构建目标可执行文件。"
	@echo "  make clean     - 清理生成的文件。"
	@echo "  make help      - 显示此帮助菜单。"

# 默认目标
all: $(REQUIREMENTS_TXT) $(TARGET)

# 构建目标可执行文件
$(TARGET): $(SRCS) $(SRCS_PY_WSBGEN)
	@mkdir -p $(@D)
	$(CC) $(SRCS) $(SRCS_PY_WSBGEN) -o $@ $(CFLAGS) $(LDFLAGS)

# 从 Python 文件生成 C 文件
$(SRCS_PY_WSBGEN): $(SRCS_PY_WSBGEN_FILE)
	xxd -i $< $@

# 生成依赖文件
$(REQUIREMENTS_TXT):
	@mkdir -p $(@D)
	@echo "PySide6==6.9.1" > $@
	@echo "PySide6_Addons==6.9.1" >> $@
	@echo "PySide6_Essentials==6.9.1" >> $@
	@echo "shiboken6==6.9.1" >> $@

# 清理生成的文件
clean:
	rm -f $(TARGET)
	rm -f $(SRCS_PY_WSBGEN)
	rm -rf $(BUILDDIR)

# 声明伪目标
.PHONY: all clean help