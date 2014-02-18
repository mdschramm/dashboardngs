from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    projects = models.ManyToManyField(
            'analysis.Project', blank=True, null=True
            )
    studies = models.ManyToManyField('projects.Study', blank=True, null=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)

def send_email_on_creation(sender, instance, created, **kwargs):
    if created:
        subject = "DASHBOARD NGS NEW USER"
        message = """\
                  A new user signed up with the following credentials:
                  username: {0}
                  email: {1}
                  """.format(instance.username, instance.email)
        from_email = settings.EMAIL_HOST_USER
        admins = User.objects.filter(is_staff=True)
        admin_emails = [admin.email for admin in admins]
        send_mail(subject, message, from_email, admin_emails)
post_save.connect(send_email_on_creation, sender=User)
