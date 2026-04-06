# LocalizeAgent (印尼语视频本地化智能体)

`LocalizeAgent` 是一个基于 **LangGraph** 和 **确定性状态机** 架构的视频本地化工具。它旨在实现从 YouTube 视频 URL 到“翻译字幕 + 自动配音 + 剪映草稿自动检测”的全流程自动化。

---

## 🌟 核心愿景
让视频跨越语言鸿沟。输入一个 URL，自动产出高质量的印尼语本地化素材。

---

## 🏗️ 项目架构

本项目采用“大脑与双手”解耦的设计模式，确保了在本地运行时的极致速度与稳定性。

```text
localizeagent/
├── core/               # 【大脑】决策中心
│   └── workflow.py     # 基于 LangGraph 的状态机调度逻辑
├── tools/              # 【双手】原子工具集
│   ├── youtube.py      # 字幕抓取与代理适配
│   ├── translator.py   # 文本清洗与 MyMemory 翻译对接
│   ├── voiceover.py    # Edge TTS 异步配音生成
│   └── capcut.py       # 剪映草稿深度解析
├── output/             # 【产物】生成的 SRT、MP3 等素材
├── main.py             # 【入口】一键启动 Agent
└── AGENT_ARCHITECTURE.md # 详细架构设计文档
```

---

## 🚀 快速开始

### 1. 环境准备
确保已安装 Python 3.10+，并安装必要依赖：

```bash
pip install langgraph langchain-core youtube-transcript-api deep-translator edge-tts ffmpeg-python
```

### 2. 配置代理
为了稳定抓取 YouTube 字幕，请确保你的 SOCKS5/HTTP 代理已开启（默认配置为 `http://127.0.0.1:7897`）。

### 3. 运行 Agent
```bash
# 翻译默认视频 (dQw4w9WgXcQ)
python3 main.py

# 翻译指定视频
python3 main.py [YOUR_VIDEO_ID]
```

---

## 🛠️ 功能特性
- **高性能翻译**: 舍弃笨重的本地小模型，采用专业的翻译引擎，实现毫秒级响应。
- **高仿真配音**: 集成印尼语神经网络语音，生成极其自然的人声。
- **剪映适配**: 自动发现本地最近编辑的剪映项目，并检测字幕注入可能性。
- **模块化设计**: 易于扩展。你可以轻松将翻译引擎更换为 GPT-4 或 Qwen。

---

## 📈 Roadmap
- [ ] **Whisper 集成**: 当视频无现成字幕时，自动开启语音转文字。
- [ ] **自动注入**: 破解剪映加密草稿，实现真正的“一键替换”。
- [ ] **多语种支持**: 扩展到日语、泰语、越南语等更多东南亚语种。

---

> **Author**: [ClearKnight](https://github.com/ClearKnight)  
> **Powered by**: Trae & Gemini-3-Flash
