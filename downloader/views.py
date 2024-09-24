from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import youtube_dl
import os
import eyed3
from PIL import Image

# تابع برای تغییر سایز تصویر به 300x300
def resize_image(image_path):
    with Image.open(image_path) as img:
        img = img.resize((300, 300))
        img.save(image_path)

# تابع برای اضافه کردن تصویر کاور به فایل MP3
def add_image(art_image_path, song_filename, mime_type='image/jpeg'):
    audiofile = eyed3.load(song_filename)
    if audiofile.tag is None:
        audiofile.initTag()
    with open(art_image_path, 'rb') as image_file:
        audiofile.tag.images.set(3, image_file.read(), mime_type)
    audiofile.tag.save()

# ویوی اصلی
def index(request):
    if request.method == 'POST':
        track_url = request.POST.get('track_url')

        if not track_url:
            return HttpResponse("URL not provided", status=400)

        try:
            ydl_opts = {
                'quiet': False,  # برای مشاهده لاگ دانلود
                'proxy': 'http://192.168.202.121:10809',  # پروکسی اگر لازم باشد
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': '%(title)s.%(ext)s',  # نام فایل خروجی
                'writethumbnail': True,  # دانلود کاور تصویر
            }

            # دانلود فایل صوتی و کاور تصویر
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(track_url, download=True)
                filename = ydl.prepare_filename(info_dict)
                base_filename, _ = os.path.splitext(filename)
                response_filename = os.path.abspath(f"{base_filename}.mp3")
                cover_path = os.path.abspath(f"{base_filename}.jpg")

                # بررسی وجود فایل صوتی و کاور
                if not os.path.exists(response_filename):
                    return HttpResponse("Error: Audio file not found.", status=500)
                if not os.path.exists(cover_path):
                    return HttpResponse("Error: Cover file not found.", status=500)

                # تغییر سایز تصویر کاور به 300x300
                resize_image(cover_path)

                # افزودن کاور به فایل صوتی
                add_image(cover_path, response_filename)

                # بازگشت فایل MP3 به کاربر به عنوان پاسخ دانلودی
                return FileResponse(open(response_filename, 'rb'), as_attachment=True, filename=os.path.basename(response_filename))

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    return render(request, 'index.html')
