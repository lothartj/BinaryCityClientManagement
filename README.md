# Binary City Client Management System

A Django-based web application for managing clients and contacts, with features for linking them together and automatic client code generation.

## Live Demo
<a href="https://binarycityclientmanagement.onrender.com" target="_blank" rel="noopener noreferrer">
  <img src="https://img.shields.io/badge/Live_Demo-Visit_App-8A2BE2?style=for-the-badge&logo=render&logoColor=white" alt="Live Demo" />
</a>

## Features

- **Client Management**
  - Create and edit clients
  - Auto-generated unique client codes (e.g., FNB001, PRO001)
  - Link multiple contacts to clients
  - View number of linked contacts per client

- **Contact Management**
  - Create and edit contacts
  - Email validation and uniqueness check
  - Link multiple clients to contacts
  - View number of linked clients per contact

## Technology Stack

- Python 3.8+
- Django 4.2.19
- Bootstrap 5.3
- SQLite (default database)
- Docker support

## Local Setup

### Without Docker

1. Clone the repository:
```bash
git clone https://github.com/lothartj/BinaryCityClientManagement.git
cd BinaryCity
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

### With Docker

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at http://localhost:8000

## Project Structure

```
BinaryCity/
├── project/
│   ├── binarycity/
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   └── binarycity/
│   │   │       ├── client_list.html
│   │   │       ├── client_form.html
│   │   │       ├── contact_list.html
│   │   │       └── contact_form.html
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   └── project/
│       ├── settings.py
│       └── urls.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Client Code Generation

The system automatically generates unique client codes following these rules:
- Takes first 3 letters of the client name (e.g., "First National Bank" → "FNB")
- For names shorter than 3 letters, pads with sequential letters (e.g., "IT" → "ITA")
- Adds a 3-digit sequential number (e.g., "001", "002")
- Ensures uniqueness across all clients

## API Endpoints

- `/` - Home page
- `/clients/` - Client list
- `/clients/create/` - Create new client
- `/clients/<id>/edit/` - Edit client
- `/contacts/` - Contact list
- `/contacts/create/` - Create new contact
- `/contacts/<id>/edit/` - Edit contact

## Development Guidelines

- Follow PEP 8 style guide for Python code
- Use Django's class-based views where possible
- Implement proper form validation
- Maintain clean separation of concerns (MVC pattern)
- Write descriptive commit messages

## Security Features

- CSRF protection enabled
- Form validation on both client and server side
- Email uniqueness validation
- Proper error handling and user feedback