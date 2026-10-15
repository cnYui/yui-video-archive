"""使用既有 Playwright 桥接；参数从 JSON 读入，避免命令转义并隐藏连接令牌。"""
import re
import subprocess
import sys
from pathlib import Path
EP=Path(__file__).resolve().parents[1]
cmd=[sys.executable,'-W','ignore','D:/大疆/docs/pw/pw_do.py','--queue','C:/Users/yui/AppData/Local/Temp/pw_ccbaga_20261014',sys.argv[1]]
arg=EP/'制作/pw_args.json'
if len(sys.argv)>2: arg=Path(sys.argv[2])
if arg.exists():cmd+=['@'+str(arg)]
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
out=re.sub(r'(token=)[^\s&\)\]]+',r'\1[已脱敏]',r.stdout+r.stderr)
print(out)
sys.exit(r.returncode)
