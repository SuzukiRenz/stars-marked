#!/usr/bin/env python3
"""
GitHub Stars 抓取 & AI 智能分类
支持 OpenAI 兼容接口 (OpenAI / Anthropic / DeepSeek / 阿里通义 / 月之暗面 等)
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# ── 配置 ───────────────────────────────────────────────────────────────────────
# GitHub
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USER  = os.environ.get("GITHUB_USER", "")

# AI 供应商 (OpenAI 兼容接口通用配置)
AI_BASE_URL  = os.environ.get("AI_BASE_URL",  "https://api.anthropic.com/openai/v1")
AI_API_KEY   = os.environ.get("AI_API_KEY",   os.environ.get("ANTHROPIC_API_KEY", ""))
AI_MODEL     = os.environ.get("AI_MODEL",     "claude-haiku-4-5-20251001")

# 行为配置
BATCH_SIZE     = int(os.environ.get("BATCH_SIZE", "20"))   # 每次 AI 请求的仓库数量
RATE_LIMIT_GAP = float(os.environ.get("RATE_LIMIT_GAP", "1.5"))  # 请求间隔(秒)

DATA_FILE = Path(__file__).parent.parent / "docs" / "data" / "stars.json"

# ── 预设供应商快速配置参考 ─────────────────────────────────────────────────────
# 在 GitHub Actions Secrets/Variables 中设置以下变量即可：
#
#  供应商           AI_BASE_URL                              AI_MODEL 示例
#  ─────────────   ──────────────────────────────────────   ────────────────────────
#  Anthropic        https://api.anthropic.com/openai/v1      claude-haiku-4-5-20251001
#  OpenAI           https://api.openai.com/v1                gpt-4o-mini
#  DeepSeek         https://api.deepseek.com/v1              deepseek-chat
#  阿里通义          https://dashscope.aliyuncs.com/compatible-mode/v1  qwen-turbo
#  月之暗面(Kimi)    https://api.moonshot.cn/v1               moonshot-v1-8k
#  智谱AI            https://open.bigmodel.cn/api/paas/v4     glm-4-flash
#  Groq             https://api.groq.com/openai/v1           llama3-8b-8192
#  本地 Ollama      http://localhost:11434/v1                 llama3.2

HEADERS_GH = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if GITHUB_TOKEN:
    HEADERS_GH["Authorization"] = f"Bearer {GITHUB_TOKEN}"


# ── GitHub API ─────────────────────────────────────────────────────────────────
def fetch_all_stars(username: str) -> list[dict]:
    """分页抓取用户所有 Star 仓库"""
    stars, page = [], 1
    print(f"[GitHub] 正在抓取 @{username} 的 Star 列表...")
    while True:
        resp = requests.get(
            f"https://api.github.com/users/{username}/starred",
            headers=HEADERS_GH,
            params={"per_page": 100, "page": page},
            timeout=20,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        stars.extend(batch)
        print(f"  第 {page} 页: {len(batch)} 个 (累计 {len(stars)})")
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.3)
    print(f"[GitHub] 共 {len(stars)} 个 Star")
    return stars


def parse_repo(raw: dict) -> dict:
    """从 GitHub API 响应提取关键字段"""
    return {
        "id":          raw["id"],
        "full_name":   raw["full_name"],
        "name":        raw["name"],
        "owner":       raw["owner"]["login"],
        "html_url":    raw["html_url"],
        "description": raw.get("description") or "",
        "homepage":    raw.get("homepage") or "",
        "topics":      raw.get("topics", []),
        "language":    raw.get("language") or "",
        "stars":       raw.get("stargazers_count", 0),
        "forks":       raw.get("forks_count", 0),
        "updated_at":  raw.get("updated_at", ""),
        "starred_at":  datetime.utcnow().isoformat() + "Z",
        "category":    None,
        "subcategory": None,
    }


# ── AI 分类 (OpenAI 兼容接口) ──────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a developer librarian. Categorize GitHub repositories into a two-level taxonomy.

Return ONLY a valid JSON array, no markdown fences, no explanation. Each element must have:
- "id": (integer, same as input)
- "category": primary category string
- "subcategory": specific subcategory string

Category reference (create new ones if needed):
- AI / Machine Learning     → LLM / Chat, Computer Vision, Audio & Speech, ML Framework, Data Science, AI Agent, Prompt Engineering, Fine-tuning, Embedding & Vector DB
- Web Development           → Frontend Framework, UI Component Library, CSS & Styling, Backend Framework, Full-stack, Static Site, Web Performance, Web Security, API & REST, GraphQL
- DevOps & Infrastructure   → CI/CD, Container & K8s, Cloud Platform, Monitoring, Infrastructure as Code, Networking, Database Ops
- Programming Language      → Language Runtime, Compiler & Transpiler, Language Tool
- Developer Tools           → CLI Tool, Code Editor / IDE, Code Quality, Testing, Debugging, Package Manager, Documentation
- Database                  → Relational DB, NoSQL, Time-series, Graph DB, Search Engine, ORM & Query Builder
- Security                  → Auth & Identity, Cryptography, Penetration Testing, Secret Management, Network Security
- Mobile Development        → iOS, Android, Cross-platform, React Native / Flutter
- Game Development          → Game Engine, Graphics & Rendering, Physics, Game Tool
- Data Engineering          → Data Pipeline, Stream Processing, Data Visualization, Data Format & Serialization
- Networking & Protocol     → HTTP Client, WebSocket, RPC & gRPC, Proxy & Gateway, DNS
- System Programming        → Operating System, Embedded, Kernel & Driver, Memory Management
- Productivity & Utility    → Automation, File Management, Terminal, Note-taking, Task Management
- Learning Resource         → Tutorial, Awesome List, Book / Course, Roadmap

Be concise and consistent."""


