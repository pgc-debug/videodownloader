import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Is line se saari external requests (Vercel) allow ho jayengi
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "running", "message": "Video Downloader API is active"}), 200

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    video_url = data['url']
    
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Duration format helper
            duration_secs = info.get('duration', 0)
            mins, secs = divmod(duration_secs, 60)
            hours, mins = divmod(mins, 60)
            duration_str = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours else f"{mins:02d}:{secs:02d}"

            formats = []
            # Only extract standard progressive or direct stream formats to keep it simple
            for f in info.get('formats', []):
                if f.get('url') and (f.get('vcodec') != 'none' or f.get('acodec') != 'none'):
                    ext = f.get('ext', 'mp4')
                    filesize_bytes = f.get('filesize') or f.get('filesize_approx')
                    filesize_str = f"{round(filesize_bytes / (1024 * 1024), 1)} MB" if filesize_bytes else "Unknown Size"
                    
                    # Target readable formats
                    resolution = f.get('resolution') or f.get('format_note') or str(f.get('height', '')) + 'p'
                    if 'audio' in str(f.get('format')).lower():
                        resolution = "Audio (MP3/M4A)"

                    formats.append({
                        'quality': resolution,
                        'ext': ext,
                        'url': f.get('url'),
                        'filesize': filesize_str
                    })

            # Reverse to show highest quality first
            formats.reverse()

            return jsonify({
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': duration_str,
                'formats': formats[:12] # Limit to top 12 best formats
            }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to parse video: {str(e)}"}), 500

@app.route('/api/download', methods=['GET'])
def download_proxy():
    video_url = request.args.get('url')
    if not video_url:
        return "Missing video stream URL", 400
        
    import requests
    from flask import Response
    
    try:
        # Render server video ko piche se stream karega
        req = requests.get(video_url, stream=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Browser ko batayen ge ki yeh ek file download hai
        headers = {
            'Content-Type': req.headers.get('Content-Type', 'video/mp4'),
            'Content-Disposition': 'attachment; filename="video.mp4"'
        }
        
        return Response(req.iter_content(chunk_size=1024*1024), headers=headers)
        
    except Exception as e:
        return f"Proxy download failed: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
