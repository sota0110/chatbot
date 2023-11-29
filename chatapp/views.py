from django.shortcuts import render
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .config.openai_key import free_secret_key

# def index(request):
#     client = OpenAI(api_key = free_secret_key)
#     i = 0
#     if request.method == "POST":
#         if "submit" in request.POST:
#             user_input = request.POST['input']
#             messages[i] = {"role": "user", "content": user_input}
#             i += 1
#             given_messages = list(messages.values())
#             completion = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=given_messages,
#             )
#             bot_response = completion.choices[0].message.content
#             messages[i] = {"role": "assistant", "content": bot_response}
#             i += 1
#             print(messages)
#             print(messages.popitem()[1]['content'])
#     return render(request, 'index.html', messages)


@csrf_exempt
def ask(request):
    client = OpenAI(api_key = free_secret_key)

    user_input = request.POST['message']
    user_message = {"role": "user", "content": user_input}
    messages = request.session.get('messages', [])
    messages.append(user_message)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    bot_response = response.choices[0].message.content
    bot_message = {"role": "assistant", "content": bot_response}
    messages.append(bot_message)
    request.session['messages'] = messages
    return JsonResponse({'message': bot_response})

def chat_view(request):
    return render(request, 'chat.html')