def classify_batch(repos: list[dict]) -> dict[int, dict]:
    """调用 OpenAI 兼容接口批量分类"""
    payload = [
        {
            "id":          r["id"],
            "name":        r["full_name"],
            "description": (r["description"] or "")[:180],
            "topics":      r["topics"][:6],
            "language":    r["language"],
        }
        for r in repos
    ]

    resp = requests.post(
        f"{AI_BASE_URL.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type":  "application/json",
        },
        json={
            "model": AI_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Classify these repos:\n\n{json.dumps(payload, ensure_ascii=False)}"},
            ],
            "temperature": 0.1,
            "max_tokens":  2048,
        },
        timeout=60,
    )
    resp.raise_for_status()

    text = resp.json()["choices"][0]["message"]["content"].strip()

    # 清除可能的 markdown 代码块
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("json"):
                stripped = stripped[4:].strip()
            if stripped.startswith("["):
                text = stripped
                break

    results = json.loads(text)
    return {
        item["id"]: {
            "category":    item.get("category", "Uncategorized"),
            "subcategory": item.get("subcategory", "General"),
        }
        for item in results
    }


# ── 主流程 ─────────────────────────────────────────────────────────────────────
def main():
    if not GITHUB_USER:
        raise ValueError("环境变量 GITHUB_USER 未设置")

    print(f"[配置] 模型: {AI_MODEL}")
    print(f"[配置] API:  {AI_BASE_URL}")

    # 加载已有分类数据
    existing: dict[int, dict] = {}
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
            existing = {r["id"]: r for r in saved.get("repos", [])}
        print(f"[缓存] 已加载 {len(existing)} 条历史分类")

    # 抓取当前 Stars
    raw_stars   = fetch_all_stars(GITHUB_USER)
    current_ids = {r["id"] for r in raw_stars}
    parsed      = [parse_repo(r) for r in raw_stars]
    new_repos   = [r for r in parsed if r["id"] not in existing]
    removed_cnt = len(set(existing.keys()) - current_ids)

    print(f"[差异] 新增: {len(new_repos)}  移除: {removed_cnt}  保持: {len(existing) - removed_cnt}")

    # 对新仓库调用 AI 分类
    if new_repos and AI_API_KEY:
        total_batches = (len(new_repos) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"[AI] 开始分类 {len(new_repos)} 个新仓库，共 {total_batches} 批...")
        for i in range(0, len(new_repos), BATCH_SIZE):
            batch     = new_repos[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            print(f"  批次 {batch_num}/{total_batches} ({len(batch)} 个)...", end="", flush=True)
            try:
                result = classify_batch(batch)
                for repo in batch:
                    if repo["id"] in result:
                        repo["category"]    = result[repo["id"]]["category"]
                        repo["subcategory"] = result[repo["id"]]["subcategory"]
                print(f" ✓")
            except Exception as e:
                print(f" ✗ ({e})")
            if i + BATCH_SIZE < len(new_repos):
                time.sleep(RATE_LIMIT_GAP)
    elif new_repos:
        print("[AI] 未设置 AI_API_KEY，跳过分类")

    # 合并：保留旧分类 + 更新元数据 + 加入新仓库
    merged = {}
    for r in parsed:
        if r["id"] in existing:
            merged[r["id"]] = {
                **r,
                "category":    existing[r["id"]].get("category"),
                "subcategory": existing[r["id"]].get("subcategory"),
                "starred_at":  existing[r["id"]].get("starred_at", r["starred_at"]),
            }
        else:
            merged[r["id"]] = r

    final_repos = sorted(merged.values(), key=lambda x: x.get("starred_at", ""), reverse=True)

    # 构建分类索引
    categories: dict[str, dict[str, list]] = {}
    for repo in final_repos:
        cat = repo.get("category")  or "Uncategorized"
        sub = repo.get("subcategory") or "General"
        categories.setdefault(cat, {}).setdefault(sub, []).append(repo["id"])

    output = {
        "meta": {
            "user":            GITHUB_USER,
            "total":           len(final_repos),
            "updated_at":      datetime.utcnow().isoformat() + "Z",
            "category_count":  len(categories),
            "ai_model":        AI_MODEL if AI_API_KEY else None,
        },
        "categories": categories,
        "repos":      final_repos,
    }

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！{len(final_repos)} 个仓库，{len(categories)} 个分类")
    print(f"   已写入 → {DATA_FILE}")


if __name__ == "__main__":
    main()
