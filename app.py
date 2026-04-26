from flask import Flask, render_template, request, send_file, send_from_directory
import yt_dlp
import os
from datetime import datetime

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Serve robots.txt and sitemap.xml
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

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    option = request.form.get('option')
    resolution = request.form.get('resolution')

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s [%(id)s].%(ext)s',
        'noplaylist': True,
        'embedthumbnail': True,
    }

    if option == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })
    elif resolution and resolution != "best":
        ydl_opts['format'] = f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]'
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'

    if request.form.get('subtitles') == 'yes':
        ydl_opts.update({
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'embedsubs': True
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)