from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates')

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_status = {}


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.root_path, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.root_path, 'sitemap.xml')


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/status/<token>')
def status(token):
    return jsonify({'status': download_status.get(token, 'pending')})

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    option = request.form.get('option', 'best')
    resolution = request.form.get('resolution', '1080')
    token = request.form.get('token', '')

    if token:
        download_status[token] = 'pending'

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s [%(id)s].%(ext)s',
        'noplaylist': True,
        'cookiefile': 'cookies.txt',
        'prefer_ffmpeg': True,
    }

    if option == "audio":
        bitrate = resolution if resolution in ('192', '128', '96') else '192'
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            }],
        })
    else:
        res = resolution if resolution.isdigit() else '1080'
        ydl_opts.update({
            'format': f'bestvideo[height<={res}]+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    if request.form.get('subtitles') == 'yes':
        ydl_opts.update({
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'embedsubs': True,
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                base = filename.rsplit('.', 1)[0]
                filename = base + ('.mp3' if option == 'audio' else '.mp4')
            if token:
                download_status[token] = 'done'
            return send_file(filename, as_attachment=True)
    except Exception as e:
        if token:
            download_status[token] = 'error'
        print("Error:", str(e))
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)