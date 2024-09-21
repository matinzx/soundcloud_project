from django.contrib import admin
from downloader import views

from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('downloader.urls')),  # مطمئن شوید که نام اپلیکیشن صحیح است
]
