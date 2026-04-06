import os
import ssl
import time
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeFetcher:
    def __init__(self, proxy="http://127.0.0.1:7897"):
        self.proxy = proxy
        self._setup_proxy()

    def _setup_proxy(self):
        os.environ['HTTP_PROXY'] = self.proxy
        os.environ['HTTPS_PROXY'] = self.proxy
        ssl._create_default_https_context = ssl._create_unverified_context

    def fetch(self, video_id: str):
        """抓取 YouTube 字幕"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                transcript_list = YouTubeTranscriptApi().list(video_id)
                # 尝试获取印尼语、中文或英文
                transcript = transcript_list.find_transcript(['en', 'zh', 'id'])
                return transcript.fetch()
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    raise e
