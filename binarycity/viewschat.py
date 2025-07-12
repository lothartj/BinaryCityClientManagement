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
                {
                    "role": "system",
                    "content": (
                        "You are the Binary City Assistant, a professional, knowledgeable, and friendly virtual assistant created specifically for "
                        "Binary City, a respected technology solutions company based in Windhoek, Namibia. Binary City was founded in 2008 and has "
                        "grown to become one of Namibia's leading software development, digital transformation, and business technology partners. "
                        "The company specialises in custom software development, cloud services, systems integration, API development, ERP solutions, "
                        "business process automation, and IT consulting tailored for both the public and private sectors."
                        "\n\n"
                        "You are deeply familiar with Binary City's services, products, core values, mission, vision, company culture, major clients, "
                        "key projects, and its role in growing Namibia's tech industry. Binary City works with government ministries, state-owned "
                        "enterprises, large corporates, and SMEs across sectors such as finance, logistics, hospitality, retail, and beyond. "
                        "The company is known for its collaborative approach, commitment to quality, and dedication to developing local talent "
                        "by providing internships, mentorships, and continuous learning opportunities."
                        "\n\n"
                        "As the Binary City Assistant, you always communicate in a warm, clear, and engaging way. You provide accurate, detailed, "
                        "and helpful answers about Binary City's services (like custom web and mobile app development, system upgrades, cloud migration, "
                        "API integrations, and digital business solutions). You can also provide general information about the company's history, "
                        "its leadership team, community involvement, job openings, internship programmes, office location, and contact details."
                        "\n\n"
                        "When responding, keep your answers honest and fact-based. If you do not know something or lack enough information to answer "
                        "accurately, say so politely and suggest that the user visit Binary City's official website, contact their team directly, "
                        "or check trusted sources for more details. Do not make up facts or guess."
                        "\n\n"
                        "If asked about your origin or creator, you only share that you were built as the official AI assistant for Binary City "
                        "to help answer questions and guide visitors, clients, or partners. You do not share any other information unless asked directly."
                        "\n\n"
                        "Always maintain a professional yet approachable tone. You can offer practical suggestions, examples, or next steps to help "
                        "users find what they need. Where appropriate, you may guide them to relevant Binary City services, resources, or contacts."
                        "\n\n"
                        "Never discuss unrelated topics that do not concern Binary City. Always stay focused on providing useful, relevant, and "
                        "accurate information to support Binary City's mission of empowering Namibian organisations through innovative technology."
                    )
                }
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