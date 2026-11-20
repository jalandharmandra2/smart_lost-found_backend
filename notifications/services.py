import logging
from django.conf import settings
from django.core.mail import send_mail
from .models import Notification

logger = logging.getLogger(__name__)

def create_in_app_notification(recipient, notification_type, title, message, action_url=""):
    """
    Persist an in-app notification for the specified user.
    """
    try:
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to create in-app notification: {e}")
        return None


def send_email_notification(recipient_email, subject, message):
    """
    Send an email notification using Django's configured email backend.
    """
    if not recipient_email:
        return False
    try:
        send_mail(
            subject=f"[Smart Lost & Found] {subject}",
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@smartlostfound.com'),
            recipient_list=[recipient_email],
            fail_silently=True,
        )
        return True
    except Exception as e:
        logger.warning(f"Email dispatch failed: {e}")
        return False


def notify_potential_match(match_record):
    """
    Notify both the lost-item owner and the found-item finder about an AI match.
    """
    lost_item = match_record.lost_item
    found_item = match_record.found_item
    pct = int(match_record.total_score * 100)

    # 1. Notify Lost Item Owner
    title_owner = f"Potential AI Match Found: {lost_item.item_name} ({pct}% match)"
    msg_owner = (
        f"Great news! Our AI engine identified a potential match for your lost '{lost_item.item_name}'. "
        f"An item matching its photograph and description was reported in '{found_item.found_location}'. "
        f"Match Confidence: {match_record.match_label} ({pct}%)."
    )
    action_owner = f"/matches"
    create_in_app_notification(lost_item.user, 'MATCH_FOUND', title_owner, msg_owner, action_owner)
    send_email_notification(lost_item.user.email, title_owner, msg_owner)

    # 2. Notify Finder
    title_finder = f"Your found item may match a reported lost item ({pct}% match)"
    msg_finder = (
        f"The '{found_item.item_name}' you reported finding has a {pct}% AI match with a lost item report "
        f"reported by a community member."
    )
    action_finder = f"/matches"
    create_in_app_notification(found_item.user, 'MATCH_FOUND', title_finder, msg_finder, action_finder)
    send_email_notification(found_item.user.email, title_finder, msg_finder)


def notify_claim_submitted(claim_request):
    """
    Notify the finder that an ownership claim has been submitted for their found item.
    """
    found_item = claim_request.found_item
    finder = found_item.user
    title = f"New Ownership Claim on: {found_item.item_name}"
    msg = (
        f"User '{claim_request.claimant.username}' has submitted an ownership claim for '{found_item.item_name}'. "
        f"Please review the claim details and provide verification in your claims dashboard."
    )
    action = f"/claims"
    create_in_app_notification(finder, 'CLAIM_SUBMITTED', title, msg, action)
    send_email_notification(finder.email, title, msg)


def notify_claim_status_updated(claim_request):
    """
    Notify claimant regarding status decision on their claim.
    """
    claimant = claim_request.claimant
    item_name = claim_request.found_item.item_name
    status_label = claim_request.get_status_display()
    title = f"Claim Status Update: {item_name} - {status_label}"
    msg = (
        f"Your ownership claim on '{item_name}' is now marked as: {status_label}.\n"
        f"Finder/Admin note: {claim_request.finder_response or claim_request.admin_notes or 'No notes provided.'}"
    )
    action = f"/claims"
    create_in_app_notification(claimant, 'CLAIM_ACCEPTED' if claim_request.status == 'APPROVED' else 'CLAIM_REJECTED', title, msg, action)
    send_email_notification(claimant.email, title, msg)
