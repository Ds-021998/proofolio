"""Top-level URL configuration.

Three lines, three jobs:
  /admin/  Django's admin — the coordinator's back door on day one, zero code
  ""       Django's own auth URLs: login, logout, password change
  ""       everything in core/urls.py
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django.contrib.auth.urls")),
    path("", include("core.urls")),
]

handler403 = "core.views.error_403"
handler404 = "core.views.error_404"
