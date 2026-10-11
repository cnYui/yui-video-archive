# -*- coding: utf-8 -*-
"""给 台本/V?_*.json 的每一句 lines[] 加上 en（英文行，中英双语字幕标准里的英文一行）。幂等：重跑会覆盖已有的 en。

  python add_en.py

- 同传句（kind = dub）的英文就是发布会原话（素材/转写/keynote.json 的词级转写，`words.py` 能查）：Sam / Holly 在台上说的那一句，
  明显的识别错字改回来（ChatGVT → ChatGPT；“instant to interactive” → “instant to interact with”；“see here at using” → “see here it using”）；
  对过：21 句里 18 句和整场转写逐字一致，其余 3 句就是上面这三处识别错字（用 ChatCut 那份转写稿 chatcut_transcript_nots.md 交叉核对过）。
- 画外音句（kind = vo）的英文是我（Claude Code）对中文画外音的翻译：口语、简洁，按意思翻；专有名词用发布会里的写法
  （Dots、Astra、GPT-6.1 Sol、Ultra Fast、Pro 500 / Pro 200、Decisions API、Luna、Codex Security Cloud、Agents API、Private Intelligence、Responses API、
  OpenAI Marketplace；Baseten 是发布会稿里被听成 “Base10” 的那家公司）。
- 长句不在这里拆：build_timeline.py 按标准（中文 ≤ 约 28 字、英文 ≤ 约 90 字符，各一行）用 bilingual_std.split_pair_aligned 自动拆成多条字幕
  （中英文一起找断点）；自动拆得不顺的句子在下面 CUT 里手动指定断点，写进台本的 "cut"。
这份稿子是别人演讲的整篇英文（同传句）+ 我们的译文，台本/*.json 因此在 .gitignore 里排除，不进公开仓库。
"""
import json
from pathlib import Path

EP = Path(__file__).resolve().parents[2]

