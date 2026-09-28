#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bing URL 提交 API 批量提交脚本（SubmitUrlBatch）。

和 IndexNow 的区别：IndexNow 只是「通知发现」，Bing 可能不提高抓取优先级；
SubmitUrl 是 Bing 后台专属的显式提交指令，会把 URL 拉进优先抓取队列，
新站首页几天内通常能从「已发现但尚未爬取」推进到「已爬取 → 收录」。

默认自动附带首页（https://ktradeatlas.com/），因为新站首页最需要优先抓取。

用法：
  # key 用命令行参数（推荐，不落盘）
  python3 tools/bing-submit.py --apikey <BING_API_KEY> /exchanges/binance/referral-code/

  # 或走环境变量
  export BING_API_KEY=<BING_API_KEY>
  python3 tools/bing-submit.py /exchanges/binance/referral-code/ /exchanges/binance/fees/

  # 不自动附加首页
  python3 tools/bing-submit.py --apikey <KEY> --no-home /exchanges/binance/referral-code/

key 获取：Bing Webmaster Tools 后台 → 设置(⚙) → API 访问 → API key。
"""
import os
import sys
import json
import argparse
import urllib.request
import urllib.error

SITE_URL = "https://ktradeatlas.com"
HOST = "ktradeatlas.com"
ENDPOINT = "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlBatch"


def normalize(u: str) -> str:
    """路径 → 完整 URL，统一尾斜杠。"""
    if u.startswith("http"):
        return u.rstrip("/") + "/"
    return f"https://{HOST}" + (u if u.startswith("/") else "/" + u)


def dedupe(urls):
    """去重并保持顺序。"""
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def main():
    parser = argparse.ArgumentParser(description="Bing URL 提交 API 批量提交脚本")
    parser.add_argument("urls", nargs="+", help="要提交的 URL 或站点内路径")
    parser.add_argument(
        "--apikey", "-k",
        default=os.environ.get("BING_API_KEY"),
        help="Bing Webmaster API key（也可用环境变量 BING_API_KEY）",
    )
    parser.add_argument(
        "--no-home", action="store_true",
        help="不自动附加首页 %s" % (SITE_URL + "/"),
    )
    args = parser.parse_args()

    if not args.apikey:
        print("缺少 API key：用 --apikey <KEY> 传入，或设置环境变量 BING_API_KEY。")
        print("获取位置：Bing Webmaster Tools 后台 → 设置(⚙) → API 访问。")
        sys.exit(1)

    urls = [normalize(a) for a in args.urls]
    if not args.no_home:
        urls = [SITE_URL + "/"] + urls
    urls = dedupe(urls)

    payload = {"siteUrl": SITE_URL, "urlList": urls}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT + "?apikey=" + args.apikey,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status
            resp = r.read().decode("utf-8", "replace")
        print(f"HTTP {status}: {resp}")
        # {"d":null} + 200 为成功；d 非 null 或非 200 需人工看响应。
        if status == 200 and '"d":null' in resp:
            print(f"✅ 已向 Bing 提交 {len(urls)} 个 URL:")
            for u in urls:
                print("  " + u)
            print("提示：Bing 抓取不是秒级，给 3~7 天再复查后台状态。")
        else:
            print(f"⚠️ 响应异常，请核对 key 是否有效、站点是否已在此账号验证。")
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误 {e.code}: {e.read().decode('utf-8', 'replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"提交失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
