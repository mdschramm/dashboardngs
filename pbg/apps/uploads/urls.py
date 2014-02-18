from django.conf.urls import patterns, include, url
from .views import upload, delete

urlpatterns = patterns('',
    url(r"upload/(\w+)/(\w+)/(\w+)/$", upload, name="upload"),
    url(r"delete/(\w+)/$", delete, name="delete"),
)
