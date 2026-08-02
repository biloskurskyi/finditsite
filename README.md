# FindIt

FindIt is a Django web application that compares two photographs and renders a visual answer showing
where one appears in the other. A person registers, logs in, picks a processing mode, uploads a
template image and a reference image, and receives a processed result image together with a history of
their recent runs.

## Processing modes

- **Common Pixels** — detects SIFT keypoints in both photographs, matches them, and draws the surviving
  matches as lines across a side-by-side composition of the two images.
- **Isolation** — matches keypoints, estimates a homography between the two photographs, warps the
  template into the reference's geometry, and places the original template beside the warped result.
- **Detection & Highlight** — matches keypoints on grayscale versions of both photographs, estimates a
  homography, projects the template's corners onto the reference, and outlines the located region with
  a coloured quadrilateral.

## Technology

- Django 5.2, server-rendered templates, no JavaScript framework
- OpenCV (SIFT, BFMatcher, FLANN, homography estimation) and NumPy for the image processing
- Pillow for image storage
- PostgreSQL 16
- python-decouple for configuration

## Running it locally

Copy `.env.example` to `.env` and fill in every key, then:

```
docker compose up --build
```

The application is served on http://localhost:8008 and the database on port 5005.

To run it without Docker, start a PostgreSQL instance matching your `.env`, then from `finditsite/`:

```
pip install -r requirements.txt -r requirements.dev.txt
python manage.py migrate
python manage.py runserver
```

## Checks

From `finditsite/`:

```
python manage.py check
python manage.py test
flake8 .
```
