from django.http import HttpResponse
from django.utils import timezone
from .viewssendnoti import notify_all_clients
import logging

logger = logging.getLogger(__name__)

def track_app_access(request):
    """Track when anyone accesses the app"""
    try:
        timestamp = timezone.now().strftime("%d-%m-%Y %H:%M:%S")
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown Browser')
        message = (
            f"🔔 App Access Alert:\n"
            f"IP Address: {ip_address}\n"
            f"Browser: {user_agent}\n"
            f"Timestamp: {timestamp}"
        )
        logger.info(f"App accessed from IP: {ip_address} at {timestamp}")
        notify_all_clients(message, request)
        
    except Exception as e:
        logger.error(f"Error tracking app access: {str(e)}")
