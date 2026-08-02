from django.urls import reverse


def navigation(request):
    if request.user.is_authenticated:
        return {
            "home_url": reverse("core:menu"),
            "user_area_partial": "core/partials/user_area_authenticated.html",
        }
    return {
        "home_url": reverse("core:landing"),
        "user_area_partial": "core/partials/user_area_anonymous.html",
    }
