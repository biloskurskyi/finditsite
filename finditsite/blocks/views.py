from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from common.views import TitleMixin
from .models import PhotoProcess
from .forms import CreateUserForm, UserLoginForm
import subprocess
from blocks.models import KeyPoints
from django.http import JsonResponse
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User


class IndexView(TitleMixin, TemplateView):
    template_name = "blocks/index.html"
    title = "FindIt"


class MianView(TitleMixin, TemplateView):
    template_name = "blocks/main.html"
    title = "FindIt - menu"


class CommonView(TitleMixin, TemplateView):
    template_name = "blocks/common.html"
    title = "FindIt - log in to use this page"


class CommonLogView(TitleMixin, TemplateView):
    template_name = "blocks/commonlog.html"
    title = "FindIt - Common img"


class IsolationView(TitleMixin, TemplateView):
    template_name = "blocks/isolation.html"
    title = "FindIt - log in to use this page"


class IsolationLogView(TitleMixin, TemplateView):
    template_name = "blocks/isolationlog.html"
    title = "FindIt - Isolation img"


class DetectionView(TitleMixin, TemplateView):
    template_name = "blocks/detection.html"
    title = "FindIt - log in to use this page"


class DetectionLogView(TitleMixin, TemplateView):
    template_name = "blocks/detectionlog.html"
    title = "FindIt - Detection img"


def open_better_script(request, script_path, redirect_path, template_name):
    try:
        user_id = None

        if request.user.is_authenticated:
            user_id = request.user.id
        print("------------", user_id)

        subprocess.Popen(['python', script_path, str(user_id)])
        return redirect(redirect_path)
    except Exception as e:
        return render(request, template_name, {'message': f'Помилка: {str(e)}'})


def get_latest_photo(request, category_id):
    if request.user.is_authenticated:
        user_id = request.user.id
        latest_photo = KeyPoints.objects.filter(user_id=user_id, category_id=category_id).order_by('-added_at').first()
        if latest_photo:
            data = {
                "image_url": latest_photo.image.url,
                "added_at": latest_photo.added_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "No latest photo available"})
    else:
        return JsonResponse({"error": "User is not authenticated"})


def get_latest_dates(request, category_id):
    if request.user.is_authenticated:
        user_id = request.user.id
        latest_dates = KeyPoints.objects.filter(user_id=user_id, category_id=category_id).order_by('-added_at')[
                       :5].values(
            'added_at')
        dates_list = [entry['added_at'] for entry in latest_dates]
        return JsonResponse({'latest_dates': dates_list})
    else:
        return JsonResponse({"error": "User is not authenticated"})


def get_photo_process_status(request):
    user_id = request.GET.get('user_id')
    photo_processes = PhotoProcess.objects.filter(user_id=user_id)

    if photo_processes.exists():
        status = photo_processes[0].status
    else:
        status = "Not found"

    return JsonResponse({'status': status})


class UserRegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = CreateUserForm
    template_name = 'blocks/registration.html'
    success_url = reverse_lazy('blocks:log')
    success_message = 'Registration is successfully done!'
    title = 'FindIt - Registration'


class UserLoginView(TitleMixin, LoginView):
    template_name = 'blocks/login.html'
    form_class = UserLoginForm
    title = 'FindIt - LogIn'


class UserChecker:
    @staticmethod
    def is_admin(user):
        return user.is_superuser
