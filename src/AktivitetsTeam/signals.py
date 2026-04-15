"""
Discord-notifikationer i realtid for AktivitetsTeamBooking ændringer.

Når en AktivitetsTeamBooking oprettes eller opdateres, sendes en notifikation til det
konfigurerede Discord webhook URL for teamet via en thread.
"""

import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

from AktivitetsTeam.models import AktivitetsTeamBooking


@receiver(post_save, sender=AktivitetsTeamBooking)
def notify_discord_on_aktivitetsteambooking_change(sender, instance, created, **kwargs):
    """
    Send en Discord notifikation til en thread når en AktivitetsTeamBooking oprettes eller opdateres.
    
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
        booking_url = f"{settings.CSRF_TRUSTED_ORIGINS[0]}/aktivitetsteam/AktivitetsTeam/AktivitetsTeamBooking/detail/{instance.id}/"
        
        # Byg kort, menneskeligt besked
        contact_name = instance.team_contact.get_full_name() if instance.team_contact else "Ikke angivet"
        item_name = instance.item.name if instance.item else "Ikke valgt"
        assigned_list = ", ".join([v.get_full_name() for v in instance.assigned_aktivitetsteam.all()]) if instance.assigned_aktivitetsteam.exists() else "Ikke tildelt"
        
        message_text = f"""**{action}** {status_emoji} | **AktivitetsTeam**
{item_name} til {instance.team.name}
📅 {instance.start_date.strftime('%d/%m')} - 🕐 {instance.start_time.strftime('%H:%M')}
👤 Team Kontakt: {contact_name} 🔧 Tildelt AT: {assigned_list}
{instance.remarks if instance.remarks else ""}
[Se booking →]({booking_url})"""
        
        # Send Discord webhook med thread support
        webhook_url = instance.team.discord_webhook_url
        
        payload = {
            "content": message_text,
            "username": "👥 AktivitetsTeam Notifikationer",
            "thread_name": "Booking opdateringer",
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 204:
            logger.info(f'Discord notifikation sendt for AktivitetsTeamBooking {instance.id}')
        else:
            logger.warning(f'Discord webhook fejl for AktivitetsTeamBooking {instance.id}: HTTP {response.status_code} - {response.text[:200]}')
    
    except Exception as e:
        logger.error(
            f'Fejl ved afsendelse af Discord notifikation for AktivitetsTeamBooking {instance.id}: {str(e)}',
            exc_info=True
        )


