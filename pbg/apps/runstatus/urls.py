from django.conf.urls import patterns, include, url
from apps.runstatus.views import (run_status, mark_as_aborted,
        send_info_to_node2)

urlpatterns = patterns('',
    url(r"^$", run_status, {"machine":"Amee"}, name="run_status"),
    url(r"^machine/(\w+)/$", run_status, name="run_status"),
    url(r"^run-abort-form/(\w+)/(\d+)/$", mark_as_aborted, name="mark_as_aborted"),
    url(r"^node2-form/$", send_info_to_node2, name="send_info_to_node2"),
)
