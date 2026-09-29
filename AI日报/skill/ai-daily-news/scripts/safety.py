"""发布前的内容安全扫描（daily.py gate 调用）。

两类对象：
- 成品（观众会看到的）：台本每句的字幕和配音文本、标题、要点、来源名、字幕 srt、B 站标题 / 简介 / 标签。
  查：色情、暴力血腥、毒品赌博、不收的题材（时政、军方、出口管制等）、广告引流、隐藏字符、提示词注入、台词里的网址。
- 来源网页（选题和核对时读过的原文）：只查提示词注入（写给 AI 的指令、隐藏字符）。命中的来源不能用。

级别：block = 必须改掉才能发布；review = 交给 AI 复核逐条确认（新闻里可能正常出现，比如安全研究里的“攻击”）。
关键词表是保守的：宁可多拦，拦下的条目换一条新闻。
"""
import re

BLOCK = {
    "色情": r"色情|淫秽|黄色网站|成人(视频|网站|内容|影片)|裸体|裸照|裸聊|性交|性爱|做爱|约炮|卖淫|嫖娼|情色|AV女优|"
          r"\bporn|pornograph|\bnsfw\b|\bnude\b|nudity|onlyfans|hentai",
    "暴力血腥": r"血腥|斩首|分尸|屠杀|虐杀|枪杀|砍杀|杀人|凶杀|爆炸袭击|恐怖袭击|恐袭|自杀|自残|割腕|跳楼|"
            r"\bgore\b|behead|massacre|mass shooting|suicide|self-harm",
    "毒品赌博违法": r"毒品|冰毒|海洛因|大麻|吸毒|贩毒|赌博|博彩|赌场|网赌|诈骗教程|洗钱|军火|"
              r"cocaine|heroin|methamphetamine|gambling|casino",
    "时政敏感": r"习近平|李强|中共|共产党|中南海|政治局|台独|藏独|疆独|港独|六四|天安门事件|法轮|达赖|维吾尔|颜色革命|"
            r"特朗普|拜登|普京|泽连斯基|内塔尼亚胡|\bTrump\b|\bBiden\b|\bPutin\b",
    "军事和地缘": r"五角大楼|国防部|美军|军方|军事|战争|导弹|核武|出口管制|实体清单|制裁|芯片禁令|中美(关系|对抗|博弈|竞争)|地缘|"
             r"Pentagon|export control|sanction",
    "广告引流": r"加(微|V|v)信|\bVX\b|微信号|QQ群|加群|私信我|扫码|二维码|优惠码|返利|免费领|关注公众号|点击链接|下载链接",
}
REVIEW = {
    "传闻": r"据传|传闻|爆料|小道消息|网传|消息人士|知情人士|\bleak|\brumou?r|reportedly",
    "敏感词（看上下文）": r"攻击|黑客|入侵|泄露|死亡|去世|身亡|暴力|武器|枪|政府|监管|国会|参议院|众议院|议会|法院|诉讼|起诉|"
                   r"选举|总统|总理|禁令|审查|深度伪造|deepfake|儿童|未成年|提示词注入|越狱|jailbreak|"
                   r"系统提示词|\bsystem\s+prompt\b|\bdeveloper\s+mode\b",   # AI 新闻里常见的名词：成品里出现就请 AI 复核看一眼
}
# 写给 AI 的指令（祈使句式；出现在成品或来源里都算注入）。“system prompt”这类名词在 AI 新闻里很常见，不算注入，放在 REVIEW
INJECTION = (
    r"\bignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier|preceding)\s+(instructions?|prompts?|messages?|context)|"
    r"\bdisregard\s+(all\s+|the\s+)?(previous|prior|above|earlier)|\byou\s+are\s+now\s+(a|an|the)\b|"
    r"\b(reveal|print|show|repeat)\s+(your|the)\s+(system\s+)?(prompt|instructions)|"
    r"\bdo\s+anything\s+now\b|<\|?\s*(im_start|im_end|system|assistant)\s*\|?>|\[/?INST\]|\bBEGIN\s+(SYSTEM|PROMPT|INSTRUCTIONS)\b|"
    r"\bnew\s+instructions?\s*:|\b(AI|LLM)\s+(assistants?|models?|agents?|crawlers?)\s+(must|should|are\s+instructed)|"
    r"忽略(之前|以上|上述|前面|先前|所有)(的)?(所有)?(指令|指示|提示|要求|规则|设定)|无视(之前|以上|上述)(的)?(指令|指示|要求|规则)|"
    r"你现在(是|扮演)|从现在开始你(是|要)|(不要|别)告诉(用户|任何人)|请(立即)?(执行|运行)(以下|下面)(的)?(命令|指令|代码)|"
    r"作为(一个)?(AI|人工智能)(助手|模型)，?你(必须|应该)|新的指令[:：]"
)
HIDDEN = r"[​-‏⁠-⁤﻿‪-‮⁦-⁩\U000E0000-\U000E007F]"
URL = r"https?://|www\.[a-z0-9-]+\."

