"""双击启动器：后台启动只监听本机的服务，然后打开应用窗口。"""
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent
STATE = ROOT/'.local'
# 不同目录的副本通常使用不同端口，避免串到另一个人的本地应用。
PORT = 18000 + int(hashlib.sha256(str(ROOT).encode()).hexdigest()[:4],16)%10000
URL = f'http://127.0.0.1:{PORT}'

def healthy():
    try:
        with urllib.request.urlopen(URL+'/_stcore/health',timeout=1) as r:
            return r.status == 200
    except Exception:
        return False

def open_window():
    for base in (os.environ.get('ProgramFiles(x86)',''),os.environ.get('ProgramFiles','')):
        edge = Path(base)/'Microsoft/Edge/Application/msedge.exe'
        if edge.is_file():
            subprocess.Popen([str(edge),'--app='+URL],creationflags=subprocess.CREATE_NO_WINDOW)
            return
    webbrowser.open(URL)

def main():
    STATE.mkdir(exist_ok=True)
    ctypes.windll.kernel32.CreateMutexW.argtypes = [ctypes.c_void_p,wintypes.BOOL,wintypes.LPCWSTR]
    ctypes.windll.kernel32.CreateMutexW.restype = wintypes.HANDLE
    ctypes.windll.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    lock = ctypes.windll.kernel32.CreateMutexW(None,False,'Local\\NJUPT-'+str(PORT))
    if ctypes.windll.kernel32.GetLastError() == 183:
        return
    try:
        state_file = STATE/'server.json'
        existing = json.loads(state_file.read_text()) if state_file.exists() else {}
        if existing.get('root') == str(ROOT) and healthy():
            open_window()
            return
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1',PORT)) == 0:
                raise RuntimeError('本地端口被其他程序占用，请关闭该程序后重试。')
        python = Path(sys.executable).with_name('python.exe')
        env = dict(os.environ,PYTHONIOENCODING='utf-8')
        with (STATE/'server.log').open('w',encoding='utf-8') as log:
            process = subprocess.Popen([str(python),'-m','streamlit','run',str(ROOT/'app.py'),
                '--server.address','127.0.0.1','--server.port',str(PORT),'--server.headless','true'],
                cwd=ROOT,env=env,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        state_file.write_text(json.dumps(dict(root=str(ROOT),pid=process.pid,port=PORT)),encoding='utf-8')
        for _ in range(90):
            if process.poll() is not None:
                raise RuntimeError('启动失败。请重新运行 setup.bat 检查依赖，或查看 .local/server.log。')
            if healthy():
                open_window()
                return
            time.sleep(1)
        process.terminate()
        raise RuntimeError('启动超时，请重新运行 setup.bat。')
    except Exception as exc:
        ctypes.windll.user32.MessageBoxW(0,str(exc),'校园知识助手',0x10)
    finally:
        ctypes.windll.kernel32.CloseHandle(lock)

if __name__ == '__main__':
    main()

