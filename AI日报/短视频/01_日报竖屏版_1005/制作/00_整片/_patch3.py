p = "build_vertical.py"
s = open(p, encoding="utf-8").read()
s = s.replace('''"现在很多智能体会自己改自己的提示词、工具和流程，": [("提示词、", "prompts,")],''', '''"现在很多智能体会自己改自己的提示词、工具和流程，": [("会自己改", "edit")],''')
open(p, "w", encoding="utf-8").write(s)
