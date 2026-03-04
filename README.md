# ⭐ GitHub Stars 收藏展示

> 自动抓取你的 GitHub Star，用 AI 智能分类，生成精美展示页面，免费托管在 GitHub Pages，每天定时更新。

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-在线-brightgreen?style=flat-square&logo=github)](.)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-自动更新-blue?style=flat-square&logo=githubactions)](.)
[![AI 分类](https://img.shields.io/badge/AI-智能分类-orange?style=flat-square)](.)

**[English](#english) | 中文（默认）**

---

## ✨ 功能特色

| 特性 | 说明 |
|------|------|
| 🤖 AI 智能分类 | 支持一级 + 二级分类，自动识别仓库类型 |
| 🔄 增量更新 | 只对新 Star 调用 AI，节省 API 费用 |
| ⚙️ 自定义 AI 供应商 | 兼容 OpenAI 接口，支持国内外主流模型 |
| 📅 定时同步 | GitHub Actions 每天自动运行，无需干预 |
| 🔍 全文搜索 | 按名称、描述、语言、话题实时搜索 |
| 📐 双视图 | 网格卡片 / 紧凑列表自由切换 |
| 🌏 中英双语 | 界面默认中文，一键切换英文 |
| 🎨 精美 UI | 仿 iCloud 毛玻璃风格，响应式适配移动端 |

---

## 🚀 五分钟快速部署

### 第一步：Fork 本仓库

点击右上角 **Fork**，仓库名随意。

### 第二步：开启 GitHub Pages

进入 **Settings → Pages**：
- Source：**Deploy from a branch**
- Branch：`main`，文件夹选 `/docs`
- 保存后站点地址为：`https://<你的用户名>.github.io/<仓库名>/`

### 第三步：配置 Secrets 和 Variables

进入 **Settings → Secrets and variables → Actions**：

#### Repository Variables（变量）
| 名称 | 值 | 说明 |
|------|----|------|
| `GITHUB_USER` | `your-github-username` | 你的 GitHub 用户名（必填） |
| `AI_BASE_URL` | 见下方供应商表 | AI 接口地址（选填，有默认值） |
| `AI_MODEL` | 见下方供应商表 | AI 模型名称（选填，有默认值） |

#### Repository Secrets（密钥）
| 名称 | 值 | 说明 |
|------|----|------|
| `AI_API_KEY` | `sk-...` | AI 服务的 API Key（必填） |

> `GITHUB_TOKEN` 由 GitHub Actions 自动提供，**无需手动添加**。

### 第四步：触发第一次运行

进入 **Actions → ✨ 更新 GitHub Stars → Run workflow**，点击绿色按钮手动运行。

首次运行大约需要 1～5 分钟（取决于 Star 数量）。运行完成后，等待 Pages 部署（约 1 分钟）即可访问。🎉

---

## ⚙️ AI 供应商配置

支持所有兼容 OpenAI Chat Completions 接口的服务商：

| 供应商 | `AI_BASE_URL` | `AI_MODEL` 示例 | 特点 |
|--------|---------------|-----------------|------|
| **Anthropic**（默认）| `https://api.anthropic.com/openai/v1` | `claude-haiku-4-5-20251001` | 原生支持，效果好 |
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o-mini` | 效果稳定 |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` | 国内可用，价格低 |
| **阿里通义** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo` | 国内快速 |
| **月之暗面(Kimi)** | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` | 中文效果好 |
| **智谱 AI** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | 免费额度大 |
| **Groq** | `https://api.groq.com/openai/v1` | `llama3-8b-8192` | 推理极快 |
| **本地 Ollama** | `http://localhost:11434/v1` | `llama3.2` | 完全免费 |

**成本参考（以 Anthropic Haiku 为例）：**
- 初次运行 1000 个 Star ≈ **$0.05～$0.10**
- 后续每日增量（0～10 个新 Star）≈ **$0.001 以下**

---

## 📁 项目结构

```
├── .github/
│   └── workflows/
│       └── update-stars.yml     # 定时更新工作流
├── docs/                        # GitHub Pages 根目录
│   ├── index.html               # 展示页面（纯静态，无需构建）
│   └── data/
│       └── stars.json           # 自动生成的分类数据
├── scripts/
│   └── fetch_and_classify.py    # 抓取 + AI 分类脚本
├── requirements.txt
└── README.md
```

---

## 🛠 本地开发

```bash
# 克隆仓库
git clone https://github.com/<你的用户名>/<仓库名>.git
cd <仓库名>

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GITHUB_USER="your-username"
export AI_API_KEY="sk-ant-..."
# export AI_BASE_URL="https://api.openai.com/v1"   # 可选，切换供应商
# export AI_MODEL="gpt-4o-mini"                     # 可选，切换模型

# 运行脚本
python scripts/fetch_and_classify.py

# 本地预览
cd docs && python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

---

## 🔧 自定义配置

### 修改更新频率

编辑 `.github/workflows/update-stars.yml` 中的 cron 表达式：

```yaml
# 每天北京时间 10:00
- cron: "0 2 * * *"

# 每 12 小时
- cron: "0 */12 * * *"

# 每周日
- cron: "0 2 * * 0"
```

### 自定义分类体系

修改 `scripts/fetch_and_classify.py` 中的 `SYSTEM_PROMPT`，添加或调整你自己的分类规则。

### 更改 AI 模型

直接修改 GitHub Variables 中的 `AI_MODEL`，无需改代码。

---

## 📄 许可证

[MIT License](LICENSE) — 自由使用、修改和分发。

---

<a id="english"></a>

# ⭐ GitHub Stars Showcase — English

> Automatically fetch your GitHub stars, classify them with AI, and display them on a beautiful page hosted on GitHub Pages with daily auto-updates.

## ✨ Features

- 🤖 **AI classification** — Primary + subcategory taxonomy using any OpenAI-compatible API
- 🔄 **Incremental updates** — Only new stars are sent to AI, saving API costs
- ⚙️ **Custom AI provider** — Works with OpenAI, Anthropic, DeepSeek, or any OpenAI-compatible API
- 📅 **Daily sync** — GitHub Actions runs automatically every night
- 🔍 **Full-text search** — Search by name, description, language, or topic
- 📐 **Grid / List view** — Toggle between card grid and compact list
- 🌏 **Bilingual UI** — Default Chinese, switch to English with one click
- 🎨 **iCloud-style UI** — Frosted glass design, fully responsive

## 🚀 Quick Setup (5 minutes)

**1. Fork this repo**

**2. Enable GitHub Pages**
> Settings → Pages → Branch: `main`, Folder: `/docs`

**3. Set Secrets & Variables**
> Settings → Secrets and variables → Actions

| Type | Name | Value |
|------|------|-------|
| Variable | `GITHUB_USER` | Your GitHub username |
| Variable | `AI_BASE_URL` | AI API base URL (optional, has default) |
| Variable | `AI_MODEL` | Model name (optional, has default) |
| Secret | `AI_API_KEY` | Your API key |

**4. Run the first sync**
> Actions → ✨ 更新 GitHub Stars → Run workflow

Your site will be live at `https://<you>.github.io/<repo>/` in ~2 minutes!

## Supported AI Providers

Any service compatible with the OpenAI Chat Completions API works. See the table in the Chinese section above for a full list including OpenAI, Anthropic, DeepSeek, Qwen, Moonshot, and more.

## License

[MIT](LICENSE)
