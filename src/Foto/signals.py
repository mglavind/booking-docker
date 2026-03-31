"""
Discord-notifikationer i realtid for FotoBooking ændringer.

Når en FotoBooking oprettes eller opdateres, sendes en notifikation til det
konfigurerede Discord webhook URL for teamet via en thread.
"""

import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

from Foto.models import FotoBooking


@receiver(post_save, sender=FotoBooking)
def notify_discord_on_fotobooking_change(sender, instance, created, **kwargs):
    """
    Send en Discord notifikation til en thread når en FotoBooking oprettes eller opdateres.
    """
    
    if not instance.team or not instance.team.discord_webhook_url:
        return
    
    try:
        action = "🆕 Ny booking" if created else "✏️ Booking opdateret"
        booking_url = f"{settings.CSRF_TRUSTED_ORIGINS[0]}/foto/Foto/FotoBooking/detail/{instance.id}/"
        contact_name = instance.team_contact.get_full_name() if instance.team_contact else "Ikke angivet"
        item_name = instance.item.name if instance.item else "Ikke valgt"
        
        message_text = f"""**{action}** | **Foto**
{item_name} for {instance.team.name}
📅 {instance.start_date.strftime('%d/%m')} - 🕐 {instance.start_time.strftime('%H:%M')}
👤 Kontakt: {contact_name}
{instance.remarks if instance.remarks else ""}
[Se booking →]({booking_url})"""
        
        webhook_url = instance.team.discord_webhook_url
        
        payload = {
            "content": message_text,
            "username": "📷 Foto Notifikationer",
            "thread_name": "Booking opdateringer",
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:
            logger.info(f'Discord notifikation sendt for FotoBooking {instance.id}')
        else:
            logger.warning(f'Discord webhook fejl for FotoBooking {instance.id}: HTTP {response.status_code}')
    
    except Exception as e:
        logger.error(f'Fejl for FotoBooking {instance.id}: {str(e)}', exc_info=True)
