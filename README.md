# FindIt

FindIt is a Django web application that compares two photographs and renders a visual answer showing
where one appears in the other. A person registers, logs in, picks a processing mode, uploads a
template image and a reference image, and receives a processed result image together with a history of
their recent runs.

Every mode page is public, but anonymous visitors see a teaser: uploading, results, and history are
only available once logged in. Processing is synchronous — the upload POST runs the pipeline, stores
the result, and redirects back to the mode page, which renders the newest result.

## Processing modes

- **Common Pixels** — detects SIFT keypoints in both photographs, matches them with a brute-force
  matcher, and draws the surviving matches as lines across a side-by-side composition of the two
  images, halved.
- **Isolation** — resizes both photographs to their shared minimum dimensions, matches keypoints,
  estimates a homography, warps the template into the reference's geometry, and places the resized
  template beside the warped result.
- **Detection & Highlight** — resizes both photographs to their shared minimum dimensions, matches
  keypoints on grayscale versions with a FLANN matcher, estimates a homography, projects the
  template's corners onto the reference, outlines the located region with a coloured quadrilateral,
  and places the template beside it, halved.

## Uploads

Both images are required. Each must be a JPEG, PNG, or WebP no larger than 10 MB and 16 megapixels.

Images the pipeline cannot work with — a damaged file, a photograph with too few distinctive
features, or a pair with too little in common — come back as an error on the upload form, not as a
server error.

## Pages

| Method | URL | Login |
|---|---|---|
| GET | `/` | no |
| GET | `/menu/` | yes |
| GET | `/modes/<slug>/` | no — teaser when anonymous, workspace when logged in |
| POST | `/modes/<slug>/results/` | yes |
| GET, POST | `/accounts/register/` | no |
| GET, POST | `/accounts/login/` | no |
| POST | `/accounts/logout/` | yes |
| — | `/admin/` | staff |

`<slug>` is one of `common-pixels`, `isolation`, `detection`. The admin is read-only over results:
they can be browsed, filtered by mode, and searched by username, but not added or edited.

## Layout

```
finditsite/                repo root — docker-compose.yml, .env.example
└── finditsite/            Django project root
    ├── finditsite/        settings, urls, wsgi
    ├── core/              base templates, static assets, landing and menu pages, wait_for_db
    ├── accounts/          registration, login, logout
    └── recognition/       the domain
        ├── forms.py       upload validation
        ├── views.py       mode page, result creation
        ├── services/      matching.py (shared SIFT pipeline), renderers.py (per mode),
        │                  recognition.py (the single entry point)
        ├── selectors.py   read queries, always scoped to the current user
        └── models.py      ProcessingMode, RecognitionResult
```

Views resolve validated input, call one service, and return; business logic lives in `services/`,
reads in `selectors.py`, and the model holds data shape only.

## Technology

- Django 5.2, server-rendered templates, no JavaScript framework
- OpenCV (SIFT, BFMatcher, FLANN, homography estimation) and NumPy for the image processing
- Pillow for image validation and decoding behind Django's `ImageField`
- PostgreSQL 16 via psycopg 3
- python-decouple for configuration
- Docker Compose for the local stand

## Running it locally

Copy `.env.example` to `.env` at the repository root and fill in every key — the same file feeds both
`docker compose` and python-decouple:

```
SECRET_KEY  DEBUG  ALLOWED_HOSTS  DB_NAME  DB_USER  DB_PASSWORD  DB_HOST  DB_PORT
```

Then:

```
docker compose up --build
```

The application is served on http://localhost:8008 and the database on port 5005. Compose overrides
`DB_HOST` and `DB_PORT` to reach Postgres inside the network, so their values in `.env` matter only
outside Docker. Migrations run on every start; for `/admin/` create a user:

```
docker compose run --rm app python manage.py createsuperuser
```

To run it without Docker, start a PostgreSQL instance matching your `.env`, then from `finditsite/`:

```
pip install -r requirements.txt -r requirements.dev.txt
python manage.py migrate
python manage.py runserver
```

Keep `DEBUG=True` for this — with `DEBUG=False` the deployment hardening turns on `SECURE_SSL_REDIRECT`
and every plain-HTTP request to localhost is redirected away.

## Checks

From `finditsite/`, with Postgres reachable (the test runner creates its own database):

```
python manage.py check
python manage.py test
flake8 .
```

Or against the compose stand, from the repository root:

```
docker compose run --rm app sh -c "python manage.py check && python manage.py test && flake8 ."
```

`python manage.py check --deploy` is only meaningful with `DEBUG=False` and a strong `SECRET_KEY`, since
the secure cookies, SSL redirect, and HSTS are all keyed off `DEBUG`. Under those settings it reports
one remaining warning, `SECURE_HSTS_PRELOAD` — left unset deliberately, since submitting a domain to
the browser preload list is the domain owner's decision. Behind a TLS-terminating proxy,
`SECURE_PROXY_SSL_HEADER` has to be set as well, or `SECURE_SSL_REDIRECT` will loop.
