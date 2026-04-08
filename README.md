# LocalizeAgent (印尼语视频本地化智能体)

`LocalizeAgent` 是一个基于 **LangGraph** 和 **确定性状态机** 架构的视频本地化工具。它旨在实现从 YouTube 视频 URL 到“翻译字幕 + 自动配音 + 剪映草稿自动对接”的全流程自动化。

---

## 🌟 核心愿景
让视频跨越语言鸿沟。输入一个 URL，自动产出高质量的印尼语本地化素材。

---

## 🏗️ 项目架构

本项目采用“大脑与双手”解耦的设计模式，确保了在本地运行时的极致速度与稳定性。

```text
localizeagent/
├── core/               # 【大脑】逻辑与决策中心
│   ├── agent.py        # Agent 类定义（逻辑中心）
│   └── workflow.py     # 基于 LangGraph 的状态机调度
├── tools/              # 【双手】原子工具集
│   ├── youtube.py      # 字幕抓取与代理适配
│   ├── translator.py   # 谷歌/机翻引擎对接
│   ├── refiner.py      # 云端 LLM (DeepSeek/Gemini) 专家润色
│   ├── voiceover.py    # Edge TTS 异步配音生成
│   └── capcut.py       # 剪映草稿深度解析与安全注入
├── output/             # 【产物】生成的 SRT、MP3 等素材
├── main.py             # 【入口】交互式一键启动脚本
└── .env                # 【私密】API Key 与代理配置
```

---

## 🛠️ 功能特性

1.  **字幕全自动化**: 抓取 YouTube 字幕，并提供“机翻初稿 + LLM 专家润色”的双重翻译保障。
2.  **高仿真配音**: 集成印尼语神经网络语音 (Edge TTS)，生成自然人声。
3.  **剪映深度对接**: 
    - **交互式选择**: 自动扫描并让用户选择最近编辑的项目。
    - **安全注入**: 自动备份项目文件，并精准替换字幕轨道，保留原有样式。
    - **素材同步**: 自动将 SRT 和 MP3 物理同步至剪映项目的 `Resources` 目录。
4.  **安全架构**: 使用 `.env` 管理 API Key，支持并发请求与频率保护。

---

## 🚀 快速开始

### 1. 环境准备
```bash
pip install langgraph langchain-core youtube-transcript-api deep-translator edge-tts python-dotenv requests
```

### 2. 配置私密信息
复制 `.env.example` 并重命名为 `.env`，填入你的 `LLM_API_KEY`：
```bash
cp .env.example .env
```

### 3. 运行 Agent
```bash
python3 main.py
```

---

## � 迭代计划 (Roadmap)
- [ ] **Whisper 集成**: 为无字幕视频提供本地语音识别。
- [ ] **UI 界面**: 开发简单的 Web 控制台或桌面客户端。
- [ ] **批量模式**: 支持通过 URL 列表进行自动化挂机处理。

---

> **Author**: [ClearKnight](https://github.com/ClearKnight)  
> **Powered by**: Trae & Gemini-3-Flash
