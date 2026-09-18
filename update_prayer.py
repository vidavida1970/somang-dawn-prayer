import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

PLAYLIST_ID = "PLkaiRsguh-Kz991rmz2yaM-6a1BatlJFT"

def get_latest_video_info():
    """유튜브 재생목록 RSS 피드를 파싱하여 최신 영상 ID 및 제목 추출"""
    rss_url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={PLAYLIST_ID}"
    req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        # XML 네임스페이스 정의
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'yt': 'http://www.youtube.com/xml/schemas/2015'
        }
        entry = root.find('atom:entry', ns)
        if entry is not None:
            video_id = entry.find('yt:videoId', ns).text
            title = entry.find('atom:title', ns).text
            return video_id, title
    except Exception as e:
        print(f"RSS 피드 조회 실패: {e}")
    return None, None

def get_prayer_text(video_id):
    """영상 자막에서 예배 초반부 목사님의 새벽기도문 추출"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
    except Exception as e:
        print(f"자막 추출 실패: {e}")
        return "당일 새벽기도 영상의 자막을 불러오는 중입니다."

    prayer_lines = []
    for item in transcript_list:
        text = item['text'].strip()
        # 안내 멘트나 음악 표시 필터링
        if text.startswith('[') and text.endswith(']'):
            continue
        prayer_lines.append(text)
        
        # 기도 종료 조건 (초반부 기도 마침 감지)
        if ("기도합니다" in text or "기도드리옵나이다" in text or "기도 드립니다" in text) and "아멘" in text:
            break
            
    # 읽기 편하도록 문맥 연결
    full_text = " ".join(prayer_lines)
    return full_text

def generate_html(video_id, video_title, prayer_text):
    """새벽 감성 디자인과 유튜브 영상이 포함된 웹페이지 생성"""
    today_str = datetime.now().strftime("%Y년 %m월 %d일")
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[소망교회] {today_str} 새벽기도문 및 예배 영상</title>
  <style>
    :root {{
      --primary-color: #1e3a5f;
      --accent-color: #2563eb;
      --text-main: #1e293b;
      --text-muted: #64748b;
      --card-bg: rgba(255, 255, 255, 0.96);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Noto Serif KR", serif;
      background: linear-gradient(180deg, #0d1b2a 0%, #1b263b 35%, #2a3d54 70%, #415a77 100%);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      padding: 40px 16px;
      color: var(--text-main);
    }}
    .container {{
      width: 100%;
      max-width: 780px;
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border-radius: 28px;
      padding: 44px 36px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.4);
    }}
    .header-badge {{
      display: inline-block;
      background: #eff6ff;
      color: #2563eb;
      font-size: 13px;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: 9999px;
      margin-bottom: 14px;
    }}
    h1 {{
      font-size: 24px;
      font-weight: 800;
      color: var(--primary-color);
      line-height: 1.4;
      margin-bottom: 10px;
    }}
    .meta-info {{
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid #e2e8f0;
    }}
    .section-title {{
      font-size: 18px;
      font-weight: 700;
      color: #0f172a;
      margin: 28px 0 16px;
      padding-left: 10px;
      border-left: 4px solid var(--accent-color);
    }}
    .prayer-content {{
      font-size: 16.5px;
      line-height: 1.95;
      color: #1e293b;
      word-break: keep-all;
      background: #f8fafc;
      padding: 28px 24px;
      border-radius: 18px;
      border: 1px solid #e2e8f0;
    }}
    .video-wrapper {{
      position: relative;
      padding-bottom: 56.25%;
      height: 0;
      overflow: hidden;
      border-radius: 18px;
      background: #000;
      margin-top: 14px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }}
    .video-wrapper iframe {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border: 0;
    }}
    .footer {{
      margin-top: 36px;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
      border-top: 1px solid #e2e8f0;
      padding-top: 20px;
    }}
    .footer a {{ color: var(--accent-color); text-decoration: none; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="container">
    <span class="header-badge">소망교회 소망새벽말씀</span>
    <h1>{today_str} 새벽기도회</h1>
    <div class="meta-info">
      <div><strong>예배 영상 제목:</strong> {video_title}</div>
      <div><strong>업데이트 일시:</strong> {today_str}</div>
    </div>

    <div class="section-title">목사님의 새벽기도문</div>
    <div class="prayer-content">
      <p>{prayer_text}</p>
    </div>

    <div class="section-title">새벽기도회 예배 영상</div>
    <div class="video-wrapper">
      <iframe src="https://www.youtube-nocookie.com/embed/{video_id}" allowfullscreen></iframe>
    </div>

    <div class="footer">
      원본 영상 출처: <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" rel="noopener noreferrer">{video_title}</a>
    </div>
  </div>
</body>
</html>"""
    return html_content

def main():
    video_id, video_title = get_latest_video_info()
    if not video_id:
        print("최신 영상을 찾을 수 없습니다.")
        return
    
    print(f"영상 확인: {video_title} ({video_id})")
    prayer_text = get_prayer_text(video_id)
    html_page = generate_html(video_id, video_title, prayer_text)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_page)
    print("index.html 성공적으로 갱신됨")

if __name__ == "__main__":
    main()
