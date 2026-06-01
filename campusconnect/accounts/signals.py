from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


def ensure_groups():
    """
    Ensure all role-based groups exist.
    """
    for role in ["admin", "teacher", "student"]:
        Group.objects.get_or_create(name=role)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def add_user_to_group(sender, instance, created, **kwargs):
    ensure_groups()  # make sure groups exist

    if created and instance.role:
        group, _ = Group.objects.get_or_create(name=instance.role)
        instance.groups.add(group)
