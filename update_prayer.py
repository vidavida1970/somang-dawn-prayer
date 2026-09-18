import os
import re
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

PLAYLIST_ID = "PLkaiRsguh-Kz991rmz2yaM-6a1BatlJFT"
PRAYERS_DIR = "prayers"
ARCHIVE_FILE = "archive.json"

def get_latest_video_info():
    """유튜브 RSS 피드에서 최신 영상 정보 추출"""
    rss_url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={PLAYLIST_ID}"
    req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
        entry = root.find('atom:entry', ns)
        if entry is not None:
            video_id = entry.find('yt:videoId', ns).text
            title = entry.find('atom:title', ns).text
            return video_id, title
    except Exception as e:
        print(f"RSS 조회 실패: {e}")
    return None, None

def extract_date_from_title(title):
    """영상 제목에서 날짜(YYYYMMDD 또는 오늘 날짜) 추출"""
    match = re.search(r'(\d{8})', title)
    if match:
        d = match.group(1)
        return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    return datetime.now().strftime("%Y-%m-%d")

def get_prayer_text(video_id):
    """자막에서 목사님의 새벽기도문 추출"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
    except Exception as e:
        print(f"자막 로드 실패: {e}")
        return "당일 새벽기도 영상의 자막을 불러오는 중입니다."

    prayer_lines = []
    for item in transcript_list:
        text = item['text'].strip()
        if text.startswith('[') and text.endswith(']'):
            continue
        prayer_lines.append(text)
        if ("기도합니다" in text or "기도드리옵나이다" in text or "기도 드립니다" in text) and "아멘" in text:
            break
            
    return " ".join(prayer_lines)

def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_archive(archive):
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

def build_html_page(date_str, video_id, video_title, prayer_text, is_subpage=False, archive_list=None):
    """공통 스타일 및 카카오톡 OG 메타태그가 적용된 HTML 생성"""
    summary = prayer_text[:130].strip() + "..." if len(prayer_text) > 130 else prayer_text
    summary_clean = summary.replace('"', '&quot;')
    og_image = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1200&h=630&auto=format&fit=crop"
    
    current_url = f"https://vidavida1970.github.io/somang-dawn-prayer/{'prayers/' + date_str + '.html' if is_subpage else ''}"
    home_link = '<div style="margin-bottom: 20px;"><a href="../index.html" style="color: #2563eb; text-decoration: none; font-weight: bold;">← 오늘의 기도문(홈)으로 가기</a></div>' if is_subpage else ''

    # 지난 기도 목록 HTML 조립
    archive_html = ""
    if not is_subpage and archive_list:
        archive_items = ""
        for item in archive_list:
            archive_items += f"""
            <a href="prayers/{item['date']}.html" class="archive-item">
              <span class="archive-date">📅 {item['date']}</span>
              <span class="archive-title">{item['title']}</span>
            </a>"""
        archive_html = f"""
        <div class="section-title">지난 새벽기도문 다시보기</div>
        <div class="archive-box">{archive_items}</div>
        """

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="소망교회 소망새벽말씀">
  <meta property="og:title" content="[소망교회] {date_str} 새벽기도문">
  <meta property="og:description" content="{summary_clean}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:url" content="{current_url}">

  <title>[소망교회] {date_str} 새벽기도문</title>
  <style>
    :root {{ --primary: #1e3a5f; --accent: #2563eb; --text: #1e293b; --muted: #64748b; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Noto Serif KR", serif;
      background: linear-gradient(180deg, #0d1b2a 0%, #1b263b 35%, #2a3d54 70%, #415a77 100%);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      padding: 40px 16px;
      color: var(--text);
    }}
    .container {{
      width: 100%;
      max-width: 780px;
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(16px);
      border-radius: 28px;
      padding: 44px 36px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.4);
    }}
    .badge {{
      display: inline-block;
      background: #eff6ff;
      color: #2563eb;
      font-size: 13px;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: 9999px;
      margin-bottom: 14px;
    }}
    h1 {{ font-size: 24px; font-weight: 800; color: var(--primary); line-height: 1.4; margin-bottom: 8px; }}
    .meta {{ font-size: 14px; color: var(--muted); margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #e2e8f0; }}
    .section-title {{ font-size: 18px; font-weight: 700; color: #0f172a; margin: 28px 0 16px; padding-left: 10px; border-left: 4px solid var(--accent); }}
    .prayer-content {{ font-size: 16.5px; line-height: 1.95; color: #1e293b; word-break: keep-all; background: #f8fafc; padding: 28px 24px; border-radius: 18px; border: 1px solid #e2e8f0; }}
    .video-wrapper {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 18px; background: #000; margin-top: 14px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); }}
    .video-wrapper iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }}
    .archive-box {{ display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }}
    .archive-item {{ display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; background: #f1f5f9; border-radius: 12px; text-decoration: none; color: var(--text); font-size: 14.5px; transition: background 0.2s; }}
    .archive-item:hover {{ background: #e2e8f0; }}
    .archive-date {{ font-weight: 700; color: #2563eb; flex-shrink: 0; margin-right: 12px; }}
    .archive-title {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .footer {{ margin-top: 36px; text-align: center; font-size: 13px; color: var(--muted); border-top: 1px solid #e2e8f0; padding-top: 20px; }}
  </style>
</head>
<body>
  <div class="container">
    {home_link}
    <span class="badge">소망교회 소망새벽말씀</span>
    <h1>{date_str} 새벽기도회</h1>
    <div class="meta">
      <div><strong>말씀 본문 / 영상:</strong> {video_title}</div>
    </div>

    <div class="section-title">목사님의 새벽기도문</div>
    <div class="prayer-content">
      <p>{prayer_text}</p>
    </div>

    <div class="section-title">새벽기도회 예배 영상</div>
    <div class="video-wrapper">
      <iframe src="https://www.youtube-nocookie.com/embed/{video_id}" allowfullscreen></iframe>
    </div>

    {archive_html}

    <div class="footer">
      출처: <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" rel="noopener noreferrer">{video_title}</a>
    </div>
  </div>
</body>
</html>"""

def main():
    os.makedirs(PRAYERS_DIR, exist_ok=True)
    video_id, video_title = get_latest_video_info()
    if not video_id:
        print("최신 영상을 찾지 못했습니다.")
        return

    date_str = extract_date_from_title(video_title)
    print(f"[{date_str}] 영상 확인: {video_title}")

    prayer_text = get_prayer_text(video_id)

    # 1. 날짜별 개별 파일 저장 (prayers/YYYY-MM-DD.html)
    subpage_html = build_html_page(date_str, video_id, video_title, prayer_text, is_subpage=True)
    subpage_path = os.path.join(PRAYERS_DIR, f"{date_str}.html")
    with open(subpage_path, "w", encoding="utf-8") as f:
        f.write(subpage_html)

    # 2. 아카이브 목록 갱신
    archive = load_archive()
    # 중복 방지 (기존 동일 날짜가 있으면 갱신)
    archive = [item for item in archive if item['date'] != date_str]
    archive.insert(0, {"date": date_str, "title": video_title, "id": video_id})
    save_archive(archive)

    # 3. 메인 index.html 갱신 (최신 기도문 + 지난 기도문 목록 포함)
    index_html = build_html_page(date_str, video_id, video_title, prayer_text, is_subpage=False, archive_list=archive)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"업데이트 완료: {subpage_path} 및 index.html 갱신 완료 (누적 {len(archive)}개)")

if __name__ == "__main__":
    main()
