import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Client, Contact
import os
import requests

API_KEY = os.getenv('GROQ_API_KEY', '')
MODEL_NAME = os.getenv('GROQ_MODEL_NAME', 'llama3-70b-8192')
API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')

def get_analytics_data():
    """Gather analytics data for AI analysis"""
    clients = Client.objects.all()
    contacts = Contact.objects.all()
    analytics_data = {
        'total_clients': clients.count(),
        'total_contacts': contacts.count(),
        'client_details': [],
        'contact_details': []
    }
    for client in clients:
        analytics_data['client_details'].append({
            'name': client.name,
            'code': client.client_code,
            'contact_count': client.contacts.count(),
            'contacts': [
                {
                    'name': contact.get_full_name(),
                    'email': contact.email
                } for contact in client.contacts.all()
            ]
        })
    for contact in contacts:
        analytics_data['contact_details'].append({
            'name': contact.get_full_name(),
            'email': contact.email,
            'client_count': contact.clients.count(),
            'clients': [
                {
                    'name': client.name,
                    'code': client.client_code
                } for client in contact.clients.all()
            ]
        })
    return analytics_data

@csrf_exempt
def get_ai_analytics_insights(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            view_type = data.get('view_type', '')
            if not API_KEY:
                return JsonResponse({'error': 'API key not configured'}, status=500)
            analytics_data = get_analytics_data()
            if view_type == 'client':
                system_message = (
                    "You are an analytics expert analyzing client-contact relationships. "
                    "Focus on insights about how clients are connected to contacts. "
                    "Analyze patterns like which clients have the most/least contacts, "
                    "identify any gaps in client-contact relationships, and suggest "
                    "potential opportunities for better client management."
                )
            else:
                system_message = (
                    "You are an analytics expert analyzing contact-client relationships. "
                    "Focus on insights about how contacts are connected to clients. "
                    "Analyze patterns like which contacts work with multiple clients, "
                    "identify any contacts with no clients, and suggest potential "
                    "opportunities for better contact management."
                )
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            messages = [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": (
                        f"Please analyze this data and provide insights about {view_type} relationships:\n"
                        f"{json.dumps(analytics_data, indent=2)}\n\n"
                        "Focus on:\n"
                        "1. Key statistics and patterns\n"
                        "2. Notable relationships or gaps\n"
                        "3. Potential areas for improvement\n"
                        "4. Actionable recommendations\n"
                        "Format the response in clear sections with bullet points where appropriate."
                    )
                }
            ]
            payload = {
                "model": MODEL_NAME,
                "messages": messages
            }
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            ai_response = response.json()['choices'][0]['message']['content']
            return JsonResponse({'response': ai_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
