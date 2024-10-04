from channels.db import database_sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import google.generativeai as genai
import os
from dotenv import load_dotenv
from core.models import Mentor

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
    system_instruction="""
    DO NOT ASK FURTHER QUESTIONS
    Please provide the following information clearly and in a readable format:

    - Experience: Specify the number of years of experience (e.g., "Experience: 5 years").
    - Expertise: Indicate the specific field or specialization (e.g., "Expertise: Data Science").

    Use bullet points or a list format for clarity. Ensure that the labels ('Experience' and 'Expertise') are clearly distinguishable from the values.

    Example response:
    - Experience: 5 years
    - Expertise: Data Science

    The response should be formatted in a human-readable way and avoid JSON or other machine-readable formats.
    """
)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        user_input = text_data_json.get('message')

        if user_input:
            chat_session = model.start_chat()
            response = chat_session.send_message(user_input)
            response_text = response.text
            criteria = self.parse_criteria(response_text)
            print(response_text)
            print(criteria)
            mentors = await database_sync_to_async(self.filter_mentors)(**criteria)
            formatted_mentors = self.format_mentors(mentors)

            await self.send(text_data=json.dumps({
                'formatted_response': response_text,
                'mentors': formatted_mentors
            }))

    def parse_criteria(self, response_text):
        criteria = {
            'experience': None,
            'expertise': None
        }
        lines = response_text.split('\n')
        for line in lines:
            if 'experience' in line.lower():
                experience_text = line.split(':')[1].strip()
                criteria['experience'] = int(''.join(filter(str.isdigit, experience_text)))
            elif 'expertise' in line.lower():
                criteria['expertise'] = line.split(':')[1].strip()


        return criteria

    def format_mentors(self, mentors):
        if not mentors:
            return "No mentors found."

        mentor_lines = []
        for mentor in mentors:
            mentor_lines.append(f"Name: {mentor['name']}")
            mentor_lines.append(f"Bio: {mentor['bio']}")
            mentor_lines.append(f"Profile Picture: {mentor['profile_picture']}")
            mentor_lines.append(f"Phone Number: {mentor['phone_number']}")
            mentor_lines.append(f"Experience: {mentor['experience']} years")
            mentor_lines.append(f"Expertise: {mentor['expertise']}")
            mentor_lines.append(f"Book now: https://localhost::5173/mentors/book/{mentor['id']}")
            mentor_lines.append("\n\n")  # Separator for readability

        return "\n".join(mentor_lines)

    def filter_mentors(self, experience=None, expertise=None):
        filters = {}
        if experience is not None:
            filters['experience__gte'] = experience
        if expertise:
            filters['expertise__icontains'] = expertise

        # Query the Mentor model using Django ORM
        mentors = Mentor.objects.filter(**filters).values('id', 'name', 'bio', 'profile_picture', 'phone_number',
                                                          'experience', 'expertise')
        return list(mentors)
