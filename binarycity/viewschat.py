import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.core.cache import cache
from django.conf import settings

API_KEY = os.getenv('GROQ_API_KEY', '')
MODEL_NAME = os.getenv('GROQ_MODEL_NAME', 'llama3-70b-8192')
API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')

def chat(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    conversation_history = cache.get(f'conversation_history_{session_id}', [])

    context = {
        'conversation_history': conversation_history,
        'session_id': session_id,
    }
    return render(request, 'chat.html', context)

@csrf_exempt
def get_ai_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            session_id = data.get('session_id', '')

            if not API_KEY:
                return JsonResponse({'error': 'API key not configured'}, status=500)

            conversation_history = cache.get(f'conversation_history_{session_id}', [])

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            messages = [
                {"role": "system", "content": "You are a helpful assistant named Impala and you were created by Lothar Tjipueja a stand alone developer from somewhere on earth and thats all you know about him but dont mention it unless you are asked. Provide informative and engaging responses based on your training data."}
            ] + conversation_history + [{"role": "user", "content": user_message}]

            payload = {
                "model": MODEL_NAME,
                "messages": messages
            }

            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()

            ai_response = response.json()['choices'][0]['message']['content']

            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": ai_response})

            cache.set(f'conversation_history_{session_id}', conversation_history, timeout=None)

            return JsonResponse({'response': ai_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def clear_conversation(request):
    if request.method == 'POST':
        session_id = request.session.session_key
        cache.delete(f'conversation_history_{session_id}')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)