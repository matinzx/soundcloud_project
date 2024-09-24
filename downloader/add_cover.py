#!/usr/bin/python3
# -*- coding: utf-8 -*-

import eyed3
import logging
import os
from tkinter import Tk, filedialog
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(message)s')

# تابع برای تغییر اندازه تصویر به 300x300
def resize_image(image_path, size=(300, 300)):
    try:
        with Image.open(image_path) as img:
            resized_image = img.resize(size)
            resized_image.save(image_path)
            logging.info(f"Image resized to {size}")
    except Exception as e:
        logging.error(f"Error resizing image: {e}")

# تابع برای اضافه کردن تصویر کاور به فایل MP3
def add_image(art_image_path, song_filename, mime_type='image/jpeg'):
    logging.info(f"Adding cover art: {song_filename}")
    
    # تغییر اندازه تصویر به 300x300
    resize_image(art_image_path, size=(300, 300))

    audiofile = eyed3.load(song_filename)
    if audiofile is None:
        logging.error("Error loading MP3 file")
        return

    if audiofile.tag is None:
        audiofile.initTag()

    try:
        with open(art_image_path, 'rb') as image_file:
            audiofile.tag.images.set(3, image_file.read(), mime_type)
        audiofile.tag.save()
        logging.info(f"Cover image added to {song_filename}")
    except Exception as e:
        logging.error(f"Error adding cover image: {e}")

# تابع برای انتخاب تصویر توسط کاربر
def select_image():
    root = Tk()
    root.withdraw()  # مخفی کردن پنجره اصلی
    file_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    return file_path

# تابع اصلی برای افزودن کاور به فایل‌های MP3
def add_cover_art(path='.'):
    song_filenames = []
    
    if os.path.isdir(path):
        logging.info("Finding all .mp3 files in: %s", path)
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.mp3'):
                    song_filenames.append(os.path.join(root, file))
    elif os.path.isfile(path) and path.endswith('.mp3'):
        logging.info("Processing: %s", path)
        song_filenames.append(os.path.abspath(path))

    for song_filename in song_filenames:
        logging.info(f"Processing file: {song_filename}")
        art_image_path = select_image()
        if art_image_path:
            add_image(art_image_path, song_filename)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Add cover art to MP3 files from local images.")
    parser.add_argument('path', nargs='?', default=os.getcwd(), help='file or directory to be processed (default: current directory)')
    args = parser.parse_args()
    
    add_cover_art(path=args.path)
