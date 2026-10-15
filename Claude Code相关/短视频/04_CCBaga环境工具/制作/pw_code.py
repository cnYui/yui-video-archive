"""用一次 Playwright 调用执行当前页面动作，避免扩展空闲重连使引用过期。"""
import json
import subprocess
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
arg=HERE/'pw_code_args.json'
code=Path(sys.argv[1]).read_text(encoding='utf-8')
arg.write_text(json.dumps(dict(code=code),ensure_ascii=False),encoding='utf-8')
r=subprocess.run([sys.executable,str(HERE/'pw_action.py'),'browser_run_code_unsafe',str(arg)])
sys.exit(r.returncode)
