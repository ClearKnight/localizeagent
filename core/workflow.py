import os
import time
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from tools.youtube import YouTubeFetcher
from tools.translator import SubtitleTranslator

# 1. 定义状态
class GraphState(MessagesState):
    video_id: str
    raw_transcript: List[Dict]  # 存储带时间戳的原始数据
    translated_transcript: List[Dict] # 存储带时间戳的译文数据

# 2. 工具函数：秒转 SRT 时间格式 (00:00:00,000)
def format_time(seconds: float) -> str:
    td_hours = int(seconds // 3600)
    td_mins = int((seconds % 3600) // 60)
    td_secs = int(seconds % 60)
    td_msecs = int((seconds - int(seconds)) * 1000)
    return f"{td_hours:02d}:{td_mins:02d}:{td_secs:02d},{td_msecs:03d}"

# 3. 定义节点逻辑
def fetch_subtitle_node(state: GraphState):
    """抓取结构化字幕数据"""
    video_id = state.get("video_id") or state["messages"][-1].content
    print(f"\n[1/2] 正在抓取视频 {video_id} 的原始字幕数据...")
    
    fetcher = YouTubeFetcher()
    try:
        data = fetcher.fetch(video_id)
        print(f"✅ 抓取成功！共 {len(data)} 条字幕轴。")
        return {
            "raw_transcript": data,
            "video_id": video_id,
            "messages": [SystemMessage(content=f"获取到 {len(data)} 条字幕轴")]
        }
    except Exception as e:
        print(f"❌ 抓取彻底失败: {str(e)}")
        return {"messages": [AIMessage(content=f"抓取失败: {str(e)}")]}

def translate_to_srt_node(state: GraphState):
    """逐行清洗并翻译，保持时间轴不变"""
    raw_data = state.get("raw_transcript", [])
    if not raw_data:
        return {"messages": [AIMessage(content="无字幕数据")]}
    
    print(f"\n[2/2] 开始 SRT 逐行翻译（MyMemory 引擎）...")
    translator = SubtitleTranslator(source='english', target='indonesian')
    
    start_time_total = time.time()
    translated_data = translator.translate_batch(raw_data)

    elapsed_time = time.time() - start_time_total
    print(f"✅ SRT 翻译完成！总耗时: {elapsed_time:.2f} 秒")
    
    return {
        "translated_transcript": translated_data,
        "messages": [AIMessage(content="SRT 数据处理完成")]
    }

# 4. 构建工作流
def create_workflow():
    workflow = StateGraph(GraphState)
    workflow.add_node("fetch", fetch_subtitle_node)
    workflow.add_node("translate", translate_to_srt_node)

    workflow.add_edge(START, "fetch")
    workflow.add_edge("fetch", "translate")
    workflow.add_edge("translate", END)
    return workflow.compile()

app = create_workflow()
