from django.shortcuts import render, redirect
from .models import CreateUserForm, PhotoProcess
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import subprocess
from blocks.models import KeyPoints
from django.contrib.auth.decorators import login_required, user_passes_test


def index(request):
    return render(request, "blocks/index.html")


def main(request):
    return render(request, "blocks/main.html")


def common(request):
    return render(request, "blocks/common.html")


def is_admin(user):
    return user.is_superuser


def commonlog(request):
    user = request.user
    latest_photos = KeyPoints.objects.filter(user=user, category_id=1).order_by('-added_at')[:5]
    return render(request, 'blocks/commonlog.html', {'latest_photos': latest_photos})


def isolation(request):
    return render(request, "blocks/isolation.html")


def isolationlog(request):
    user = request.user
    latest_photos = KeyPoints.objects.filter(user=user, category_id=2).order_by('-added_at')[:5]
    return render(request, "blocks/isolationlog.html", {'latest_photos': latest_photos})


def detection(request):
    return render(request, "blocks/detection.html")


def detectionlog(request):
    user = request.user
    latest_photos = KeyPoints.objects.filter(user=user, category_id=3).order_by('-added_at')[:5]
    return render(request, "blocks/detectionlog.html", {'latest_photos': latest_photos})


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


from django.http import JsonResponse


def get_photo_process_status(request):
    user_id = request.GET.get('user_id')
    photo_processes = PhotoProcess.objects.filter(user_id=user_id)

    if photo_processes.exists():
        status = photo_processes[0].status
    else:
        status = "Not found"

    return JsonResponse({'status': status})


def registration(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            key_points = KeyPoints(user=user)
            key_points.save()

            messages.success(request, 'Account was created for ' + user.username)

            return redirect('log')

    context = {'form': form}
    return render(request, "blocks/registration.html", context)


def loginPG(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('loghome')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'blocks/login.html', context)


def logoutPG(request):
    logout(request)
    return redirect('log')


'''
def open_better_script(request):
    try:
        user_id = None

        if request.user.is_authenticated:
            user_id = request.user.id
        print("------------", user_id)

        subprocess.Popen(
            ['python', 'D:/work/project1/finditsite/1_better.py', str(user_id)])
        return redirect('workprog1')
    except Exception as e:
        return render(request, 'blocks/commonlog.html', {'message': f'Помилка: {str(e)}'})


def open_better_script2(request):
    try:
        user_id = None

        if request.user.is_authenticated:
            user_id = request.user.id
        print("------------", user_id)

        subprocess.Popen(
            ['python', 'D:/work/project1/finditsite/2_better.py', str(user_id)])
        return redirect('workprog2')
    except Exception as e:
        return render(request, 'blocks/isolation.html', {'message': f'Помилка: {str(e)}'})


def open_better_script3(request):
    try:
        user_id = None

        if request.user.is_authenticated:
            user_id = request.user.id
        print("------------", user_id)

        subprocess.Popen(
            ['python', 'D:/work/project1/finditsite/3_better.py', str(user_id)])
        return redirect('workprog3')
    except Exception as e:
        return render(request, 'blocks/detection.html', {'message': f'Помилка: {str(e)}'})
'''
"""
def get_latest_photo2(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        latest_photo = KeyPoints.objects.filter(user_id=user_id, category_id=2).order_by('-added_at').first()
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


def get_latest_photo3(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        latest_photo = KeyPoints.objects.filter(user_id=user_id, category_id=3).order_by('-added_at').first()
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
"""
"""
def get_latest_dates2(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        latest_dates = KeyPoints.objects.filter(user_id=user_id, category_id=2).order_by('-added_at')[:5].values(
            'added_at')
        dates_list = [entry['added_at'] for entry in latest_dates]
        return JsonResponse({'latest_dates': dates_list})
    else:
        return JsonResponse({"error": "User is not authenticated"})


def get_latest_dates3(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        latest_dates = KeyPoints.objects.filter(user_id=user_id, category_id=3).order_by('-added_at')[:5].values(
            'added_at')
        dates_list = [entry['added_at'] for entry in latest_dates]
        return JsonResponse({'latest_dates': dates_list})
    else:
        return JsonResponse({"error": "User is not authenticated"})
"""
