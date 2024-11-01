import pip
import os
import threading
import time
import shutil
import sys
import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from pytubefix.cli import on_progress
    from pytubefix import YouTube
except ImportError:
    print("Module 'pytubefix' is not installed. Installing now.")
    install('pytubefix')
    try:
        from pytubefix.cli import on_progress
        from pytubefix import YouTube
    except ImportError as e:
        print(f"Failed to import 'pytubefix' after installation: {e}")
        sys.exit(1)

try:
    from flask import Flask, render_template, request, send_file, after_this_request
except ImportError:
    if sys.platform.startswith("win"):
        os.system("python -m pip install flask")
    else:
        os.system("python3 -m pip install flask")
    try:
        from flask import Flask, render_template, request, send_file, after_this_request
    except ImportError:
        print("You need python3 installed! Main")
        exit()


try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    if sys.platform.startswith("win"):
        os.system("python -m pip install moviepy")
    else:
        os.system("python3 -m pip install moviepy")
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip
    except ImportError:
        print("You need python3 installed! Main")
        exit()

app = Flask(__name__)

def downloadVideo(url):
    try:
        yt = YouTube(url, use_po_token=True, on_progress_callback = on_progress)

        videoStreams = yt.streams.filter(res="1080p").first()
        audioStreams = yt.streams.filter(only_audio=True).first()

        if videoStreams and audioStreams:

            print(f"Downloading: {yt.title}")
            print(f"Downloading {videoStreams.resolution} resolution...")


            videoStreams.download("Videos/")
            audioStreams.download("Videos/")

            print("\nDone Downloading")

            VideoFileName = videoStreams.default_filename
            AudioFileName = audioStreams.default_filename

            if '|' in VideoFileName: 
                VideoFileName = VideoFileName.replace('|', '')

            if ':' in VideoFileName:
                VideoFileName = VideoFileName.replace(':', '')

            if '*' in VideoFileName:
                VideoFileName = VideoPath.replace('*', '')

            if '?' in VideoFileName:
                VideoFileName = VideoFileName.replace('?', '')

            if '"' in VideoFileName:
                VideoFileName = VideoFileName.replace('"', '')

            if '<' in VideoFileName:
                VideoFileName = VideoFileName.replace('<', '')

            if '>' in VideoFileName:
                VideoFileName = VideoFileName.replace('>', '')

            if '/' in VideoFileName:
                VideoFileName = VideoFileName.replace('/', '')

            if "\\" in VideoFileName:
                VideoFileName = VideoFileName.replace("\\", "")

                #Audio Path

            if '|' in AudioFileName: 
                AudioFileName = AudioFileName.replace('|', '')

            if ':' in AudioFileName:
                AudioFileName = AudioFileName.replace(':', '')

            if '*' in AudioFileName:
                AudioFileName = AudioFileName.replace('*', '')

            if '?' in AudioFileName:
                AudioFileName = AudioFileName.replace('?', '')

            if '"' in AudioFileName:
                AudioFileName = AudioFileName.replace('"', '')

            if '<' in AudioFileName:
                AudioFileName = AudioFileName.replace('<', '')

            if '>' in AudioFileName:
                AudioFileName = AudioFileName.replace('>', '')

            if '/' in AudioFileName:
                AudioFileName = AudioFileName.replace('/', '')

            if "\\" in AudioFileName:
                AudioFileName = AudioFileName.replace("\\", "")

            VideoPath = os.path.join('Videos', VideoFileName)
            AudioPath = os.path.join('Videos', AudioFileName)
            OutputPath = os.path.join('Videos', "Final " + VideoFileName)


            video_clip = VideoFileClip(VideoPath)
            audio_clip = AudioFileClip(AudioPath)

            final_clip = video_clip.set_audio(audio_clip)

            final_clip.write_videofile(OutputPath, codec="libx264", audio_codec="aac")

            print("Merging complete!")

            print(f"VideoPath: {VideoPath}")
            print(f"AudioPath: {AudioPath}")
            print(f"SoundPath: {OutputPath}")

            return "Final " + videoStreams.default_filename
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
    status = "Status: "
    if request.method == 'POST':
        url_text = request.form['search_url']

        if 'search' in request.form:
            if 'search_url' in request.form and 'https' in url_text.lower():
                status = "Status: Processing...!"
                stored_url = url_text
                print(stored_url)
                youtube = YouTube(url_text, use_po_token=True)
                thumbnail = youtube.thumbnail_url
                title = f"Title: {youtube.title}"
                visibility = "visible"
                status = "Status: "

        if "download_button_mine" in request.form:
            print(stored_url)
            status = "Status: Downloading...!"
            filename = downloadVideo(stored_url)

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
        res_visibility=visibility,)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")