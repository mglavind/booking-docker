"""
Discord-notifikationer i realtid for TeknikBooking ændringer.

Når en TeknikBooking oprettes eller opdateres, sendes en notifikation til det
konfigurerede Discord webhook URL for teamet via en thread.
"""

import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

from Teknik.models import TeknikBooking


@receiver(post_save, sender=TeknikBooking)
def notify_discord_on_teknikbooking_change(sender, instance, created, **kwargs):
    """
    Send en Discord notifikation til en thread når en TeknikBooking oprettes eller opdateres.
    """
    
    if not instance.team or not instance.team.discord_webhook_url:
        return
    
    try:
        action = "🆕 Ny booking" if created else "✏️ Booking opdateret"
        status_emoji = {"Approved": "✅", "Pending": "⏳", "Rejected": "❌"}.get(instance.status, "📋")
        booking_url = f"{settings.CSRF_TRUSTED_ORIGINS[0]}/teknik/Teknik/TeknikBooking/detail/{instance.id}/"
        contact_name = instance.team_contact.get_full_name() if instance.team_contact else "Ikke angivet"
        item_name = instance.item.name if instance.item else "Ikke valgt"
        
        extra_info = ""
        if instance.assistance_needed:
            extra_info += "\n🆘 Assistance påkrævet"
        if instance.delivery_needed:
            extra_info += "\n🚚 Levering påkrævet"
        
        message_text = f"""**{action}** {status_emoji} | **Teknik**
📦 Antal: {instance.quantity} stk {item_name} til {instance.team.name}
📅 {instance.start_date.strftime('%d/%m')} - 🕐 {instance.start_time.strftime('%H:%M')}
👤 TeamKontakt: {contact_name}{extra_info}
{instance.remarks if instance.remarks else ""}
[Se booking →]({booking_url})"""
        
        webhook_url = instance.team.discord_webhook_url
        
        payload = {"content": message_text, "username": "🔧 Teknik Notifikationer", "thread_name": "Booking opdateringer"}
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:
            logger.info(f'Discord notifikation sendt for TeknikBooking {instance.id}')
        else:
            logger.warning(f'Discord webhook fejl for TeknikBooking {instance.id}: HTTP {response.status_code}')
    
    except Exception as e:
        logger.error(f'Fejl for TeknikBooking {instance.id}: {str(e)}', exc_info=True)
