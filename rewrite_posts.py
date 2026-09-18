#!/usr/bin/env python3
"""
Rewrite To My Voice — Supabase edition
--------------------------------------
Takes each viral post's transcript (or caption) and rewrites it into a
ready-to-film Chinese 口播 script in the owner's brand voice (from
brand_voice.md), writing the result to the `my_script` column. Edit
brand_voice.md to tune the persona/tone/red-lines — no code change needed.

Mirrors analyze_posts.py: highest-scoring posts first, HTTP-400 rejections
are marked so the queue moves on, GitHub Models by default / Anthropic when
ANTHROPIC_API_KEY is set. Non-fatal by design: if the `my_script` column is
missing (older schema) it explains the one-line fix and exits 0 so the
Analyze → Deploy chain keeps running.

Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GITHUB_TOKEN
     NICHE (default: 自媒体内容), GH_MODEL (openai/gpt-4o-mini),
     POST_LIMIT (60), REWRITE_ALL (set to "1" to redo every post after
     changing brand_voice.md)
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SUPABASE_URL = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
NICHE = os.environ.get("NICHE", "自媒体内容")
GH_MODEL = os.environ.get("GH_MODEL", "openai/gpt-4o-mini")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
POST_LIMIT = int(os.environ.get("POST_LIMIT", "60"))
REWRITE_ALL = os.environ.get("REWRITE_ALL", "").strip()  # set to redo existing (voice change)
FAIL_MARK = "(改写失败)"
SKIP_TR = ("(转录失败)", "(视频不可用)", "(无口播内容)")

BRAND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brand_voice.md")


def load_brand():
    try:
        txt = open(BRAND_PATH, encoding="utf-8").read().strip()
        if txt:
            return txt
    except Exception:
        pass
    return (f"你是一名做「{NICHE}」的短视频口播创作者。"
            "语气真诚、有画面、有落地步骤,不夸大、不承诺结果。不用 emoji、不用破折号。")


def build_system():
    return (
        "你是一名口播脚本写手。下面【人设与规矩】是你要扮演的品牌身份、语气、受众和红线,"
        "你写的每一句都要像本人亲口说出来的,并严格遵守里面的红线。\n\n"
        "任务:给你一条【竞对爆款短视频】的口播稿或文案(可能是英文、可能是别的领域)。"
        "把它改写成可以直接对着镜头念的【中文口播脚本】:\n"
        "1. 保留原爆款的钩子和结构节奏(只借结构,不抄原文字句)\n"
        "2. 把话题、案例、场景换成【人设与规矩】里的受众痛点\n"
        "3. 全程用【人设与规矩】的语气,红线一条都不能碰\n"
        "4. 长度约 30-60 秒口播,开头第一句就是强钩子,结尾一句软性行动指引\n"
        "5. 直接输出脚本正文本身,不要任何解释、标题、前后缀,不要写「以下是」或「脚本:」\n\n"
        "【人设与规矩】\n" + load_brand()
    )


SYSTEM = build_system()


def _request(url, method="GET", data=None, headers=None, timeout=120):
    hdrs = headers or {}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", None)
        raw = resp.read()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        raise RuntimeError("HTTP %s non-JSON body: %r" % (status, raw[:300]))


def sb(path, method="GET", data=None, prefer=None):
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": "Bearer " + key}
    if prefer:
        headers["Prefer"] = prefer
    return _request(f"{SUPABASE_URL}/rest/v1/{path}", method, data, headers, 60)


def fetch_pending():
    flt = "" if REWRITE_ALL else "&my_script=is.null"
    rows = sb(
        "posts?select=post_id,competitor,caption,transcript,post_type,"
        "likes,comments,followers"
        + flt +
        "&order=viral_score.desc.nullslast"
    )
    # need real material to rewrite: a usable transcript or a decent caption
    # (length filters live here — PostgREST cannot filter on expressions)
    return [p for p in rows
            if len((p.get("transcript") or "") if (p.get("transcript") or "") not in SKIP_TR else "") > 30
            or len(p.get("caption") or "") > 50]


def build_prompt(p):
    tr = p.get("transcript") or ""
    if tr in SKIP_TR:
        tr = ""
    cap = (p.get("caption") or "")[:800]
    body = (f"竞对账号: @{p.get('competitor', '?')}\n"
            f"数据: 赞 {p.get('likes', '?')} | 评论 {p.get('comments', '?')} | 粉丝 {p.get('followers', '?')}\n")
    if tr:
        body += f"\n【原视频口播稿(主要改写依据)】\n{tr[:2800]}\n"
    if cap:
        body += f"\n【原帖文案(辅助参考)】\n{cap}\n"
    body += "\n请按系统指令,把上面这条爆款改写成【人设与规矩】里这个人的中文口播脚本。"
    return body


def rewrite_github(token, p):
    resp = _request(
        "https://models.github.ai/inference/chat/completions", "POST",
        {"model": GH_MODEL, "max_tokens": 700,
         "messages": [{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": build_prompt(p)}]},
        {"Authorization": "Bearer " + token}, 90)
    ch = resp.get("choices") or []
    return (ch[0].get("message", {}).get("content") or "").strip() if ch else ""


def rewrite_anthropic(key, p):
    resp = _request(
        "https://api.anthropic.com/v1/messages", "POST",
        {"model": CLAUDE_MODEL, "max_tokens": 700, "system": SYSTEM,
         "messages": [{"role": "user", "content": build_prompt(p)}]},
        {"x-api-key": key, "anthropic-version": "2023-06-01"}, 90)
    parts = resp.get("content") or []
    return "".join(x.get("text", "") for x in parts if x.get("type") == "text").strip()


def save(post_id, text):
    sb(f"posts?post_id=eq.{urllib.parse.quote(post_id)}", method="PATCH",
       data={"my_script": text[:4000]}, prefer="return=minimal")


def main():
    if not SUPABASE_URL or not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY required")
        sys.exit(1)
    anthropic_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    gh_token = (os.environ.get("GITHUB_TOKEN") or "").strip()
    if anthropic_key:
        provider, delay = "anthropic", 0.5
        call = lambda p: rewrite_anthropic(anthropic_key, p)
    elif gh_token:
        provider, delay = f"github-models ({GH_MODEL})", 4.5
        call = lambda p: rewrite_github(gh_token, p)
    else:
        print("No ANTHROPIC_API_KEY or GITHUB_TOKEN — skipping (non-fatal).")
        return
    print(f"[Provider] {provider} | [Niche] {NICHE}" + (" | REWRITE_ALL" if REWRITE_ALL else ""))

    try:
        queue = fetch_pending()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace") if exc.fp else ""
        # older schema without the column: tell the student the one-line fix and
        # exit 0 so the Analyze → Deploy chain is not blocked by this bonus step
        if exc.code == 400 and ("my_script" in body or '"42703"' in body):
            print("posts 表还没有 my_script 这一列(旧版 schema),这次跳过「我的稿」,其他步骤不受影响。")
            print("补上只要一句:Supabase → SQL Editor → 贴这行 → Run:")
            print("  alter table posts add column if not exists my_script text;")
            return
        raise
    print(f"{len(queue)} posts pending rewrite")
    if not queue:
        return
    if len(queue) > POST_LIMIT:
        print(f"capping at {POST_LIMIT} ({len(queue) - POST_LIMIT} left for next run)")
        queue = queue[:POST_LIMIT]

    ok = failed = 0
    for i, p in enumerate(queue, 1):
        who = p.get("competitor", "?")
        try:
            text = call(p)
            if not text:
                raise ValueError("empty response")
            save(p["post_id"], text)
            ok += 1
            print(f"[{i}/{len(queue)}] @{who} OK: {text[:50]}")
        except urllib.error.HTTPError as exc:
            failed += 1
            if exc.code == 400:
                try:
                    save(p["post_id"], FAIL_MARK)
                except Exception:
                    pass
                print(f"[{i}/{len(queue)}] @{who} REJECTED (marked)")
            else:
                print(f"[{i}/{len(queue)}] @{who} FAILED: HTTP {exc.code} (retry)")
        except Exception as exc:
            failed += 1
            print(f"[{i}/{len(queue)}] @{who} FAILED: {exc} (retry)")
        time.sleep(delay)

    print(f"Done: {ok} rewritten, {failed} failed")


if __name__ == "__main__":
    main()
