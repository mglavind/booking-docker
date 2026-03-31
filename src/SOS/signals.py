"""
Discord-notifikationer i realtid for SOSBooking ændringer.

Når en SOSBooking oprettes eller opdateres, sendes en notifikation til det
konfigurerede Discord webhook URL for teamet via en thread.
"""

import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

from SOS.models import SOSBooking


@receiver(post_save, sender=SOSBooking)
def notify_discord_on_sosbooking_change(sender, instance, created, **kwargs):
    """
    Send en Discord notifikation til en thread når en SOSBooking oprettes eller opdateres.
    """
    
    if not instance.team or not instance.team.discord_webhook_url:
        return
    
    try:
        action = "🆕 Ny booking" if created else "✏️ Booking opdateret"
        status_emoji = {"Approved": "✅", "Pending": "⏳", "Rejected": "❌"}.get(instance.status, "📋")
        booking_url = f"{settings.CSRF_TRUSTED_ORIGINS[0]}/sos/SOS/SOSBooking/detail/{instance.id}/"
        contact_name = instance.team_contact.get_full_name() if instance.team_contact else "Ikke angivet"
        item_name = instance.item.name if instance.item else "Ikke valgt"
        
        flags = []
        if instance.assistance_needed:
            flags.append("🆘 Assistance nødvendig")
        if instance.delivery_needed:
            flags.append("🚚 Levering nødvendig")
        flags_text = "\n" + "\n".join(flags) if flags else ""
        
        message_text = f"""**{action}** {status_emoji} | **SOS**
📦 {instance.quantity} stk {item_name} til {instance.team.name}
📅 {instance.start_date.strftime('%d/%m')} - 🕐 {instance.start_time.strftime('%H:%M')}
👤 Kontakt: {contact_name}{flags_text}
{instance.remarks if instance.remarks else ""}
[Se booking →]({booking_url})"""
        
        webhook_url = instance.team.discord_webhook_url
        
        payload = {"content": message_text, "username": "🆘 SOS Notifikationer", "thread_name": "Booking opdateringer"}
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:
            logger.info(f'Discord notifikation sendt for SOSBooking {instance.id}')
        else:
            logger.warning(f'Discord webhook fejl for SOSBooking {instance.id}: HTTP {response.status_code}')
    
    except Exception as e:
        logger.error(f'Fejl for SOSBooking {instance.id}: {str(e)}', exc_info=True)
