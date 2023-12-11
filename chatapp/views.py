from django.shortcuts import render
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .config.openai_key import free_secret_key
from .utils import LangChain

@csrf_exempt
def ask(request):
    client = OpenAI(api_key = free_secret_key)
    sql_judge_prompt = "If you are asked about jobs, please output 1. If you are asked about other things, please output 0. Don't output anything else."
    prompt = [{"role": "system", "content": sql_judge_prompt}]
    user_input = request.POST['message']
    prompt.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
    )
    sql_judge = response.choices[0].message.content
    print(f'{sql_judge=}')
    
    if sql_judge == '1':
        lang = LangChain()
        bot_response = lang.search_db(user_input)
    
    else:
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