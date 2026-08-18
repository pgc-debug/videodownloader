import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "running", "message": "Downloader Engine Ready"}), 200

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    video_url = data['url']
    
    # Fully dynamic browser configuration to pull un-blockable dynamic mirrors
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            duration_secs = info.get('duration', 0)
            mins, secs = divmod(duration_secs, 60)
            hours, mins = divmod(mins, 60)
            duration_str = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours else f"{mins:02d}:{secs:02d}"

            formats = []
            
            # Extract standard accessible URLs directly
            for f in info.get('formats', []):
                if f.get('url') and (f.get('vcodec') != 'none' or f.get('acodec') != 'none'):
                    ext = f.get('ext', 'mp4')
                    filesize_bytes = f.get('filesize') or f.get('filesize_approx')
                    filesize_str = f"{round(filesize_bytes / (1024 * 1024), 1)} MB" if filesize_bytes else "HD Quality"
                    
                    resolution = f.get('resolution') or f.get('format_note') or str(f.get('height', '')) + 'p'
                    if 'audio' in str(f.get('format')).lower():
                        resolution = "Audio (MP3)"

                    formats.append({
                        'quality': resolution,
                        'ext': ext,
                        'url': f.get('url'),
                        'filesize': filesize_str
                    })

            if not formats:
                # Fallback format mirror configuration
                formats.append({
                    'quality': 'HD Progressive',
                    'ext': 'mp4',
                    'url': info.get('url'),
                    'filesize': 'Direct Stream'
                })

            formats.reverse()

            return jsonify({
                'title': info.get('title', 'Downloaded Media File'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': duration_str,
                'formats': formats[:6]
            }), 200

    except Exception as e:
        return jsonify({"error": f"Extraction limit hit: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
