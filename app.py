import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "running", "message": "Universal Bypass Downloader Engine Active"}), 200

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    target_url = data['url']
    
    # Universal public un-blockable extraction mirror architecture
    api_endpoint = "https://cobalt.tools"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": target_url,
        "vQuality": "720",
        "filenamePattern": "classic"
    }

    try:
        response = requests.post(api_endpoint, json=payload, headers=headers, timeout=20)
        res_data = response.json()

        # Handle direct clean dynamic stream links
        if response.status_code == 200 and res_data.get('status') == 'stream':
            formats = [{
                'quality': 'HD Progressive (MP4)',
                'ext': 'mp4',
                'url': res_data.get('url'),
                'filesize': 'Direct Full Speed Mirror'
            }]
            return jsonify({
                'title': 'Downloaded Media File',
                'thumbnail': 'https://placehold.co',
                'duration': 'Auto-Detected',
                'formats': formats
            }), 200

        # Handle picker items formats lists arrays configurations
        elif response.status_code == 200 and res_data.get('status') == 'picker':
            formats = []
            picker_items = res_data.get('picker', [])
            for idx, item in enumerate(picker_items):
                formats.append({
                    'quality': item.get('type', 'Video') + f" Mirror {idx+1}",
                    'ext': 'mp4' if item.get('type') == 'video' else 'mp3',
                    'url': item.get('url'),
                    'filesize': 'High-Speed Stream'
                })
            return jsonify({
                'title': 'Multi-Link Media Assets Gathered',
                'thumbnail': 'https://placehold.co',
                'duration': 'Multi-Clip',
                'formats': formats[:8]
            }), 200
            
        else:
            return jsonify({"error": res_data.get('text', 'Bypass gateway did not respond correctly.')}), 400

    except Exception as e:
        return jsonify({"error": f"Bypass Server Sync Failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
