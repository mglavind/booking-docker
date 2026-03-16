"""
Discord-notifikationer i realtid for TeknikBooking ændringer.

Når en TeknikBooking oprettes eller opdateres, sendes en notifikation til det
konfigurerede Discord webhook URL for teamet.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

# Kontroller om apprise er tilgængelig
try:
    import apprise
    from apprise import NotifyType
    APPRISE_AVAILABLE = True
except ImportError:
    APPRISE_AVAILABLE = False
    logger.warning('apprise bibliotek ikke installeret - Discord notifikationer deaktiveret')

from Teknik.models import TeknikBooking


@receiver(post_save, sender=TeknikBooking)
def notify_discord_on_teknikbooking_change(sender, instance, created, **kwargs):
    """
    Send en Discord notifikation når en TeknikBooking oprettes eller opdateres.
    
    Signal handler der:
    - Kontrollerer om apprise er tilgængelig
    - Verificerer at teamet har et discord_webhook_url konfigureret
    - Formaterer en rig Discord embed besked med bookingdetaljer
    - Sender via Discord webhook ved brug af apprise
    - Håndterer fejl elegant (påvirker ikke bookingoprettelse)
    """
    
    if not APPRISE_AVAILABLE:
        return
    
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
        booking_url = f"{settings.CSRF_TRUSTED_ORIGINS[0]}/teknik/Teknik/TeknikBooking/detail/{instance.id}/"
        
        # Byg kort, menneskeligt besked
        contact_name = instance.team_contact.get_full_name() if instance.team_contact else "Ikke angivet"
        item_name = instance.item.name if instance.item else "Ikke valgt"
        extra_info = ""
        if instance.assistance_needed:
            extra_info += "\n🆘 Assistance påkrævet"
        if instance.delivery_needed:
            extra_info += "\n🚚 Levering påkrævet"
        
        message = f"""
**{action}** {status_emoji} | **Teknik**

{item_name} for {instance.team.name}

📅 {instance.start_date.strftime('%d/%m')} - {instance.end_date.strftime('%d/%m')}
🕐 {instance.start_time.strftime('%H:%M')} - {instance.end_time.strftime('%H:%M')}
📦 Antal: {instance.quantity}
👤 Kontakt: {contact_name}{extra_info}

{instance.remarks if instance.remarks else ""}

[Se booking →]({booking_url})
""".strip()
        
        # Byg Discord notifikation
        apobj = apprise.Apprise()
        
        # Byg webhook URL med avatar
        favicon_url = f"{settings.CSRF_TRUSTED_ORIGINS[0]}/static/favicon.png"
        webhook_url = f"{instance.team.discord_webhook_url}?avatar_url={favicon_url}"
        apobj.add(webhook_url)
        
        # Send notifikation via Discord webhook
        success = apobj.notify(
            body=message,
            title=f"🔧 Teknik - {instance.team.name}",
            notify_type=NotifyType.INFO
        )
        
        if success:
            logger.info(f'Discord notifikation sendt for TeknikBooking {instance.id}')
        else:
            logger.warning(f'Fejl ved afsendelse af Discord notifikation for TeknikBooking {instance.id}')
    
    except Exception as e:
        logger.error(
            f'Fejl ved afsendelse af Discord notifikation for TeknikBooking {instance.id}: {str(e)}',
            exc_info=True
        )
