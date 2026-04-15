"""
Discord-notifikationer i realtid for SjakBooking ændringer.

Når en SjakBooking oprettes eller opdateres, sendes en notifikation til det
konfigurerede Discord webhook URL for teamet via en thread.
"""

import logging
import json
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

from Sjak.models import SjakBooking


@receiver(post_save, sender=SjakBooking)
def notify_discord_on_sjakbooking_change(sender, instance, created, **kwargs):
    """
    Send en Discord notifikation til en thread når en SjakBooking oprettes eller opdateres.
    
    Signal handler der:
    - Verificerer at teamet har et discord_webhook_url konfigureret
    - Opretter eller finder threaden "Booking opdateringer"
    - Poster notifikationen til threaden
    - Håndterer fejl elegant (påvirker ikke bookingoprettelse)
    """
    
    # Afslut tidligt hvis teamet ikke har webhook URL konfigureret
    if not instance.team or not instance.team.discord_webhook_url:
        return
    
    try:
        # Bestem handling
        action = "🆕 Ny booking" if created else "✏️ Booking opdateret"
        status_emoji = {
            "Approved": "✅",
            "Pending": "⏳",
            "Rejected": "❌",
        }.get(instance.status, "📋")
        
        # Byg booking URL
        booking_url = f"{settings.CSRF_TRUSTED_ORIGINS[0]}/sjak/Sjak/SjakBooking/detail/{instance.id}/"
        
        # Byg kort, menneskeligt besked
        contact_name = instance.team_contact.get_full_name() if instance.team_contact else "Ikke angivet"
        assigned_name = instance.assigned_sjak.get_full_name() if instance.assigned_sjak else "Ikke tildelt"
        item_name = instance.item.name if instance.item else "Ikke valgt"
    
        message_text = f"""**{action}** {status_emoji} | **SJAK**
📦 {instance.quantity} {item_name} til {instance.team.name}
📅 {instance.start.strftime('%d/%m')}  🕐 {instance.start_time.strftime('%H:%M')}
{instance.remarks if instance.remarks else ""}
[Se booking →]({booking_url})"""
        
        # Send Discord webhook med thread support
        webhook_url = instance.team.discord_webhook_url
        
        payload = {
            "content": message_text,
            "username": "⚙️ Sjak Notifikationer",
            "thread_name": "Booking opdateringer",
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 204:
            logger.info(f'Discord notifikation sendt for SjakBooking {instance.id}')
        else:
            logger.warning(f'Discord webhook fejl for SjakBooking {instance.id}: HTTP {response.status_code} - {response.text[:200]}')
    
    except Exception as e:
        logger.error(
            f'Fejl ved afsendelse af Discord notifikation for SjakBooking {instance.id}: {str(e)}',
            exc_info=True
        )

