from flask import Flask, render_template, request, send_file, after_this_request
from pytubefix import YouTube
import os
import threading
import time
from pytubefix.cli import on_progress
import shutil

app = Flask(__name__)

def downloadVideo(url):
    try:
        yt = YouTube(url, use_po_token=True, on_progress_callback = on_progress)
        streams = yt.streams.filter(res="1080p").first()
        if streams:
            streams.download("Videos/")
            print(f"Downloading: {yt.title}")
            print(f"Downloading {streams.resolution} resolution...")
            return streams.default_filename
        else:
            print("No streams available for the video.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def deleteFileAfterDelay(delay_seconds=5):
    time.sleep(delay_seconds)
    shutil.rmtree("Videos")


stored_url = ""
@app.route('/', methods=['GET', 'POST'])
def home():
    global stored_url
    thumbnail = ""
    title = ""
    visibility = "hidden"

    if request.method == 'POST':
        url_text = request.form['search_url']

        if 'search' in request.form:
            if 'search_url' in request.form and 'https' in url_text.lower():
                stored_url = url_text
                print(stored_url)
                youtube = YouTube(url_text, use_po_token=True)
                thumbnail = youtube.thumbnail_url
                title = f"Title: {youtube.title}"
                visibility = "visible"

        if "download_button_mine" in request.form:
            print(stored_url)
            status = "status: Downloading"
            filename = downloadVideo(stored_url)
            
            if '|' in filename: 
                filename = filename.replace('|', '')

            if ':' in filename:
                filename = filename.replace(':', '')

            if '*' in filename:
                filename = filename.replace('*', '')

            if '?' in filename:
                filename = filename.replace('?', '')

            if '"' in filename:
                filename = filename.replace('"', '')

            if '<' in filename:
                filename = filename.replace('<', '')

            if '>' in filename:
                filename = filename.replace('>', '')

            if '/' in filename:
                filename = filename.replace('/', '')

            if "\\" in filename:
                filename = filename.replace("\\", "")

            video_path = "Videos\\" + filename

            print(video_path)

            if video_path:
                @after_this_request
                def remove_file(response):
                    threading.Thread(target=deleteFileAfterDelay).start()
                    return response

                return send_file(
                    video_path,
                    as_attachment=True,
                    download_name=os.path.basename(video_path)
                )
            else:
                return "File download failed", 404
            
    return render_template(
        'index.html', 
        thumbnail=thumbnail, 
        title=title, 
        un_visible=visibility,
        res_visibility=visibility)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")