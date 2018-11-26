"""SecretSanta URL Configuration
"""
from django.contrib import admin, auth
from django.conf.urls.static import static
from django.urls import path, include
from SecretSanta import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('social_django.urls', namespace='social')),
    path("test", views.test),
    path("favicon.ico", views.favicon),
    path("about", views.about),
    path("", views.home),
    path("contact", views.contact),
    path("robots.txt", views.robots),
    path("sitemap.xml", views.sitemap),
    path("logout", views.log_user_out),
    path("shuffle", views.shuffle),
    path("notes", views.notes),
    path("createnote", views.createnote),
    path("editnote", views.editnote),
    path("removenote", views.deletenote),
    path("graph", views.graph),
    path("settings", views.settings),
    path("editfam", views.editfamily),
    path("editgroup", views.editgroup),
    path("testmail", views.testmail),
    path("recreategraph", views.regraph),
    path("secretgraph", views.secretgraph),
    path("giftingto", views.updatenotestatus),
] + static("static/", document_root="./static")
