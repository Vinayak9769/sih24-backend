# Raahi - A Smart India Hackathon 2024 Project

## Overview

**Raahi** is a web-based platform developed for the Smart India Hackathon 2024. The platform aims to simplify scheduling, mentoring, and collaboration by providing a seamless user experience for mentors and mentees. The core features include:

- Real-time communication using WebSockets.
- Easy scheduling of mentoring sessions using a calendar system.
- A chatbot feature for instant assistance.
- REST API integration for efficient data management.
  
This project was built using the Django framework for the backend and Django Channels for real-time functionality.

## Key Features

- **Mentoring System**: Users can schedule appointments with mentors and manage availability through a user-friendly calendar interface.
- **Chatbot**: An AI-powered chatbot helps users navigate through the platform and answer common questions.
- **Real-time Communication**: Enables real-time communication between users using Django Channels and WebSockets.
- **API Documentation**: Swagger API is integrated for documentation, making it easier to test the APIs and explore the platform's functionality.

## Tech Stack

- **Backend**: Django, Django Channels, Daphne, REST Framework
- **Database**: SQLite (default, can be switched to PostgreSQL)
- **Frontend**: React.js
- **Authentication**: JWT-based authentication using `rest_framework_simplejwt`.
- **Real-time communication**: WebSockets with Django Channels

## Installation and Setup

### Prerequisites

- Python 3.9+
- Django 5.1+
- Node.js (for frontend)

### Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/vinayak9769/sih24-backend.git
   cd raahi
    ```
2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Create a virtual environment and activate it:
   
   ```bash
   python -m venv env
   source env/bin/activate # On Windows use: venv\Scripts\activate
   ```
4. Create a `.env` file in the root directory and add the following environment variables:

   ```bash
   SECRET_KEY='your-secret-key'
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   EMAIL_HOST=smtp.example.com
   EMAIL_HOST_USER=you@example.com
   EMAIL_HOST_PASSWORD=supersecretpassword
   EMAIL_PORT=587
   ```
5. Run the Django migrations:

   ```bash
   python manage.py migrate
   ```
6. Run the server:

   ```bash
   python manage.py runserver
   ```
7. Access the application by navigating to http://127.0.0.1:8000/ in your browser.

## Running the Application with Daphne

To run the application using Daphne for WebSocket support, use the following command:

```bash
daphne -b 0.0.0.0 -p 8000 sih.asgi:application
```

## API Documentation

The API documentation can be accessed at https://sudormrf.pythonanywhere.com/redoc/

## Hosting with Procfile

Raahi includes a `Procfile` for easy hosting on platforms such as **Heroku** or **Railway**. The `Procfile` defines how the app is executed in a production environment. Example contents:

```Procfile
web: gunicorn sih.wsgi
```

## Contributors
[Vinayak9769](https://github.com/Vinayak9769)

[V3dang](https://github.com/V3dang)



Feel free to reach out if you have any questions or feedback!

