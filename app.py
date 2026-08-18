from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)  # Allows your Vercel frontend to talk to this backend

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/api/info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
        
    ydl_opts = {
        'skip_download': True,
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Format formats to only send clean video/audio structures
            formats = []
            for f in info.get('formats', []):
                # Only grab direct HTTP download links with known extensions
                if f.get('url') and f.get('ext') in ['mp4', 'm4a', 'mp3', 'webm']:
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution') or f.get('format_note') or 'Audio',
                        'filesize': f.get('filesize') or f.get('filesize_approx') or 'Unknown',
                        'download_url': f.get('url')
                    })
            
            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "formats": formats[::-1] # Newest/Highest quality usually at the end
            })
    except Exception as e:
        return jsonify({"error": str(e)}), {500}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
