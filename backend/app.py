from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import uuid
import subprocess
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
METADATA_FILE = 'videos.json'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return []
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_metadata(metadata):
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def get_video_duration(filepath):
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except:
        return 0

def change_video_speed(input_path, output_path, speed):
    if speed == 1.0:
        import shutil
        shutil.copy2(input_path, output_path)
        return True
    
    try:
        atempo_filters = []
        remaining_speed = speed
        
        while remaining_speed > 2.0:
            atempo_filters.append('atempo=2.0')
            remaining_speed /= 2.0
        while remaining_speed < 0.5:
            atempo_filters.append('atempo=0.5')
            remaining_speed *= 2.0
        
        atempo_filters.append(f'atempo={remaining_speed}')
        audio_filter = ','.join(atempo_filters)
        
        video_speed = 1.0 / speed
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-filter:v', f'setpts={video_speed}*PTS',
            '-filter:a', audio_filter,
            '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error processing video: {e}")
        return False

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': '没有视频文件'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400
    
    video_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'mp4'
    new_filename = f"{video_id}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    
    file.save(filepath)
    
    duration = get_video_duration(filepath)
    file_size = os.path.getsize(filepath)
    
    metadata = load_metadata()
    video_info = {
        'id': video_id,
        'filename': filename,
        'stored_filename': new_filename,
        'upload_time': datetime.now().isoformat(),
        'duration': duration,
        'file_size': file_size
    }
    metadata.insert(0, video_info)
    save_metadata(metadata)
    
    return jsonify({
        'success': True,
        'video': video_info
    })

@app.route('/api/videos', methods=['GET'])
def list_videos():
    metadata = load_metadata()
    return jsonify({
        'success': True,
        'videos': metadata
    })

@app.route('/api/video/<video_id>', methods=['GET'])
def get_video(video_id):
    metadata = load_metadata()
    video_info = None
    
    for v in metadata:
        if v['id'] == video_id:
            video_info = v
            break
    
    if not video_info:
        return jsonify({'error': '视频不存在'}), 404
    
    speed = request.args.get('speed', '1.0')
    try:
        speed = float(speed)
        if speed < 0.1 or speed > 5.0:
            speed = 1.0
    except:
        speed = 1.0
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], video_info['stored_filename'])
    if not os.path.exists(filepath):
        return jsonify({'error': '视频文件不存在'}), 404
    
    range_header = request.headers.get('Range', None)
    
    if range_header:
        def generate():
            with open(filepath, 'rb') as f:
                f.seek(int(range_header.split('=')[1].split('-')[0]))
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    yield chunk
        
        return Response(generate(), 206, content_type='video/mp4')
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], video_info['stored_filename'])

@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    metadata = load_metadata()
    video_info = None
    
    for v in metadata:
        if v['id'] == video_id:
            video_info = v
            break
    
    if not video_info:
        return jsonify({'error': '视频不存在'}), 404
    
    speed = request.args.get('speed', '1.0')
    try:
        speed = float(speed)
        if speed < 0.1 or speed > 5.0:
            speed = 1.0
    except:
        speed = 1.0
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], video_info['stored_filename'])
    if not os.path.exists(input_path):
        return jsonify({'error': '视频文件不存在'}), 404
    
    ext = video_info['stored_filename'].rsplit('.', 1)[1].lower() if '.' in video_info['stored_filename'] else 'mp4'
    
    if speed == 1.0:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            video_info['stored_filename'],
            as_attachment=True,
            download_name=video_info['filename']
        )
    
    processed_filename = f"{video_id}_{speed}x.{ext}"
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
    
    if not os.path.exists(processed_path):
        success = change_video_speed(input_path, processed_path, speed)
        if not success:
            return jsonify({'error': '视频处理失败'}), 500
    
    base_name = video_info['filename'].rsplit('.', 1)[0] if '.' in video_info['filename'] else video_info['filename']
    download_name = f"{base_name}_{speed}x.{ext}"
    
    return send_from_directory(
        app.config['PROCESSED_FOLDER'],
        processed_filename,
        as_attachment=True,
        download_name=download_name
    )

@app.route('/api/video/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    metadata = load_metadata()
    video_index = None
    
    for i, v in enumerate(metadata):
        if v['id'] == video_id:
            video_index = i
            break
    
    if video_index is None:
        return jsonify({'error': '视频不存在'}), 404
    
    video_info = metadata[video_index]
    
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], video_info['stored_filename'])
    if os.path.exists(upload_path):
        os.remove(upload_path)
    
    ext = video_info['stored_filename'].rsplit('.', 1)[1].lower() if '.' in video_info['stored_filename'] else 'mp4'
    for filename in os.listdir(app.config['PROCESSED_FOLDER']):
        if filename.startswith(f"{video_id}_") and filename.endswith(f".{ext}"):
            filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
    
    del metadata[video_index]
    save_metadata(metadata)
    
    return jsonify({'success': True})

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)
