from django.contrib.auth.views import LogoutView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

from .views import *
from . import views

app_name = 'blocks'
urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('main/', login_required(MianView.as_view()), name='loghome'),

    path('log-for-common/', CommonView.as_view(), name='prog1'),
    path('common/', login_required(CommonLogView.as_view()), name='workprog1'),

    path('log-for-isolation/', IsolationView.as_view(), name='prog2'),
    path('isolation/', login_required(IsolationLogView.as_view()), name='workprog2'),

    path('log-for-detection/', DetectionView.as_view(), name='prog3'),
    path('detection/', login_required(DetectionLogView.as_view()), name='workprog3'),

    path('login/', UserLoginView.as_view(), name='log'),
    path('registration/', UserRegistrationView.as_view(), name='reg'),
    path('logout/', LogoutView.as_view(), name='logout'),

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
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
