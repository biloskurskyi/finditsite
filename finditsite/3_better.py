import os
import tkinter as tk
from tkinter import filedialog

import cv2
import django
import numpy as np
from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finditsite.settings")

django.setup()

import sys

from blocks.models import KeyPoints, PhotoProcess
from django.core.files import File


def create_photo_process(user_id):
    photo_process = PhotoProcess(user_id=user_id)
    photo_process.save()
    return photo_process


user_id = None
if len(sys.argv) > 1:
    user_id = sys.argv[1]

PhotoProcess.objects.filter(user_id=user_id).delete()

photo_process = create_photo_process(user_id)
photo_process.status = "Waiting for photos"
photo_process.save()


def select_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    return file_path


photo_process.status = "Processing"
photo_process.save()


def resize_image(image):
    if image is not None:
        return cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))
    return None


photo_process.status = "Analyzing"
photo_process.save()


def resize_and_find_and_display_on_picture(template_path, reference_path, user_id):
    template_image = cv2.imread(template_path)
    reference_image = cv2.imread(reference_path)

    if template_image is None or reference_image is None:
        print("Error: One or both images could not be loaded.")
        return

    if template_image.shape != reference_image.shape:
        height, width = min(template_image.shape[0], reference_image.shape[0]), min(template_image.shape[1],
                                                                                    reference_image.shape[1])
        template_image = cv2.resize(template_image, (width, height))
        reference_image = cv2.resize(reference_image, (width, height))

    template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
    reference_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()

    key_points_template, descriptors_template = sift.detectAndCompute(template_gray, None)
    key_points_reference, descriptors_reference = sift.detectAndCompute(reference_gray, None)

    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(descriptors_template, descriptors_reference, k=2)

    good_matches = []
    ratio_threshold = 0.75
    for m, n in matches:
        if m.distance < ratio_threshold * n.distance:
            good_matches.append(m)

    src_pts = np.float32([key_points_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([key_points_reference[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    homography_matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    template_corners = np.array(
        [[0, 0], [template_image.shape[1], 0], [template_image.shape[1], template_image.shape[0]],
         [0, template_image.shape[0]]],
        dtype=np.float32).reshape(-1, 1, 2)

    projected_corners = cv2.perspectiveTransform(template_corners, homography_matrix)

    reference_with_cuboid = reference_image.copy()
    colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0)]
    for i in range(4):
        pt1 = tuple(map(int, projected_corners[i][0]))
        pt2 = tuple(map(int, projected_corners[(i + 1) % 4][0]))
        cv2.line(reference_with_cuboid, pt1, pt2, colors[i % 3], 7)

    combined_image = cv2.hconcat([template_image, reference_with_cuboid])

    resized_combined_image = cv2.resize(combined_image, None, fx=0.5, fy=0.5)

    if resized_combined_image is not None:

        image_buffer = cv2.imencode(".jpg", combined_image)[1].tobytes()

        image_file = File(ContentFile(image_buffer))

        key_point = KeyPoints(user_id=user_id, category_id=3)
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

template_image_path = select_image()
if template_image_path is not None and os.path.isfile(template_image_path):
    reference_image_path = select_image()
    if reference_image_path is not None and os.path.isfile(reference_image_path):
        photo_process.status = "Processing"
        photo_process.save()
        resize_and_find_and_display_on_picture(template_image_path, reference_image_path, user_id)
    else:
        print("Error: Користувач не вибрав друге зображення.")
        sys.exit(1)
else:
    print("Error: Користувач не вибрав перше зображення.")
    sys.exit(1)

photo_process.status = "Ready"
photo_process.save()
