from yt_dlp import YoutubeDL # 引入 yt-dlp 模組
import os

def download_audio(url, platform):
    # 設定 yt-dlp 的選項
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'app/static/downloads/{platform}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    os.makedirs(f'app/static/downloads/{platform}', exist_ok=True)

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        return f"下載成功：{info.get('title')}"
    except Exception as e:
        return f"下載失敗：{str(e)}"
    
    # 新增：只驗證網址是否為有效影片，**不下載**
def validate_url(url, cookie_path = None):
    print(" 傳給 yt-dlp 的 cookie 路徑：", cookie_path)
    # 設定 yt-dlp 的選項
    ydl_opts = {
        'quiet': True,
        'skip_download': True
    }
    #尋找cookie檔案
    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path
        if not os.path.exists(cookie_path):
            return False, f"找不到 cookie 檔案：{cookie_path}", []
        try:
            # 嘗試讀取 cookie 檔案的前 500 個字元
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie_preview = f.read(500)
                print("Cookie 檔案內容預覽：")
                print(cookie_preview)
        except Exception as e:
            return False, f"無法讀取 cookie 檔案：{e}", []
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        ##解析支援格式
        available_formats = set()
        audio_exts = {'mp3', 'm4a', 'aac', 'opus'}
        video_exts = {'mp4', 'webm', 'mov', 'mkv'}

        for f in info.get('formats', []):
            ext = f.get('ext')
            if ext in audio_exts:
                available_formats.add(ext)
            elif ext in video_exts:
                available_formats.add(ext)
        #印出可用格式
        print("/validate:可用格式：", available_formats , "\n")
        return True, f"網址有效, 標題：{info.get('title', '未知')}", list(available_formats)#回傳可用格式

    except Exception as e:
        error_msg = str(e)
        if "NSFW tweet requires authentication" in error_msg:
            return False, "這則推文需要登入帳號才能下載，請確認你的 cookie 檔案來自登入狀態。", []
        elif "HTTP Error 403" in error_msg:
            return False, "下載被拒絕（403 Forbidden），可能是 cookie 過期或未登入。", []
        elif "cookies" in error_msg:
            return False, "缺少有效的 cookie 檔案，請重新匯出登入後的 cookie。", []
        else:
            return False, f"其他錯誤：{error_msg}", []
