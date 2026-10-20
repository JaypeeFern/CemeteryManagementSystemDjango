from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(pre_save, sender=User, dispatch_uid='dashboard.remember_user_active_status')
def remember_user_active_status(sender, instance, using, update_fields, **kwargs):
    if not instance.pk:
        instance._previous_is_active = None
        return

    instance._previous_is_active = (
        sender._default_manager.using(using)
        .filter(pk=instance.pk)
        .values_list('is_active', flat=True)
        .first()
    )


@receiver(post_save, sender=User, dispatch_uid='dashboard.revoke_sessions_on_active_status_change')
def revoke_sessions_after_active_status_change(
    sender,
    instance,
    using,
    created,
    update_fields,
    **kwargs,
):
    previous_is_active = getattr(instance, '_previous_is_active', None)
    if created or previous_is_active is None or previous_is_active == instance.is_active:
        return
    if update_fields is not None and 'is_active' not in update_fields:
        return

    # Prevent sessions from becoming valid again if this account is reactivated.
    session_keys = []
    sessions = Session.objects.using(using).filter(expire_date__gt=timezone.now())
    for session in sessions.iterator():
        if session.get_decoded().get('_auth_user_id') == str(instance.pk):
            session_keys.append(session.session_key)

    if session_keys:
        Session.objects.using(using).filter(session_key__in=session_keys).delete()
