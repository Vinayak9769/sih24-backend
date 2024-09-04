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

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=config,
    system_instruction="You are a pet expert with years of experience in understanding different breeds and their characteristics. Based on the user's lifestyle, preferences, and specific needs, you will recommend the most suitable dog breeds. Consider factors like activity level, space requirements, temperament, grooming needs, and compatibility with children or other pets.When responding, follow this structure:Brief Analysis: Analyze the user's requirements and key factors to consider. Top Recommendations: Provide 2-3 specific dog breeds that fit the user's needs.Reasoning: Explain why these breeds are suitable based on their characteristics. Additional Tips: Offer any additional advice or considerations the user should keep in mind when choosing or caring for the recommended breeds."
)


def generate_dog_recommendation(request):
    user_input = request.GET.get('message', '')
    if not user_input:
        return JsonResponse({"error": "No input provided"}, status=400)
    chat_session = model.start_chat()
    response = chat_session.send_message(user_input)
    return JsonResponse({"response": response.text})


def chat_view(request):
    return render(request, 'chat.html')
