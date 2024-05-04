from django.urls import path, include
from example_app import urls as app_urls

urlpatterns = [path("", include(app_urls))]
