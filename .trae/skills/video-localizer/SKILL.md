---
name: "video-localizer"
description: "Automates video localization: fetches YouTube subtitles, translates with LLM refinement, generates Indonesian TTS, and integrates with CapCut. Invoke when user wants to localize a video or manage CapCut drafts."
---

# Video Localizer Skill

This skill provides a comprehensive automated workflow for localizing videos, specifically targeting the English-to-Indonesian "搬运" (video re-uploading/localization) use case.

## 🌟 Core Capabilities

1.  **Subtitle Intelligence**: Fetches timed subtitles from YouTube and provides a two-stage translation (Google Machine Translation + LLM Expert Refinement).
2.  **Voiceover Excellence**: Generates high-fidelity Indonesian neural voiceovers using Edge TTS.
3.  **CapCut Deep Integration**: 
    - Scans and lists local CapCut projects.
    - Safely injects translated subtitles into existing project tracks with style preservation.
    - Synchronizes generated SRT and MP3 files directly into the CapCut `Resources` folder.
4.  **Security & Reliability**: Manages API keys via `.env` and ensures data safety with automatic project backups (`.bak`).

## 🚀 When to Invoke

- **New Video Project**: When you have a YouTube ID and want to start the localization process.
- **Translation Quality Check**: When you need to refine existing machine translations using advanced LLM logic.
- **CapCut Sync**: When you want to find a specific CapCut draft and import localized assets into it.
- **Batch Processing**: When the user asks to process multiple videos or automate the repetitive editing tasks.

## 🛠️ Usage Guide

### 1. Initialization
Ensure the environment is ready:
- Run `python3 main.py` to start the interactive agent.
- Ensure `.env` is configured with `LLM_API_KEY` and `HTTP_PROXY`.

### 2. File Structure
- `core/agent.py`: The main logic coordinator.
- `core/workflow.py`: The LangGraph state machine.
- `tools/capcut.py`: CapCut draft manipulation logic.
- `tools/refiner.py`: LLM-based translation refinement.
- `output/`: Where all SRT, MP3, and reports are stored.

### 3. Key Commands
- **Start Agent**: `python3 main.py [video_id]`
- **Push to Git**: `git add . && git commit -m "update" && git push origin main`

## 📈 Roadmap & Evolution
- [ ] **Whisper Integration**: For videos without native subtitles.
- [ ] **Multi-language Support**: Expanding beyond Indonesian.
- [ ] **UI/Web Interface**: Providing a dashboard for the localization pipeline.
