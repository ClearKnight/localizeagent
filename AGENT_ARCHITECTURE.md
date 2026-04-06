# VideoLocalize-Agent 架构方案设计 (v2.0 - 已实现基础框架)

本文档详细描述了如何将现有的 YouTube 翻译工作流升级为一个具备自主决策能力的 **AI Agent**。

---

## 1. 核心愿景
构建一个“输入 URL，输出本地化视频成品”的智能体。它不仅能翻译，还能感知视频状态、自主选择工具、并对输出质量负责。

---

## 2. 现已实现的 Agent 基础框架 (v1.5)

目前项目已完成核心模块重构并整合为 `VideoLocalizeAgent`。

### A. 核心模块 (Tools)
1. **Subtitle Fetcher (`tools/translator/workflow.py`)**:
   - 自动抓取 YouTube 结构化字幕数据。
   - 使用 `MyMemory` 引擎进行高效翻译。
2. **Voice Over Generator (`tools/translator/voiceover.py`)**:
   - 集成 `edge-tts` 异步生成高仿真印尼语配音。
3. **CapCut Manager (`tools/capcut/manager.py`)**:
   - 自动发现本地剪映草稿并尝试解析内容（支持 `Timelines` 深度结构）。

### B. 执行器 (`agent_executor.py`)
- 整合上述工具，实现“一键翻译+配音+草稿检测”流程。

---

## 3. 下阶段 Agent 进化目标 (Roadmap)

1. **第一阶段：自适应素材处理 (待处理)**
   - **Whisper 集成**: 当视频无字幕时，自动启动 Whisper 进行音频转录。
   - **自动重试机制**: 遇到代理失败或连接超时时，自动切换端口。

2. **第二阶段：剪映深度集成 (进行中)**
   - **破解加密草稿**: 探索新版剪映加密 JSON 的读取与修改。
   - **自动注入字幕**: 将生成的 SRT 自动注入到草稿轨道中。

3. **第三阶段：质量闭环 (待处理)**
   - **翻译校验**: 使用更高阶模型 (如 GPT-4o) 对翻译结果进行语法与风格审核。
   - **音频合成**: 使用 `FFmpeg` 将生成的配音与原视频自动合成预览版。
