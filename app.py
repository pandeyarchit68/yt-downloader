from flask import Flask, render_template, request, send_file, send_from_directory
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates')

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.root_path, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.root_path, 'sitemap.xml')

import re
import os

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    option = request.form.get('option', 'best')

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s',
        'noplaylist': True,
        'cookiefile': 'cookies.txt',
        'prefer_ffmpeg': True,
    }

    if option == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        })
    else:
        # Strong force for 1080p
        ydl_opts.update({
            'format': '137+251/248+251/136+251/137/best',
            'merge_output_format': 'mp4',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_file = ydl.prepare_filename(info)

            if option == "audio":
                final_file = f"{DOWNLOAD_FOLDER}/{info.get('id')}.mp3"
            else:
                final_file = f"{DOWNLOAD_FOLDER}/{info.get('id')}.mp4"

            if os.path.exists(temp_file):
                os.rename(temp_file, final_file)
                filename = final_file
            else:
                filename = temp_file

            return send_file(filename, as_attachment=True)
    except Exception as e:
        print("Error:", str(e))
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)