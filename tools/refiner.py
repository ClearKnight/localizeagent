import json
import requests
from typing import List, Dict

class TranslationRefiner:
    def __init__(self, model="qwen2.5:7b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/generate"

    def refine_batch(self, original_texts: List[str], machine_translations: List[str]) -> List[str]:
        """
        使用 LLM 对机翻结果进行微调和润色
        """
        refined_results = []
        
        # 为了效率，我们分小批次处理，或者单条处理以保证精准度
        # 这里采用单条处理逻辑，方便模型对比原文和译文
        for orig, machine in zip(original_texts, machine_translations):
            if not orig.strip():
                refined_results.append("")
                continue
                
            prompt = f"""你是一位精通英语和印尼语的专业视频字幕审校专家。
请根据提供的【英文原文】和【Google机翻结果】，对机翻结果进行微调。

你的任务：
1. 修正语法错误和不地道的表达。
2. 确保语气符合视频语境（通常为自然、口语化）。
3. 严格控制长度，使其简洁有力，适合作为字幕。
4. 如果机翻已经非常完美，则保持不变。

【英文原文】：{orig}
【Google机翻结果】：{machine}

请直接输出微调后的【印尼语译文】，不要包含任何解释或额外文字。
微调后的译文："""

            try:
                response = requests.post(
                    self.base_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3}
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    refined_text = response.json().get("response", "").strip()
                    # 去掉可能存在的引号
                    refined_text = refined_text.replace('"', '').replace('「', '').replace('」', '')
                    refined_results.append(refined_text)
                else:
                    refined_results.append(machine) # 失败则回退到机翻
            except Exception as e:
                # print(f"⚠️ 润色节点连接失败 (Ollama 可能未启动): {e}")
                refined_results.append(machine) # 失败则回退到机翻
                
        return refined_results
