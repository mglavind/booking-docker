"""
Context Processors for the core app.

Provides access to feature toggles in templates via the config context variable.
"""
from constance import config


def app_feature_toggles(request):
    """
    Make feature toggle configuration available in all templates.
    
    Usage in templates:
    {% if config.APP_ENABLE_SOS %}
        <!-- SOS app content -->
    {% endif %}
    """
    return {
        'config': config,
    }
