import cv2
import tkinter as tk
from tkinter import filedialog
import os
import django
from celery import shared_task

from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finditsite.settings")

django.setup()

from django.core.files import File
from blocks.models import KeyPoints, PhotoProcess

import sys


def create_photo_process(user_id):
    photo_process = PhotoProcess(user_id=user_id)
    photo_process.save()
    return photo_process


user_id = None
if len(sys.argv) > 1:
    user_id = sys.argv[1]

PhotoProcess.objects.filter(user_id=user_id).delete()

photo_process = create_photo_process(user_id)


# photo_process.status = "Waiting for photos"
# photo_process.save()

def select_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    return file_path


# photo_process.status = "Processing"
# photo_process.save()


def resize_image(image):
    if image is not None:
        return cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))
    return None


# photo_process.status = "Analyzing"
# photo_process.save()

@shared_task()
def find_key_points(template_path, reference_path, user_id):
    if template_path is None or reference_path is None:
        print("Error: Одне або обидва зображення не можуть бути завантажені.")
        photo_process.status = "Error"
        photo_process.save()
    else:
        sift = cv2.SIFT_create()

        key_points_template, descriptors_template = sift.detectAndCompute(template_path, None)
        key_points_reference, descriptors_reference = sift.detectAndCompute(reference_path, None)

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors_template, descriptors_reference, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        matched_image = cv2.drawMatches(template_path, key_points_template, reference_path, key_points_reference,
                                        good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        smaller_matched_image = resize_image(matched_image)
        if smaller_matched_image is not None:

            image_buffer = cv2.imencode(".jpg", smaller_matched_image)[1].tobytes()

            image_file = File(ContentFile(image_buffer))

            key_point = KeyPoints(user_id=user_id, category_id=1)  # Встановлення значення category_id на 1
            key_point.image.save('image.jpg', image_file, save=True)
            print("Зображення збережено у базу даних разом із user_id.")
        else:
            photo_process.status = "Error"
            photo_process.save()
            print("Error: Неможливо змінити розмір відповідного зображення.")


user_id = None
if len(sys.argv) > 1:
    user_id = sys.argv[1]

PhotoProcess.objects.filter(user_id=user_id).delete()
photo_process = create_photo_process(user_id)
photo_process.status = "Waiting for photos"
photo_process.save()

template_image_path = cv2.imread(select_image())
if template_image_path is not None:
    reference_image_path = cv2.imread(select_image())
    if reference_image_path is not None:
        photo_process.status = "Processing"
        photo_process.save()
        # print(template_image_path)
        find_key_points(template_image_path, reference_image_path, user_id)
    else:
        print("Error: Користувач не вибрав друге зображення.")
        sys.exit(1)
else:
    print("Error: Користувач не вибрав перше зображення.")
    sys.exit(1)

photo_process.status = "Ready"
photo_process.save()

"""import cv2
import json
import tkinter as tk
from tkinter import filedialog
import os
import django
from celery import shared_task
from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finditsite.settings")

django.setup()

from django.core.files import File
from blocks.models import KeyPoints, PhotoProcess

import sys


# app = Celery('finditsite')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()


def create_photo_process(user_id):
    photo_process = PhotoProcess(user_id=user_id)
    photo_process.save()
    return photo_process


user_id = None
if len(sys.argv) > 1:
    user_id = sys.argv[1]

PhotoProcess.objects.filter(user_id=user_id).delete()

photo_process = create_photo_process(user_id)


# photo_process.status = "Waiting for photos"
# photo_process.save()


def select_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    image = cv2.imread(file_path)
    return image


# photo_process.status = "Processing"
# photo_process.save()


def resize_image(image):
    if image is not None:
        return cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))
    return None


@shared_task
def find_key_points(template_image, reference_image, user_id):
    if template_image is None or reference_image is None:
        print("Error: Одне або обидва зображення не можуть бути завантажені.")
        photo_process.status = "Error"
        photo_process.save()
    else:
        sift = cv2.SIFT_create()

        key_points_template, descriptors_template = sift.detectAndCompute(template_image, None)
        key_points_reference, descriptors_reference = sift.detectAndCompute(reference_image, None)

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors_template, descriptors_reference, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        matched_image = cv2.drawMatches(template_image, key_points_template, reference_image, key_points_reference,
                                        good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        smaller_matched_image = resize_image(matched_image)
        if smaller_matched_image is not None:
            # Конвертуємо зображення у список пікселів
            pixel_list = smaller_matched_image.tolist()
            # Кодуємо у формат JSON
            image_json = json.dumps(pixel_list)

            # Отримуємо файл JSON
            image_file = ContentFile(image_json)

            key_point = KeyPoints(user_id=user_id, category_id=1)  # Встановлення значення category_id на 1
            key_point.image.save('image.json', image_file, save=True)
            print("Зображення збережено у базу даних разом із user_id.")
        else:
            photo_process.status = "Error"
            photo_process.save()
            print("Error: Неможливо змінити розмір відповідного зображення.")


user_id = None
if len(sys.argv) > 1:
    user_id = sys.argv[1]

PhotoProcess.objects.filter(user_id=user_id).delete()
photo_process = create_photo_process(user_id)
photo_process.status = "Waiting for photos"
photo_process.save()
from finditsite.celery_setup import app as celery_app

template_image = select_image()
if template_image is not None:
    reference_image = select_image()
    if reference_image is not None:
        photo_process.status = "Processing"
        photo_process.save()
        find_key_points(template_image, reference_image, user_id)
    else:
        print("Error: Користувач не вибрав друге зображення.")
        sys.exit(1)
else:
    print("Error: Користувач не вибрав перше зображення.")
    sys.exit(1)

photo_process.status = "Ready"
photo_process.save()
"""
