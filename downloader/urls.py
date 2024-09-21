from django.urls import path
from . import views  # وارد کردن views از اپلیکیشن

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.index, name='download'),
]
