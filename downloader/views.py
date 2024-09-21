from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import youtube_dl
import os
import subprocess
import eyed3

def add_image(art_image_path, song_filename, mime_type='image/jpeg'):
    audiofile = eyed3.load(song_filename)
    if audiofile.tag is None:
        audiofile.initTag()
    audiofile.tag.images.set(3, open(art_image_path, 'rb').read(), mime_type)
    audiofile.tag.save()

def index(request):
    if request.method == 'POST':
        track_url = request.POST.get('track_url')

        if not track_url:
            return HttpResponse("URL not provided", status=400)

        try:
            ydl_opts = {
                'quiet': False,
                'proxy': 'http://192.168.202.121:10809',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': '%(title)s.%(ext)s',
                'writethumbnail': True,
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(track_url, download=True)
                filename = ydl.prepare_filename(info_dict)
                base_filename, _ = os.path.splitext(filename)
                response_filename = os.path.abspath(f"{base_filename}.mp3")
                cover_path = os.path.abspath(f"{base_filename}.jpg")

                artist = info_dict.get('artist', 'Unknown Artist')
                album = info_dict.get('album', 'Unknown Album')

                if not os.path.exists(response_filename):
                    return HttpResponse("Error: Audio file not found.", status=500)
                if not os.path.exists(cover_path):
                    return HttpResponse("Error: Cover file not found.", status=500)

                # افزودن کاور به فایل صوتی
                add_image(cover_path, response_filename)

                return FileResponse(open(response_filename, 'rb'), as_attachment=True, filename=os.path.basename(response_filename))

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    return render(request, 'index.html')
