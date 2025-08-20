#include <stdio.h>
#include <windows.h>
#include "py_wsbgen.h"

#define ENV_FOLDER "env"
#define SCRIPTS_FOLDER "Scripts"
#define ACTIVATE_BAT "activate.bat"
#define PYTHONW_EXE "pythonw.exe"

int main() {
    // 获取当前可执行文件的路径
    char exe_path[MAX_PATH];
    GetModuleFileName(NULL, exe_path, MAX_PATH);

    // 获取当前批处理文件的路径（去掉文件名）
    char batch_path[MAX_PATH];
    GetModuleFileName(NULL, batch_path, MAX_PATH);
    char *last_slash = strrchr(batch_path, '\\');
    if (last_slash != NULL) {
        *last_slash = '\0'; // 去掉文件名，保留路径
    }

    // 去掉路径末尾的反斜杠（如果存在）
    if (strlen(batch_path) > 0 && batch_path[strlen(batch_path) - 1] == '\\') {
        batch_path[strlen(batch_path) - 1] = '\0';
    }

    // 构造Python脚本的路径
    char py_path[MAX_PATH];
    snprintf(py_path, MAX_PATH, "%s\\main.py", batch_path);

    // 检查是否存在main.py文件
    if (GetFileAttributes(py_path) == INVALID_FILE_ATTRIBUTES) {
        // 如果不存在main.py，创建并写入Python代码
        FILE *file = fopen(py_path, "wb");
        if (!file) {
            perror("无法创建输出文件");
            return -1;
        }

        // 将Python脚本数据写入文件
        fwrite(WSBGen_py, WSBGen_py_len, 1, file);
        fclose(file);
    }

    // 检查虚拟环境的activate.bat是否存在
    char activate_path[MAX_PATH];
    snprintf(activate_path, MAX_PATH, "%s\\%s\\%s\\%s", batch_path, ENV_FOLDER, SCRIPTS_FOLDER, ACTIVATE_BAT);

    char pythonw_path[MAX_PATH];
    if (GetFileAttributes(activate_path) != INVALID_FILE_ATTRIBUTES) {
        // 虚拟环境存在，使用虚拟环境的pythonw.exe
        snprintf(pythonw_path, MAX_PATH, "%s\\%s\\%s\\%s", batch_path, ENV_FOLDER, SCRIPTS_FOLDER, PYTHONW_EXE);
    } else {
        // 虚拟环境不存在，使用系统环境的pythonw
        snprintf(pythonw_path, MAX_PATH, PYTHONW_EXE);
    }

    // 构造命令行
    char command_line[MAX_PATH * 2];
    snprintf(command_line, MAX_PATH * 2, "\"%s\" \"%s\"", pythonw_path, py_path);

    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    if (!CreateProcess(NULL, command_line, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        fprintf(stderr, "Failed to start Python script: %lu\n", GetLastError());
        return 1;
    }

    // 等待Python进程结束（可选）
    // WaitForSingleObject(pi.hProcess, INFINITE);

    // 关闭句柄
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return 0;
}