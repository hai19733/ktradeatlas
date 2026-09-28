#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexNow 定向提交脚本（Bing）。

只提交本次实际变动的 URL（不要全站 sitemap 重推，见 indexnow-targeted-submit 约定）。

用法：
  python3 tools/indexnow-submit.py /transfer/english-name-mismatch/ /transfer/
  # 或直接给完整 URL：
  python3 tools/indexnow-submit.py https://ktradeatlas.com/transfer/english-name-mismatch/
"""
import sys
import json
import urllib.request

HOST = "ktradeatlas.com"
KEY = "56b4ddbc15ac05b303305280a2c68c47"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"

def normalize(u: str) -> str:
    if u.startswith("http"):
        return u.rstrip("/") + "/"
    return f"https://{HOST}" + (u if u.startswith("/") else "/" + u)

def main():
    urls = [normalize(a) for a in sys.argv[1:]]
    if not urls:
        print("用法: python3 tools/indexnow-submit.py <url1> [url2 ...]")
        sys.exit(1)
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://www.bing.com/indexnow",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status
            resp = r.read().decode("utf-8", "replace")
        print(f"HTTP {status}: {resp}")
        print(f"已提交 {len(urls)} 个 URL:")
        for u in urls:
            print("  " + u)
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误 {e.code}: {e.read().decode('utf-8', 'replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"提交失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