EN = {
    # ---- V1 Dots ----
    "V1-N01": "OpenAI has built that movie-style AI assistant that's always standing right behind you.",
    "V1-N02": "It's called Dots, a new always-on assistant inside ChatGPT.",
    "V1-K1a": "So today we're introducing Dots.",
    "V1-K1b": "Dots are remarkably capable, always-on agents, built to handle really anything you can think of.",
    "V1-N03": "The keynote opened with a short film. A user names their Dot Alfred, and it gets to work.",
    "V1-N04": "Update the website, refresh the board deck, migrate the app.",
    "V1-N05": "A bakery cancels an order, and it lines up a backup on the way.",
    "V1-N06": "It handles the small stuff, and you can hand it the big jobs too.",
    "V1-N07": "Just give it one responsibility: watch the bug reports, start next year's budget planning, or find out why the app got slow.",
    "V1-N08": "It gets started, and it keeps going.",
    "V1-K2a": "They follow your access. They have their own computer in the cloud, their own browser, and they can write and test code as needed.",
    "V1-N09": "You don't even need to open ChatGPT. Soon you can text it and it replies, or just call it and talk.",
    "V1-N10": "It can use the 4,000-plus apps you've connected in ChatGPT, and you decide the permissions and limits.",
    "V1-N11": "Dots are available today to ChatGPT Pro, Business Premium and Enterprise users.",
    "V1-N12": "It's included in your plan, and chatting with it doesn't use up extra quota.",
    # ---- V2 Space ----
    "V2-N01": "OpenAI's engineers have their Dots fix dozens of bugs every day.",
    "V2-N02": "That's Holly from the product team, who showed how it works live on stage.",
    "V2-K1a": "Next up, we're introducing ChatGPT Space.",
    "V2-K1b": "This is a place where you, your teammates, and your agents can all work together.",
    "V2-N03": "A Space starts from a page. Call a Dot into the page to track dependencies; @-mention it in a comment and it jumps in to work.",
    "V2-N04": "You can also give the page standing instructions, like checking a Slack channel every day and updating the page with what it finds.",
    "V2-N05": "In the demo, Holly @-mentions her own Dot on the page and has it turn the chart into a bar chart.",
    "V2-N06": "The chart is live: you can filter by feedback type, and the Dot refreshes the data automatically every hour.",
    "V2-N07": "In Slack, forward a thread to a Dot and say \"you take it from here,\" and the work is handed off.",
    "V2-N08": "Someone drops a session ID and a user's error in the feedback channel; a teammate's Dot investigates right away and opens a PR that fixes it.",
    "V2-K2a": "And this is a real example.",
    "V2-K2b": "Our engineers have their dots fixing dozens of bugs a day in this way.",
    "V2-N09": "Dots and Space are available today to ChatGPT Pro, Business Premium and Enterprise users.",
    "V2-N10": "Enterprises also get a preview: specialist Dots. Like virtual coworkers set up by the company, they can take on accounting, email marketing, legal analysis and ticket handling.",
    "V2-N11": "OpenAI is also working with Microsoft to bring specialist Dots into Agent 365, so enterprises can manage them with familiar Microsoft tools.",
    # ---- V3 GPT-6.1 Sol 和 Ultra Fast ----
    "V3-N01": "Same task: one rocket has already taken off, while the other hasn't even finished drawing.",
    "V3-N02": "At the developer conference, OpenAI pushed two things this time: GPT-6.1 Sol and Ultra Fast.",
    "V3-N03": "First, GPT-6.1 Sol: intelligence close to the flagship Astra, at one fifth of the price.",
    "V3-N04": "Cached input gets a 95% discount, so agents that keep re-reading context and revising plans cost much less.",
    "V3-N05": "Prices on the slide: input $2 versus $10, cached input $0.10 versus $1, output $10 versus $50.",
    "V3-K1a": "Fast already gives you twice the speed at twice the price of standard.",
    "V3-K1b": "But ultra fast takes that to eight times the speed at six times the price of standard. An incredible 300 tokens per second.",
    "V3-K1c": "You know what? It's worth it.",
    "V3-N06": "They ran a comparison on stage: both sides get the same prompt, build a rocket that launches, in the DevDay colors.",
    "V3-N07": "The Ultra Fast rocket on the left has already lifted off; the standard one on the right is nowhere close. Sam says nothing else on the market does this.",
    "V3-N08": "Subscriptions change too. The new Pro 500 has 25 times the usage of Plus, includes Ultra Fast, and the slide says there's no 5-hour limit.",
    "V3-N09": "Pro 200 reopens today and still covers all the frontier models; using 6.1 Sol as your daily driver is plenty.",
    # ---- V4 Decisions API 和 AI 研究实习生 ----
    "V4-N01": "A response in a fraction of a second, and this video is not sped up.",
    "V4-K1a": "Today we're previewing our new Decisions API.",
    "V4-K1b": "The Decisions API lets the model respond in a fraction of a second.",
    "V4-K1c": "It's so fast, so it really feels almost instant to interact with.",
    "V4-K1d": "You can see here it using a computer and how quickly it's moving through these steps. This is not sped up.",
    "V4-N02": "The approach: give the Luna model a predefined set of options and have it only choose, to route a request, judge an image, or decide the agent's next step.",
    "V4-N03": "A small range of choices is why it's fast; image understanding, multilingual support and safeguards are all still there.",
    "V4-K2a": "Last year around this time, Jakob and I made a somewhat bold prediction on a live stream, saying that we would see the first AI research intern in the next year.",
    "V4-K2b": "To say the world did not have a lot of confidence in that prediction at the time was an understatement.",
    "V4-K2c": "A few weeks ago, we announced that we hit that goal.",
    "V4-K2d": "We now have an AI research intern, a system that can take on a clearly defined research task that would take a skilled researcher a lot of time and effort to complete.",
    "V4-N04": "Researcher Tejal shared the data: in January, the models basically couldn't finish research tasks that took a day or more.",
    "V4-N05": "By July, models could complete over a third of full-day research tasks start to finish, with no human intervention.",
    "V4-N06": "Models like Astra have already helped solve more than 100 math problems that had been open for decades.",
    "V4-N07": "They're also helping speed up work on new antibiotics, ancient languages, renewable energy and industrial manufacturing.",
    # ---- V5 Codex 上云和 Agents API ----
    "V5-N01": "Close the laptop and the task keeps running. Codex has now moved entirely to the cloud.",
    "V5-K1a": "Codex is now fully in the cloud.",
    "V5-K1b": "So this means you can start a task on your phone, pick it up on your browser or your desktop, right where you left off, no more lost threads.",
    "V5-K1c": "You don't have to worry about closing your laptop in the middle of a run. Your agents just keep working wherever you are.",
    "V5-N02": "Live demo: create a new task, pick \"cloud,\" and give one instruction: rewrite the entire backend in Rust.",
    "V5-N03": "It's a long job, but that's fine: hand it to the cloud, check back later, and keep adding ideas from your phone on the way.",
    "V5-N04": "The cloud also gets Codex Security Cloud: it keeps finding vulnerabilities and prepares verified fixes for you to review.",
    "V5-N05": "It adds automatic deduplication, scheduled scans and a new interface, available today.",
    "V5-N06": "The Agents API opens in public beta: the technology behind Codex and Dots is now available to developers.",
    "V5-N07": "It includes the harness, managed memory and multi-agent control, plus computer use: for example, an agent opens a browser and clicks through your site's flow to test it.",
    "V5-N08": "It works on AWS too: OpenAI's agents can run directly on Amazon's cloud, right next to your existing apps and data.",
    "V5-N09": "OpenAI Private Intelligence opens in preview: zero data retention plus private secure processing, so your content never sits on OpenAI's servers.",
    "V5-N10": "Reliability has numbers too: the Responses API grew 100x in a year, time to first token is 45% faster, and tool calls are over 30% faster.",
    # ---- V6 登录、插件和 Marketplace ----
    "V6-N01": "1.2 billion people use ChatGPT every week. How does the product you build get in?",
    "V6-N02": "The last part of the keynote is about doing business through that front door.",
    "V6-N03": "OpenAI admits earlier attempts were hit and miss; this time you get the same tools it uses to build ChatGPT itself.",
    "V6-N04": "First, sign in with ChatGPT: users bring their ChatGPT subscription into your product and use the tokens in their plan directly.",
    "V6-N05": "They're already paying for the subscription, so you don't have to cover their costs. 16 partners at launch.",
    "V6-N06": "Second, plugin extensions: developers can build full apps that feel native to ChatGPT, distributed through OpenAI.",
    "V6-N07": "Editors, dashboards, whole workspaces can be built straight into ChatGPT and Codex.",
    "V6-N08": "Live example: in a meetings app, one click on \"take notes\" turns the notes page into a Space, where teammates and Dots follow up together.",
    "V6-N09": "Figma brings design into the conversation: see team comments, and have ChatGPT revise the design.",
    "V6-N10": "Adobe brings Photoshop's features in. Dozens of partners are building.",
    "V6-N11": "When a user asks a question, ChatGPT judges whether your plugin can help, and connects on the spot.",
    "V6-N12": "Submission is simpler too: you can see review progress, request a human re-review, and update tools without resubmitting.",
    "V6-N13": "Finally, the OpenAI Marketplace launches today, with 30-plus launch partners including CodeRabbit, Notion and Vercel.",
    "V6-N14": "Enterprise customers can buy your product with their existing OpenAI commitment; through Baseten, they can even use open-source models directly.",
}


