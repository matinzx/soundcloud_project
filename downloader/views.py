from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import yt_dlp
import os
import eyed3
from PIL import Image
from django.conf import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def resize_image(image_path):
    try:
        with Image.open(image_path) as img:
            img.thumbnail((300, 300))
            img.save(image_path)
        logger.info(f"Image resized successfully: {image_path}")
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")

def add_image(art_image_path, song_filename):
    try:
        audiofile = eyed3.load(song_filename)
        if audiofile.tag is None:
            audiofile.initTag()
        
        logger.info(f"Before adding cover: Tag version: {audiofile.tag.version}, Image count: {len(audiofile.tag.images)}")
        
        with open(art_image_path, 'rb') as image_file:
            image_data = image_file.read()
            audiofile.tag.images.set(3, image_data, 'image/jpeg')
        
        audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
        
        # Reload the file to verify changes
        audiofile = eyed3.load(song_filename)
        logger.info(f"After adding cover: Tag version: {audiofile.tag.version}, Image count: {len(audiofile.tag.images)}")
        
        if len(audiofile.tag.images) > 0:
            logger.info("Cover art successfully added and verified.")
        else:
            logger.warning("Cover art was not added successfully.")
        
    except Exception as e:
        logger.error(f"Error adding cover art: {str(e)}")

def index(request):
    if request.method == 'POST':
        track_url = request.POST.get('track_url')

        if not track_url:
            return HttpResponse("URL not provided", status=400)

        try:
            downloads_dir = os.path.join(settings.BASE_DIR, 'downloads')
            os.makedirs(downloads_dir, exist_ok=True)

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
                'writethumbnail': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(track_url, download=True)
                title = info_dict['title']
                mp3_filename = f"{title}.mp3"
                response_filename = os.path.join(downloads_dir, mp3_filename)
                cover_path = os.path.join(downloads_dir, f"{title}.jpg")

                if not os.path.exists(response_filename):
                    logger.error(f"Audio file not found: {response_filename}")
                    return HttpResponse("Error: Audio file not found.", status=500)
                if not os.path.exists(cover_path):
                    logger.error(f"Cover file not found: {cover_path}")
                    return HttpResponse("Error: Cover file not found.", status=500)

                resize_image(cover_path)
                add_image(cover_path, response_filename)
                
                # Verify if cover art was added successfully
                audiofile = eyed3.load(response_filename)
                if audiofile.tag and len(audiofile.tag.images) > 0:
                    logger.info(f"Cover art found in {response_filename}")
                else:
                    logger.warning(f"No cover art found in {response_filename}")

                return FileResponse(open(response_filename, 'rb'), as_attachment=True, filename=mp3_filename)

        except Exception as e:
            logger.error(f"Error in download process: {str(e)}")
            return HttpResponse(f"Error: {str(e)}", status=500)

    return render(request, 'index.html')