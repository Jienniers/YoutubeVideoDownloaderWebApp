from flask import Flask, render_template, request, send_file, after_this_request
from pytubefix import YouTube
import os
import threading
import time

app = Flask(__name__)


def get_video_resolutions(url):
    try:
        yt = YouTube(url)
        highest_resolution = yt.streams.get_highest_resolution()
        return [f"{highest_resolution.resolution} (Highest)"]
    except Exception as e:
        print(f"Error: {e}")
        return []


def download_video(url):
    try:
        yt = YouTube(url)
        highest_resolution = yt.streams.filter(adaptive=True).filter(mime_type='video/mp4').first()
        if highest_resolution:
            highest_resolution.download()
            print(f"Downloading {highest_resolution.resolution} resolution...")
            return highest_resolution.default_filename
        else:
            print("No streams available for the video.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def delete_file_after_delay(file_path, sent_flag, delay_seconds=5):
    time.sleep(delay_seconds)
    try:
        if sent_flag[0]:
            os.remove(file_path)
            print(f"File deleted: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")

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
                thumbnail = YouTube(url_text).thumbnail_url
                title = f"Title: {YouTube(url_text).title}"
                visibility = "visible"
        if "download_button_mine" in request.form:
            print(stored_url)
            status = "status: Downloading"
            desired_resolution = request.form.get('dropdown', '720')
            video_path = download_video(stored_url)
            print(video_path)
            print(desired_resolution)
            if video_path:
                sent_flag = [False]
                @after_this_request
                def remove_file(response):
                    threading.Thread(target=delete_file_after_delay, args=(video_path, sent_flag)).start()
                    return response
                sent_flag[0] = True
                return send_file(
                    video_path,
                    as_attachment=True,
                    download_name=os.path.basename(video_path)
                )
            
    return render_template('index.html', thumbnail=thumbnail, title=title, un_visible=visibility)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")