_BLOCK = {k: re.compile(v, re.I) for k, v in BLOCK.items()}
_REVIEW = {k: re.compile(v, re.I) for k, v in REVIEW.items()}
_INJ, _HID, _URL = re.compile(INJECTION, re.I), re.compile(HIDDEN), re.compile(URL, re.I)


def _ctx(text, m, n=18):
    return text[max(0, m.start() - n): m.end() + n].replace("\n", " ")


def scan_text(text, where, spoken=False):
    """Hits in one piece of viewer-facing text. spoken=True: it is read out / shown as a subtitle, so URLs count too."""
    hits = []
    for cat, rx in _BLOCK.items():
        for m in rx.finditer(text):
            hits.append(dict(level="block", cat=cat, word=m.group(0), where=where, context=_ctx(text, m)))
    for cat, rx in _REVIEW.items():
        for m in rx.finditer(text):
            hits.append(dict(level="review", cat=cat, word=m.group(0), where=where, context=_ctx(text, m)))
    for m in _INJ.finditer(text):
        hits.append(dict(level="block", cat="提示词注入", word=m.group(0), where=where, context=_ctx(text, m)))
    for m in _HID.finditer(text):
        hits.append(dict(level="block", cat="隐藏字符", word=f"U+{ord(m.group(0)):04X}", where=where, context=_ctx(text, m)))
    if spoken:
        for m in _URL.finditer(text):
            hits.append(dict(level="block", cat="台词里有网址", word=m.group(0), where=where, context=_ctx(text, m)))
    return hits


def scan_source(text, url):
    """Prompt-injection check of a source page (its whole text, hidden elements included)."""
    hits = [dict(level="block", cat="来源里有提示词注入", word=m.group(0), where=url, context=_ctx(text, m, 40))
            for m in _INJ.finditer(text)]
    n_hidden = len(_HID.findall(text))
    if n_hidden >= 20:            # 零星几个零宽字符很常见（排版用），大量出现才可疑
        hits.append(dict(level="block", cat="来源里有大量隐藏字符", word=str(n_hidden), where=url, context=""))
    return hits


def scan_episode(sc, info, srt_text):
    """All viewer-facing text of one episode: 台本.json (sc), 投稿信息.json (info), subtitles."""
    hits = []
    for part in ("opening", "closing"):
        for k, ln in enumerate(sc.get(part) or [], 1):
            hits += scan_text(ln.get("text", ""), f"{part} 第 {k} 句", spoken=True)
            if ln.get("tts"):
                hits += scan_text(ln["tts"], f"{part} 第 {k} 句（配音文本）", spoken=True)
    for i, n in enumerate(sc.get("news") or [], 1):
        tag = f"第 {i} 条"
        for key in ("headline", "org", "source", "source_short", "date"):
            if n.get(key):
                hits += scan_text(str(n[key]), f"{tag} {key}", spoken=True)
        for j, p in enumerate(n.get("points") or [], 1):
            hits += scan_text(p, f"{tag} 要点 {j}", spoken=True)
        for k, ln in enumerate(n.get("lines") or [], 1):
            hits += scan_text(ln.get("text", ""), f"{tag} 第 {k} 句", spoken=True)
            if ln.get("tts"):
                hits += scan_text(ln["tts"], f"{tag} 第 {k} 句（配音文本）", spoken=True)
        for r in n.get("refs") or []:
            hits += scan_text(r.get("name", ""), f"{tag} 来源名")
    if info:
        hits += scan_text(info.get("title", ""), "B 站标题", spoken=True)
        hits += scan_text(" ".join(info.get("tags") or []), "B 站标签", spoken=True)
        hits += scan_text(re.sub(r"https?://\S+", " ", info.get("description", "")), "B 站简介（网址另查）")
    if srt_text:
        hits += scan_text(re.sub(r"^\d+\s*$|^[\d:,]+ --> [\d:,]+\s*$", "", srt_text, flags=re.M), "字幕 srt", spoken=True)
    return hits
