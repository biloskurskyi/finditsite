import cv2
import numpy as np

from recognition.models import ProcessingMode
from recognition.services.detectors import build_matcher, get_detector
from recognition.services.matching import (find_homography, find_matches,
                                           normalize_dimensions)

QUADRILATERAL_COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0)]
QUADRILATERAL_THICKNESS = 7


def halve(image):
    height, width = image.shape[:2]
    return cv2.resize(image, (width // 2, height // 2))


def corner_point(corners, index):
    return tuple(map(int, corners[index][0]))


def render_common_pixels(template_image, reference_image):
    detector = get_detector()
    match = find_matches(
        template_image, reference_image, build_matcher(detector), detector
    )
    composite = cv2.drawMatches(
        template_image,
        match.template_keypoints,
        reference_image,
        match.reference_keypoints,
        match.good_matches,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
    return halve(composite)


def render_isolation(template_image, reference_image):
    template_image, reference_image = normalize_dimensions(
        template_image, reference_image
    )
    detector = get_detector()
    match = find_matches(
        template_image, reference_image, build_matcher(detector), detector
    )
    homography = find_homography(match.template_keypoints, match.reference_keypoints, match.good_matches)
    aligned_template = cv2.warpPerspective(
        template_image,
        homography,
        (reference_image.shape[1], reference_image.shape[0]),
    )
    return cv2.hconcat([halve(template_image), halve(aligned_template)])


def render_detection(template_image, reference_image):
    template_image, reference_image = normalize_dimensions(
        template_image, reference_image
    )
    detector = get_detector()
    match = find_matches(
        cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY),
        build_matcher(detector, use_flann=True),
        detector,
    )
    homography = find_homography(match.template_keypoints, match.reference_keypoints, match.good_matches)
    height, width = template_image.shape[:2]
    template_corners = np.float32(
        [[0, 0], [width, 0], [width, height], [0, height]]
    ).reshape(-1, 1, 2)
    projected_corners = cv2.perspectiveTransform(template_corners, homography)

    highlighted_reference = reference_image.copy()
    for index in range(4):
        cv2.line(
            highlighted_reference,
            corner_point(projected_corners, index),
            corner_point(projected_corners, (index + 1) % 4),
            QUADRILATERAL_COLORS[index % 3],
            QUADRILATERAL_THICKNESS,
        )
    combined = cv2.hconcat([template_image, highlighted_reference])
    return cv2.resize(combined, None, fx=0.5, fy=0.5)


RENDERERS = {
    ProcessingMode.COMMON_PIXELS: render_common_pixels,
    ProcessingMode.ISOLATION: render_isolation,
    ProcessingMode.DETECTION: render_detection,
}


def render(mode, template_image, reference_image):
    return RENDERERS[mode](template_image, reference_image)
