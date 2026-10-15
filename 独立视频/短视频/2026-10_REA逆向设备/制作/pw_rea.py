"""连接本期独立 Playwright 队列，动作从文件读取并隐藏连接参数。"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUEUE = Path('C:/Users/yui/AppData/Local/Temp/pw_rea_20261014')
tool = sys.argv[1]
args = {'code': Path(sys.argv[2]).read_text(encoding='utf-8')} if tool=='browser_run_code_unsafe' else json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
arg = QUEUE/'rea_action_args.json'
arg.write_text(json.dumps(args,ensure_ascii=False),encoding='utf-8')
r = subprocess.run([sys.executable,'-W','ignore','D:/大疆/docs/pw/pw_do.py','--queue',str(QUEUE),tool,'@'+str(arg)],capture_output=True,text=True,encoding='utf-8',errors='replace')
out = re.sub(r'(token=)[^\s&\)\]]+',r'\1[已脱敏]',r.stdout+r.stderr)
print(out)
sys.exit(r.returncode)
