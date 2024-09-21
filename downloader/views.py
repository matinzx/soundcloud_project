from django.http import HttpResponse
from django.shortcuts import render
import os
import youtube_dl

def index(request):
    if request.method == 'POST':
        track_url = request.POST.get('track_url')
        
        # مسیر فایل به صورت موقت
        download_path = os.path.join(os.getcwd(), 'downloaded_track.%(ext)s')
        
        # تنظیمات youtube_dl
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': download_path,  # فایل را در دایرکتوری فعلی ذخیره کن
            'noplaylist': True,
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(track_url)
            file_url = ydl.prepare_filename(info)  # مسیر فایل دانلود شده
            file_name = f"{info['title']}.mp3"  # نام فایل نهایی

        # ارسال فایل برای دانلود در مرورگر
        with open(file_url, 'rb') as f:
            response = HttpResponse(f.read(), content_type='audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        
    return render(request, 'index.html')
