
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
            return False, f"找不到 cookie 檔案：{cookie_path}", [], []
        try:
            # 嘗試讀取 cookie 檔案的前 500 個字元
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie_preview = f.read(500)
                print("Cookie 檔案內容預覽：")
                print(cookie_preview)
        except Exception as e:
            return False, f"無法讀取 cookie 檔案：{e}", [], []
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        print("yt-dlp 影片資訊標題：", info.get('title'))
        print("yt-dlp 抓到格式總數：", len(info.get('formats', [])))
        
        # 解析支援格式
        available_formats = set()
        audio_exts = {'mp3', 'm4a', 'aac', 'opus'}
        video_exts = {'mp4', 'webm', 'mov', 'mkv'}

        available_resolution_formats = set()
        # 檢查音訊和視訊格式
        for f in info.get('formats', []):
            ext = f.get('ext')
            acodec = f.get('acodec')
            vcodec = f.get('vcodec')
            height = f.get('height', None)


            # 檢查音訊和視訊編解碼器
            if acodec and acodec != 'none' and vcodec == 'none':
                available_formats.add("mp3")
            elif acodec and acodec != 'none' and vcodec and vcodec != 'none':
                available_formats.add("mp4")
            # 若 codec 判斷不到，再用 ext fallback
            elif ext in audio_exts:
                available_formats.add('mp3')
            elif ext in video_exts:
                available_formats.add('mp4')
            # 檢查解析度
            try:
                if height and isinstance(height, int):
                    res = f'{height}p'
                    available_resolution_formats.add(res)
            except Exception as e:
                print(f"無法解析{height} 的解析度：{e}")
            
        # 過濾出大於 360p 的解析度（轉成 int 後比較）並排序解析度
        filtered_resolutions = [res for res in available_resolution_formats if int(res[:-1]) >= 360]
        available_resolution_formats = sorted(filtered_resolutions, key=lambda x: int(x[:-1]))
        print("validate_url 驗證成功")
        print("可用格式：", available_formats)
        print("可用解析度：", available_resolution_formats)
        return True, f"網址有效, 標題：{info.get('title', '未知')}", list(available_formats), list(available_resolution_formats)  # 回傳可用格式

    except Exception as e:
        error_msg = str(e)
        if "NSFW tweet requires authentication" in error_msg:
            return False, "這則推文需要登入帳號才能下載，請確認你的 cookie 檔案來自登入狀態。", [], []
        elif "HTTP Error 403" in error_msg:
            return False, "下載被拒絕（403 Forbidden），可能是 cookie 過期或未登入。", [], []
        elif "cookies" in error_msg:
            return False, "缺少有效的 cookie 檔案，請重新匯出登入後的 cookie。", [], []
        else:
            return False, f"其他錯誤：{error_msg}", [], []
