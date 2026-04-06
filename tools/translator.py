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
                clean_text = self.clean_text(entry.get('text', ''))
                
                if not clean_text:
                    translated_text = ""
                else:
                    try:
                        translated_text = self.translator.translate(clean_text)
                    except:
                        translated_text = clean_text # 失败保底
                
                translated_data.append({
                    'start': entry['start'],
                    'end': entry['start'] + entry.get('duration', 0),
                    'text': translated_text
                })
            time.sleep(0.5)
        return translated_data
