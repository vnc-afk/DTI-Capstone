from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_user_notification(user_id, notification):
    channel_layer = get_channel_layer()

    if hasattr(notification, "display_message"):
        payload = {
            "id": int(notification.id),
            "message": str(notification.display_message()),
            "time": str(notification.time_display()),
            "url": str(notification.url) if notification.url else "",
            "type": str(notification.type),
            "is_read": bool(notification.is_read),
            "sender": {
                "id": notification.sender.id if notification.sender else None,
                "username": notification.sender.username if notification.sender else "System",
                "full_name": notification.sender.get_full_name() if notification.sender else "System",
                "profile_picture": (
                    str(notification.sender.profile_picture.url)
                    if notification.sender and getattr(notification.sender, "profile_picture", None)
                    else None
                )
            }
        }
    else:
        payload = notification

    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",   # fixed underscore
        {
            "type": "notification.message",   # matches consumer method
            "content": payload,
        }
    )