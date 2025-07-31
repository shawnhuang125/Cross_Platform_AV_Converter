import os
from flask import Blueprint, render_template, request, jsonify  

from app.downloader import download_audio, validate_url

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/download_verify', methods=['POST'])
def download_verify():
    try: 
        if request.content_type.startswith('application/json'):
            #第一次請求,沒有cookie的狀況
            data = request.get_json()
            url = data.get('url')
            platform = data.get('platform')
            cookie_file = None
        else:
            #第二次請求,有cookie的狀況
            url = request.form.get('url')
            platform = request.form.get('platform')
            cookie_file = request.files.get('cookie_file')
        # 檢查 URL 和平台是否存在
        if not url or not platform:
            return jsonify({'status': 'error', 'message': '缺少 URL 或平台'}), 400
        # 檢查x平台的請求 cookie 檔案是否存在
        if platform == 'x' and not cookie_file:
            return jsonify({'status': 'error', 'message': 'cookie_required'}), 400
        # 儲存cookie檔案
        cookie_path = None
        if cookie_file:
            cookie_path = f'app/static/cookies/{cookie_file.filename}'
            os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
            cookie_file.save(cookie_path)
        
        # 無論各個平台,無論是否有cookie都驗證 URL 是否有效
        is_valid, message, available_formats, available_resolutions = validate_url(url, cookie_path)
        if is_valid:
            print(f"/verify_download 驗證成功\n標題：{message}\ncookie_path: {cookie_path}\n可用格式：{', '.join(available_formats)}\n可用解析度：{', '.join(available_resolutions)}\n")
            return jsonify({
                'status': 'success', #驗證成功
                'message': message,  #驗證成功訊息
                'available_formats': available_formats, #回傳可用格式['mp3', 'mp4']
                'available_resolutions': available_resolutions #回傳可用解析度['360p', '480p']
            }), 200
        else:
            return jsonify({'status': 'error', 'message': message}), 400
            
    except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
