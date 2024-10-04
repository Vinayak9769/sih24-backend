from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('API_KEY'))

config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain"
}


def chat_view(request):
    return render(request, 'chat.html')
