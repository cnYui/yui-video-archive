"""Windows 计划任务「AI日报-抓取」调用（pythonw 运行，不弹黑窗）：跑一次 collect.py collect，输出追加到 logs/collect_YYYYMM.log。"""
import datetime
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
log = HERE / "logs" / f"collect_{datetime.datetime.now():%Y%m}.log"
log.parent.mkdir(exist_ok=True)
py = Path(sys.executable).with_name("python.exe")          # pythonw.exe 同目录下的 python.exe（子进程不开窗口）
with open(log, "a", encoding="utf-8") as f:
    f.write(f"==== {datetime.datetime.now():%Y-%m-%d %H:%M:%S}（本机时间）\n")
    f.flush()
    r = subprocess.run([str(py), str(HERE / "collect.py"), "collect"], cwd=str(HERE), stdout=f, stderr=subprocess.STDOUT,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"}, creationflags=subprocess.CREATE_NO_WINDOW)
    f.write(f"==== exit {r.returncode}\n\n")
