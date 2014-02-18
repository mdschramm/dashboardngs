from django.conf.urls import patterns, include, url
from .views import view, post, delete

urlpatterns = patterns('',
    url(r"view/(\w+)/(\w+)/(\w+)/$", view, name="view"),
    url(r"post/(\w+)/(\w+)/(\w+)/$", post, name="post"),
    url(r"delete/(\w+)/$", delete, name="delete"),
)

