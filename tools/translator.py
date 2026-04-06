import re
import time
from typing import List, Dict
from deep_translator import MyMemoryTranslator

class SubtitleTranslator:
    def __init__(self, source='english', target='indonesian'):
        self.translator = MyMemoryTranslator(source=source, target=target)

    def clean_text(self, text: str) -> str:
        """清洗字幕文本：移除音乐符号和方括号内容"""
        text = text.replace("♪", "")
        text = re.sub(r'\[.*?\]', '', text).strip()
        return text

    def translate_batch(self, raw_data: List[Dict], batch_size: int = 10) -> List[Dict]:
        """批量翻译字幕"""
        translated_data = []
        for i in range(0, len(raw_data), batch_size):
            batch = raw_data[i : i + batch_size]
            for entry in batch:
                # 兼容字典和对象两种访问方式
                if isinstance(entry, dict):
                    original_text = entry.get('text', '')
                    start = entry.get('start', 0)
                    duration = entry.get('duration', 0)
                else:
                    # 如果是 FetchedTranscriptSnippet 对象
                    original_text = getattr(entry, 'text', '')
                    start = getattr(entry, 'start', 0)
                    duration = getattr(entry, 'duration', 0)

                clean_text = self.clean_text(original_text)
                
                if not clean_text:
                    translated_text = ""
                else:
                    try:
                        translated_text = self.translator.translate(clean_text)
                    except:
                        translated_text = clean_text # 失败保底
                
                translated_data.append({
                    'start': start,
                    'end': start + duration,
                    'text': translated_text
                })
            time.sleep(0.5)
        return translated_data