# 自动拆条（bilingual_std.split_pair_aligned：中英一起找断点）拆得不顺的句子，手动指定断点，写进台本的 "cut"：
# [(中文在这段文字之后断, 英文在这段文字之后断), …]，按出现的先后找。标准：每一条的中文和英文说的是同一件事，不在词组中间断（“defined | research task”）。
CUT = {
    "V4-K2b": [("信心，", "at the time")],                                              # 当时 = at the time，属于第一条
    "V4-K2d": [("研究任务，", "clearly defined research task")],                        # 英文第一条 92 字符，比 90 多 2，换来不拆 “research task”
    "V5-K1b": [("开个任务，", "on your phone,"), ("桌面端，", "your desktop,")],        # 三条，各对一句
    "V6-N08": [("会议应用，", "meetings app,"), ("变成 Space，", "into a Space,")],
}


def main():
    done, missing, seen = 0, [], set()
    for f in sorted((EP / "台本").glob("V?_*.json")):
        text = f.read_text(encoding="utf-8")
        d = json.loads(text)
        for l in d["lines"]:
            seen.add(l["id"])
            if l["id"] in EN:
                l["en"] = EN[l["id"]]
                done += 1
            else:
                missing.append(l["id"])
            if l["id"] in CUT:
                l["cut"] = [list(c) for c in CUT[l["id"]]]
            else:
                l.pop("cut", None)
        # 只重写 "lines" 那一块（每句一行，和原来的排版一致），别的地方的排版不动
        a = text.index('  "lines": [\n') + len('  "lines": [\n')
        b = text.index("\n  ]", a)
        new = text[:a] + ",\n".join("    " + json.dumps(l, ensure_ascii=False) for l in d["lines"]) + text[b:]
        assert json.loads(new) == d, f"{f.name}：重写后内容对不上"
        f.write_text(new, encoding="utf-8")
    extra = sorted(set(EN) - seen)
    print(f"加了 {done} 句英文；缺：{missing or '无'}；多出来的 id：{extra or '无'}")


if __name__ == "__main__":
    main()
