#!/usr/bin/env python3
"""광고 카드 3장. 계정 4개를 넣으면 10p, 없으면 회사 계정 100p."""

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
OUT = ROOT / "cards"
OUT.mkdir(exist_ok=True)
W, H = 1240, 1754
INK = (28, 36, 42)
SOFT = (90, 100, 108)
RED = (176, 52, 48)
SKY = (226, 232, 236)
YES = "https://www.yes24.com/product/goods/194774944"

PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>광고 카드 3장</title>
<style>
  body { margin:0; background:#e7eef2; color:#1c242a; font-family:"Apple SD Gothic Neo","Noto Sans KR",sans-serif; }
  main { max-width:980px; margin:0 auto; padding:32px 18px 60px; }
  h1 { font-weight:500; font-size:32px; margin:8px 0; }
  .kicker { color:#b03430; letter-spacing:.22em; font-size:12px; }
  form, .box { background:rgba(255,255,255,.78); padding:18px; margin:14px 0; }
  label { display:block; font-size:13px; color:#5c6972; margin:10px 0 4px; }
  input, textarea { width:100%; border:1px solid #d5dee3; padding:10px; font:inherit; }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  button { margin-top:14px; background:#1c242a; color:#fff; border:0; padding:12px 18px; cursor:pointer; }
  .point { color:#b03430; font-size:20px; }
  .cards { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
  .cards img { width:100%; background:#fff; }
  pre { white-space:pre-wrap; font-size:13px; }
  @media (max-width:800px) { .grid, .cards { grid-template-columns:1fr; } }
</style>
</head>
<body>
<main>
  <div class="kicker">AD STUDIO</div>
  <h1>저 0000가 0000를 0000 해주는 광고</h1>
  <p>계정 4개를 넣으면 10p. 비우면 회사 계정 100p. 추가 계정을 켜면 100p.</p>
  <form id="f">
    <div class="grid">
      <div><label>저 누가</label><input name="who" value="정한영"></div>
      <div><label>누구에게</label><input name="whom" value="배고픈 청춘"></div>
      <div><label>무엇을 해 주나</label><input name="does" value="희망으로 세워"></div>
      <div><label>책 이름</label><input name="book" value="배고픈 청춘을 위하여"></div>
    </div>
    <label>제미니 키</label><input name="gemini" type="password" autocomplete="off">
    <label>챗지피티 키</label><input name="openai" type="password" autocomplete="off">
    <label>그록 키</label><input name="grok" type="password" autocomplete="off">
    <label>클로드 키</label><input name="claude" type="password" autocomplete="off">
    <label><input name="extra" type="checkbox" style="width:auto"> 선택 추가 계정 사용, 100p</label>
    <button type="submit">3장 만들기</button>
  </form>
  <div class="box">
    <div class="point" id="point">아직 만들지 않았다.</div>
    <pre id="log"></pre>
  </div>
  <div class="cards" id="cards"></div>
</main>
<script>
document.getElementById("f").onsubmit = async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  data.extra = e.target.extra.checked;
  document.getElementById("log").textContent = "만드는 중";
  const res = await fetch("/generate", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)});
  const out = await res.json();
  document.getElementById("point").textContent = out.point_label;
  document.getElementById("log").textContent = out.note;
  document.getElementById("cards").innerHTML = out.cards.map(src => `<img src="${src}" alt="광고 카드">`).join("");
};
</script>
</body>
</html>
"""


def font(size):
    return ImageFont.truetype(FONT, size)


def draw_center(draw, text, y, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)


def card(lines, foot, photo=None):
    im = Image.new("RGB", (W, H), SKY)
    d = ImageDraw.Draw(im)
    if photo and photo.exists():
        src = Image.open(photo).convert("RGB")
        src = src.crop((0, int(src.height * 0.42), src.width, int(src.height * 0.9)))
        ph = 980
        pw = int(src.width * ph / src.height)
        src = src.resize((pw, ph), Image.Resampling.LANCZOS)
        im.paste(src, ((W - pw) // 2, H - ph - 36))
    d.rectangle((28, 28, W - 29, H - 29), outline=(255, 255, 255), width=1)
    d.rectangle((40, 40, W - 41, H - 41), outline=INK, width=1)
    d.rectangle((W / 2 - 22, 118, W / 2 + 22, 121), fill=RED)
    y = 150
    for text, size, fill in lines:
        draw_center(d, text, y, font(size), fill)
        y += size + 22
    draw_center(d, foot, H - 90, font(20), INK)
    return im


def house_lines(who, whom, does, book):
    sentence = f"저 {who}이 {whom}을 {does} 주는 광고다."
    return sentence, [
        [("1", 22, RED), (book, 42, INK), (f"저 {who}이", 36, INK), (f"{whom}을", 36, INK), (f"{does} 준다", 32, SOFT)],
        [("2", 22, RED), ("절망한 자에게 희망을,", 34, INK), ("빚진 자에게 기회를.", 34, INK), (sentence, 28, SOFT), ("子悟民道信崔寶辰", 30, RED)],
        [("3", 22, RED), ("예스24에서 본다", 36, INK), (book, 28, SOFT), (who, 32, INK), ("지주클럽", 26, RED)],
    ]


def ask(url, headers, payload, timeout=25):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode())


def from_models(prompt, keys):
    notes = []
    texts = []
    if keys.get("openai"):
        try:
            data = ask(
                "https://api.openai.com/v1/chat/completions",
                {"Authorization": f"Bearer {keys['openai']}", "Content-Type": "application/json"},
                {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
            )
            texts.append(data["choices"][0]["message"]["content"])
            notes.append("챗지피티 자기 계정")
        except Exception as exc:
            notes.append(f"챗지피티 실패: {exc.__class__.__name__}")
    if keys.get("grok"):
        try:
            data = ask(
                "https://api.x.ai/v1/chat/completions",
                {"Authorization": f"Bearer {keys['grok']}", "Content-Type": "application/json"},
                {"model": "grok-3-mini", "messages": [{"role": "user", "content": prompt}]},
            )
            texts.append(data["choices"][0]["message"]["content"])
            notes.append("그록 자기 계정")
        except Exception as exc:
            notes.append(f"그록 실패: {exc.__class__.__name__}")
    if keys.get("claude"):
        try:
            data = ask(
                "https://api.anthropic.com/v1/messages",
                {"x-api-key": keys["claude"], "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                {"model": "claude-3-5-haiku-latest", "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]},
            )
            texts.append(data["content"][0]["text"])
            notes.append("클로드 자기 계정")
        except Exception as exc:
            notes.append(f"클로드 실패: {exc.__class__.__name__}")
    if keys.get("gemini"):
        try:
            data = ask(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={keys['gemini']}",
                {"Content-Type": "application/json"},
                {"contents": [{"parts": [{"text": prompt}]}]},
            )
            texts.append(data["candidates"][0]["content"]["parts"][0]["text"])
            notes.append("제미니 자기 계정")
        except Exception as exc:
            notes.append(f"제미니 실패: {exc.__class__.__name__}")
    return texts, notes


def points(keys, extra):
    filled = sum(1 for name in ("gemini", "openai", "grok", "claude") if keys.get(name))
    if filled == 4:
        base, label = 10, "자기 계정 4개, 10p"
    else:
        base, label = 100, "계정 없음, 회사 계정 100p" if filled == 0 else f"계정 {filled}개, 회사 계정이 채움, 100p"
    if extra:
        base += 100
        label += " + 추가 계정 100p"
    return base, label


def make(body):
    who = (body.get("who") or "정한영").strip()
    whom = (body.get("whom") or "배고픈 청춘").strip()
    does = (body.get("does") or "희망으로 세워").strip()
    book = (body.get("book") or "배고픈 청춘을 위하여").strip()
    keys = {k: (body.get(k) or "").strip() for k in ("gemini", "openai", "grok", "claude")}
    extra = bool(body.get("extra"))
    cost, label = points(keys, extra)
    sentence, pages = house_lines(who, whom, does, book)
    prompt = (
        f"{sentence} 의미는 바꾸지 말고 표지, 설명, 연결 세 장으로만 짧게 고쳐라. "
        "가격, ISBN, 판매량은 쓰지 마라."
    )
    texts, notes = from_models(prompt, keys)
    if texts:
        notes.append("모델 답은 참고만 하고, 카드 문장은 잠근 형식이다.")
    else:
        notes.append("키 호출이 없어 우리 형식으로 3장을 만들었다.")
    names = []
    for i, lines in enumerate(pages, 1):
        path = OUT / f"card-{i}.png"
        card(lines, label, ROOT / "cover.jpg" if i == 1 else None).save(path, quality=95)
        names.append(f"/cards/card-{i}.png")
    return {"point": cost, "point_label": label, "note": sentence + "\n" + "\n".join(notes), "cards": names}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            data = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif self.path.startswith("/cards/"):
            path = OUT / self.path.split("/")[-1]
            if not path.exists():
                self.send_error(404)
                return
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
        else:
            self.send_error(404)
            return
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/generate":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(n).decode() or "{}")
        out = make(body)
        data = json.dumps(out, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    sample = make({"who": "정한영", "whom": "배고픈 청춘", "does": "희망으로 세워", "book": "배고픈 청춘을 위하여"})
    print(json.dumps({k: sample[k] for k in ("point", "point_label")}, ensure_ascii=False))
    port = int(os.environ.get("PORT", "8787"))
    print(f"http://127.0.0.1:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
