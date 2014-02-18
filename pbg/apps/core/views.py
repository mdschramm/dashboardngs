from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UserNameForm


def user_name_form_view(request):
    user = request.user
    if request.method == "POST":
        form = UserNameForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user.first_name = cd["first_name"]
            user.last_name = cd["last_name"]
            user.save()
            return HttpResponseRedirect(reverse("profile"))
    else:
        initials = {"first_name":user.first_name, "last_name":user.last_name}
        form = UserNameForm(initial=initials)
    return render(request, "form.html", {"form":form})
