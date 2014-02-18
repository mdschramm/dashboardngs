from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from apps.core.views import user_name_form_view

admin.autodiscover()

UP = settings.UGLY_PREFIX
urlpatterns = patterns('',
    url(r"^%s$" % UP,
        TemplateView.as_view(template_name="home.html"),
        name="home"
        ),
    url(r"^%sanalysis/" % UP,
        include("apps.analysis.urls",
        namespace="analysis")
        ),
    url(r"^%srun-status/" % UP,
        include("apps.runstatus.urls",
        namespace="run_status")
        ),
    url(r"^%scomments/" % UP,
        include("apps.comments.urls",
        namespace="comments")
        ),
    url(r"^%supload/" % UP,
        include("apps.uploads.urls",
        namespace="uploads")
        ),
    url(r"^%sprojects/" % UP,
        include("apps.projects.urls", namespace="projects")
        ),
    url(r"^%sadmin/" % UP,
        include(admin.site.urls)
        ),
    url(r"^%saccounts/" % UP,
        include('registration.backends.default.urls')
        ),
    url(r"^%saccounts/profile/$" % UP,
        TemplateView.as_view(template_name="registration/profile.html"),
        name="profile"
        ),
    url(r"^%saccounts/edit/$" % UP,
        user_name_form_view,
        name="profile_edit"
        ),
    url(r"^dev", TemplateView.as_view(template_name="staging_redirect.html")),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = TemplateView.as_view(template_name="maintenance.html")
