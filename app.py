import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Aapki asli RapidAPI Key jo screenshot mein hai
RAPIDAPI_KEY = "42c5e277b0msh39fe483a134e3aap19efb5jsn6afbd66c1a92"
# All-in-One stable API host destination
RAPIDAPI_HOST = "://rapidapi.com"

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "running", "message": "RapidAPI Multi-Downloader Engine Active"}), 200

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    target_url = data['url']
    
    # RapidAPI standard endpoint configuration
    url = f"https://{RAPIDAPI_HOST}/api/v1/downloader"
    querystring = {"url": target_url}
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=25)
        res_data = response.json()

        if response.status_code != 200 or not res_data.get('success', False):
            return jsonify({"error": res_data.get('message', 'API failed to parse media links.')}), 400

        links = res_data.get('data', [])
        formats = []
        
        for item in links:
            # Map quality configurations to clean strings
            quality_label = item.get('quality', 'HD Quality')
            if 'audio' in str(item.get('type', '')).lower():
                quality_label = "Audio (MP3)"

            formats.append({
                'quality': quality_label,
                'ext': item.get('extension', 'mp4'),
                'url': item.get('url'),
                'filesize': item.get('formattedSize', 'Standard Size')
            })

        return jsonify({
            'title': res_data.get('title', 'Downloaded Media File'),
            'thumbnail': res_data.get('picture', ''),
            'duration': res_data.get('duration', 'N/A'),
            'formats': formats
        }), 200

    except Exception as e:
        return jsonify({"error": f"API Gateway Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
