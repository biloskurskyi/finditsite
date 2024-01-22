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


def find_image(template_path, reference_path, user_id):
    if template_path is None or reference_path is None:
        print("Error: One or both images could not be loaded.")
    else:
        sift = cv2.SIFT_create()

        key_points_template, descriptors_template = sift.detectAndCompute(template_path, None)
        key_points_reference, descriptors_reference = sift.detectAndCompute(reference_path, None)

        bf = cv2.BFMatcher()

        matches = bf.knnMatch(descriptors_template, descriptors_reference, k=2)

        good_matches = []
        ratio_threshold = 0.75
        for m, n in matches:
            if m.distance < ratio_threshold * n.distance:
                good_matches.append(m)

        src_pts = np.float32([key_points_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([key_points_reference[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        homography_matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        aligned_template = cv2.warpPerspective(template_path, homography_matrix,
                                               (reference_path.shape[1], reference_path.shape[0]))

        smaller_template = cv2.resize(template_path, (template_path.shape[1] // 2, template_path.shape[0] // 2))
        smaller_aligned_template = cv2.resize(aligned_template,
                                              (aligned_template.shape[1] // 2, aligned_template.shape[0] // 2))

        combined_image = cv2.hconcat([smaller_template, smaller_aligned_template])
        if combined_image is not None:

            image_buffer = cv2.imencode(".jpg", combined_image)[1].tobytes()

            image_file = File(ContentFile(image_buffer))

            key_point = KeyPoints(user_id=user_id, category_id=2)  # Встановлення значення category_id на 1
            key_point.image.save('image.jpg', image_file, save=True)
            print("Зображення збережено у базу даних разом із user_id.")
        else:
            photo_process.status = "Error"
            photo_process.save()
            print("Error: Неможливо змінити розмір відповідного зображення.")

        """ Відображення об'єднаного зображення
        cv2.imshow('Combined Image', combined_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()"""


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
        find_image(template_image_path, reference_image_path, user_id)
    else:
        print("Error: Користувач не вибрав друге зображення.")
        sys.exit(1)
else:
    print("Error: Користувач не вибрав перше зображення.")
    sys.exit(1)

photo_process.status = "Ready"
photo_process.save()

'''
template_image1_path = cv2.imread(select_image())
reference_image1_path = cv2.imread(select_image())
find_image(template_image1_path, reference_image1_path)

        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(template_path, cv2.COLOR_BGR2RGB))
        plt.title('Template Image')

        plt.subplot(1, 2, 2)
        plt.imshow(cv2.cvtColor(aligned_template, cv2.COLOR_BGR2RGB))
        plt.title('Aligned Template Image')
        plt.show()
'''

# find_image(template_image2_path, reference_image2_path)
# find_image(template_image3_path, reference_image3_path)
# find_image(template_image6_path, reference_image6_path)
# find_image(template_image6_path, reference_image7_path)


'''template_image2_path = cv2.imread('template_tea_cup_pad_2.jpg')
reference_image2_path = cv2.imread('find_tea_cup_pad_pose.jpg')
template_image3_path = cv2.imread('photo_2023-10-17_18-45-31.jpg')
reference_image3_path = cv2.imread('photo_2023-10-17_18-45-50.jpg')
template_image6_path = cv2.imread('paris1.jpg')
reference_image6_path = cv2.imread('paris2.jpg')
reference_image7_path = cv2.imread('paris3.jpg')
'''
