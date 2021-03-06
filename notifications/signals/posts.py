import telegram
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from bot.common import ADMIN_CHAT, send_telegram_message, render_html_message, CLUB_ONLINE
from posts.models import Post


@receiver(post_save, sender=Post)
def create_or_update_post(sender, instance, created, **kwargs):
    if instance.type == Post.TYPE_INTRO and instance.is_visible and "text" in instance.changed_fields:
        # send intro updates to moderators
        async_task(
            send_telegram_message,
            chat=ADMIN_CHAT,
            text=render_html_message("moderator_updated_intro.html", user=instance.author, intro=instance),
        )
        return None

    if not created and "is_visible" not in instance.changed_fields:
        return None  # we're not interested in updates, only if they change visibility

    if instance.type in {Post.TYPE_WEEKLY_DIGEST}:
        return None  # skip emails

    if not instance.is_visible:
        return None  # skip drafts too

    async_task(async_create_or_update_post, instance, created)


def async_create_or_update_post(post, is_created):
    if not post.is_approved_by_moderator:
        send_telegram_message(
            chat=ADMIN_CHAT,
            text=render_html_message("moderator_new_post_review.html", post=post),
            reply_markup=telegram.InlineKeyboardMarkup([
                [
                    telegram.InlineKeyboardButton("👍 Одобрить", callback_data=f"approve_post:{post.id}"),
                    telegram.InlineKeyboardButton("😕 Так себе", callback_data=f"forgive_post:{post.id}"),
                ],
                [
                    telegram.InlineKeyboardButton("❌ В черновики", callback_data=f"delete_post:{post.id}"),
                ]
            ])
        )

    # post to online channel
    send_telegram_message(
        chat=CLUB_ONLINE,
        text=render_html_message("channel_post_announce.html", post=post),
        parse_mode=telegram.ParseMode.HTML,
        disable_preview=True,
    )
