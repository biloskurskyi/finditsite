from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from .views import *
from . import views

urlpatterns = [
    path('', index, name='home'),
    path('log-for-common/', common, name='prog1'),
    path('log-for-isolation/', isolation, name='prog2'),
    path('log-for-detection/', detection, name='prog3'),
    path('common/', login_required(commonlog), name='workprog1'),
    path('isolation/', login_required(isolationlog), name='workprog2'),
    path('detection/', login_required(detectionlog), name='workprog3'),
    path('main/', login_required(main), name='loghome'),
    path('login/', views.loginPG, name='log'),
    path('registration/', views.registration, name='reg'),
    path('logout/', views.logoutPG, name='logout'),

    path('open_better_script/', views.open_better_script,
         {'script_path': 'D:/work/project1/finditsite/1_better.py', 'redirect_path': 'workprog1',
          'template_name': 'blocks/commonlog.html'}, name='open_better_script'),
    path('open_better_script2/', views.open_better_script,
         {'script_path': 'D:/work/project1/finditsite/2_better.py', 'redirect_path': 'workprog2',
          'template_name': 'blocks/isolationlog.html'}, name='open_better_script2'),
    path('open_better_script3/', views.open_better_script,
         {'script_path': 'D:/work/project1/finditsite/3_better.py', 'redirect_path': 'workprog3',
          'template_name': 'blocks/detectionlog.html'}, name='open_better_script3'),

    path('get_latest_photo/', views.get_latest_photo, {'category_id': '1'}, name='get_latest_photo'),
    path('get_latest_photo2/', views.get_latest_photo, {'category_id': '2'}, name='get_latest_photo2'),
    path('get_latest_photo3/', views.get_latest_photo, {'category_id': '3'}, name='get_latest_photo3'),
    path('get_latest_dates/', views.get_latest_dates, {'category_id': '1'}, name='get_latest_dates'),
    path('get_latest_dates2/', views.get_latest_dates, {'category_id': '2'}, name='get_latest_dates2'),
    path('get_latest_dates3/', views.get_latest_dates, {'category_id': '3'}, name='get_latest_dates3'),

    path('get_photo_process_status/', views.get_photo_process_status, name='get_photo_process_status'),

]
# path('your_view/', your_view, name='your_view')
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# .\venv1\Scripts\activate
# .\venv2\Scripts\activate
# .\venv\Scripts\activate
# cd D:\work\project1\finditsite
# python manage.py runserver
# cmd /c "D:\work\project1\finditsite\venv1\Scripts\activate & python D:\work\project1\finditsite\manage.py runserver"
# python manage.py makemigrations
# python manage.py migrate blocks
# python manage.py runserver 8080
# python manage.py runserver 8081
# taskkill /IM celery.exe /F
# celery -A finditsite.celery_setup worker -l info
# celery -A finditsite.celery_setup beat -l INFO

# Mike2
# Mike9876
"""path('open_better_script_isolation/', views.open_better_script_isolation, name='open_better_script_isolation'),
    path('get_latest_photo_isolation/', views.get_latest_photo_isolation, name='get_latest_photo_isolation'),
    path('get_latest_dates_isolation/', views.get_latest_dates_isolation, name='get_latest_dates_isolation'),
    path('get_photo_process_status_isolation/', views.get_photo_process_status_isolation,
         name='get_photo_process_status_isolation'),"""
# python manage.py createsuperuser
# path('get_latest_photo/', views.get_latest_photo, name='get_latest_photo'),
# path('get_latest_photo2/', views.get_latest_photo2, name='get_latest_photo2'),
# path('get_latest_photo3/', views.get_latest_photo3, name='get_latest_photo3'),
# path('get_latest_dates2/', views.get_latest_dates2, name='get_latest_dates2'),
# path('get_latest_dates3/', views.get_latest_dates3, name='get_latest_dates3'),
# path('open_better_script/', views.open_better_script, name='open_better_script'),
# path('open_better_script2/', views.open_better_script2, name='open_better_script2'),
# path('open_better_script3/', views.open_better_script3, name='open_better_script3'),
# tasklist | findstr nginx
# taskkill /IM nginx.exe /F
