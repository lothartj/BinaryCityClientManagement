from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import os
import base64
from urllib.parse import quote
import uuid
from django.core.files.base import ContentFile
from django.conf import settings
from dotenv import load_dotenv
from .models import NotificationClient, Client, Contact
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
import logging
from asgiref.sync import async_to_sync
from django.core.asgi import get_asgi_application
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import threading
from django.utils import timezone
from threading import local
_thread_locals = local()

logger = logging.getLogger(__name__)

load_dotenv()

executor = ThreadPoolExecutor(max_workers=3)

def get_whatsapp_credentials():
    """Get WhatsApp API credentials from environment variables"""
    instance_id = os.getenv('ULTRAMSG_INSTANCE_ID')
    token = os.getenv('ULTRAMSG_TOKEN')
    base_url = os.getenv('ULTRAMSG_BASE_URL')
    if not all([instance_id, token, base_url]):
        logger.error("WhatsApp API credentials not found in environment variables!")
        raise Exception("Please set ULTRAMSG_INSTANCE_ID, ULTRAMSG_TOKEN, and ULTRAMSG_BASE_URL in your .env file")

    return instance_id, token, base_url

def send_whatsapp_message(phone, message):
    """Send WhatsApp message"""
    try:
        instance_id, token, base_url = get_whatsapp_credentials()
        api_url = f"{base_url}/{instance_id}"

        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        if not phone.startswith('264'):
            phone = '264' + phone
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        chat_url = f"{api_url}/messages/chat"
        text_payload = {
            "token": token,
            "to": phone,
            "body": message,
            "priority": 10
        }
        encoded_payload = "&".join([f"{key}={quote(str(value))}" for key, value in text_payload.items()])
        logger.info(f"Sending WhatsApp message to {phone}")
        logger.info(f"URL: {chat_url}")
        logger.info(f"Message: {message}")
        response = requests.post(chat_url, data=encoded_payload, headers=headers)
        logger.info(f"WhatsApp API Response: {response.json()}")
        return response.json()
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return None

def format_message_with_user_info(message, request=None):
    """Format message with user and timestamp information"""
    timestamp = timezone.now().strftime("%d-%m-%Y %H:%M:%S")
    user_info = f"by {request.user.username}" if request and request.user.is_authenticated else "by system"
    return f"{message}\n\nAction performed {user_info} at {timestamp}"

def notify_all_clients_background(message, request=None):
    """Background task to send notifications to all clients"""
    try:
        notification_clients = NotificationClient.objects.filter(is_active=True)
        
        if not notification_clients.exists():
            logger.warning("No active notification clients found!")
            return []
        formatted_message = format_message_with_user_info(message, request)
        logger.info(f"Found {notification_clients.count()} active notification clients")
        results = []
        for client in notification_clients:
            phone = client.get_formatted_phone()
            if phone  :
                logger.info(f"Sending message to {client.name} ({phone})")
                result = send_whatsapp_message(phone, formatted_message)
                logger.info(f"WhatsApp API response for {client.name}: {result}")
                results.append({
                    'client': client.name,
                    'phone': phone,
                    'result': result
                })
            else:
                logger.warning(f"Invalid phone number for client {client.name}")
        return results
    except Exception as e:
        logger.error(f"Error in background notification task: {str(e)}")
        return []

def notify_all_clients(message, request=None):
    """Asynchronously send notification to all active notification clients"""
    try:
        executor.submit(notify_all_clients_background, message, request)
        logger.info(f"Notification task submitted to background for message: {message}")
    except Exception as e:
        logger.error(f"Error submitting notification task: {str(e)}")

@receiver(post_save, sender=Client)
def client_changed(sender, instance, created, **kwargs):
    from django.contrib.auth.models import AnonymousUser
    from django.core.handlers.wsgi import WSGIRequest
    request = getattr(_thread_locals, 'request', None)
    user = getattr(request, 'user', None) if isinstance(request, WSGIRequest) else None
    username = user.username if user and not isinstance(user, AnonymousUser) else 'system'
    
    logger.info(f"Client signal triggered - Created: {created}, Instance: {instance.name}")
    if created:
        message = f"New client added: {instance.name} (Client Code: {instance.client_code})\nAction performed by {username}"
    else:
        message = f"Client updated: {instance.name} (Client Code: {instance.client_code})\nAction performed by {username}"
    
    notify_all_clients(message)

@receiver(post_save, sender=Contact)
def contact_changed(sender, instance, created, **kwargs):
    from django.contrib.auth.models import AnonymousUser
    from django.core.handlers.wsgi import WSGIRequest
    request = getattr(_thread_locals, 'request', None)
    user = getattr(request, 'user', None) if isinstance(request, WSGIRequest) else None
    username = user.username if user and not isinstance(user, AnonymousUser) else 'system'
    logger.info(f"Contact signal triggered - Created: {created}, Instance: {instance.get_full_name()}")
    if created:
        message = f"New contact added: {instance.get_full_name()}\nAction performed by {username}"
    else:
        message = f"Contact updated: {instance.get_full_name()}\nAction performed by {username}"
    notify_all_clients(message)

@receiver(m2m_changed, sender=Client.contacts.through)
def client_contacts_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    from django.contrib.auth.models import AnonymousUser
    from django.core.handlers.wsgi import WSGIRequest
    request = getattr(_thread_locals, 'request', None)
    user = getattr(request, 'user', None) if isinstance(request, WSGIRequest) else None
    username = user.username if user and not isinstance(user, AnonymousUser) else 'system'
    logger.info(f"M2M signal triggered - Action: {action}, Reverse: {reverse}")
    if action in ["post_add", "post_remove"]:
        if reverse:
            contact = instance
            clients = Client.objects.filter(pk__in=pk_set)
            client_names = ", ".join([client.name for client in clients])
            action_word = "added to" if action == "post_add" else "removed from"
            message = f"Contact {contact.get_full_name()} was {action_word} clients: {client_names}\nAction performed by {username}"
        else:
            client = instance
            contacts = Contact.objects.filter(pk__in=pk_set)
            contact_names = ", ".join([contact.get_full_name() for contact in contacts])
            action_word = "added to" if action == "post_add" else "removed from"
            message = f"Contacts {contact_names} were {action_word} client: {client.name}\nAction performed by {username}"
        
        logger.info(f"Sending M2M change message: {message}")
        notify_all_clients(message)
