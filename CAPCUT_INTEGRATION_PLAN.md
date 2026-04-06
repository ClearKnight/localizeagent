# 剪映 (CapCut) 自动化集成技术方案

本文档研究了如何让 Agent 具备“直接修改剪映工程”的能力，实现字幕的一键本地化。

---

## 1. 剪映工程核心原理
剪映桌面版将所有草稿存储在特定的本地目录中。每个草稿包含一个核心文件：**`draft_content.json`**。

### A. 存储路径 (Mac)
`~/Library/Containers/com.lemon.lv/Data/Library/Application Support/com.lemon.lv/drafts/`

### B. JSON 结构分析
在 `draft_content.json` 中，字幕信息存储在以下路径：
- `materials.texts`: 这里定义了所有文本素材的内容（`content` 字段）。
- `tracks`: 这里定义了视频轴，通过 `material_id` 引用上面的文本素材。

**关键点**：`content` 字段通常包含富文本标签，例如：
`[{"content":"<color=#ffffff>原始字幕内容</color>","type":"text"}]`

---

## 2. Agent 自动化逻辑设计

### 节点 A: Draft Locator (草稿定位器)
- **任务**：扫描剪映草稿目录，按修改时间排序，自动找到你刚刚打开或编辑过的那个工程。
- **输出**：草稿文件夹路径及 `draft_content.json` 的备份。

### 节点 B: Text Extractor (文本提取器)
- **任务**：解析 JSON，提取出所有属于“字幕”类型的文本块，并保留它们的 `id` 和顺序。

### 节点 C: Translation Injector (翻译注入器)
- **任务**：
  1. 调用我们的翻译引擎（MyMemory 或 LLM）。
  2. 将译文（印尼语）重新包装进原有的富文本标签中。
  3. 替换 JSON 中的 `content` 字段。

### 节点 D: Safety Checker (安全校验)
- **任务**：验证修改后的 JSON 格式是否正确，确保不会导致剪映软件崩溃。

---

## 3. 进化为 Agent 的杀手锏功能

为了让它真正像一个 Agent，我们可以加入以下“高级感知”：

1. **自动排版调整 (Auto-Layout)**:
   - 如果印尼语翻译比中文长很多，Agent 自动调小该条字幕的 `font_size` 字段，防止文字出屏。
2. **多版本对比**:
   - Agent 可以在剪映里创建一个新的“印尼语字幕轨道”，保留原轨道，让你在剪映里可以一键切换开关对比效果。
3. **闭环工作流**:
   - 你在剪映里改了一处中文，Agent 监测到文件变动，立刻在后台自动更新对应的印尼语。

---

## 4. 风险与注意事项
- **备份第一**：操作前必须强制备份 `draft_content.json`。
- **软件冲突**：在注入翻译时，必须确保剪映软件处于**关闭状态**或**退出当前草稿**，否则会产生写入冲突。

---

> **下一步构思**：编写一个 Python 工具类 `CapCutManager`，实现对 `draft_content.json` 的安全读写。
