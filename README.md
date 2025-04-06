# Healthcare Appointment Scheduling System

![Healthcare System](https://img.shields.io/badge/healthcare-system-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)

A robust backend service for managing patient data and scheduling appointments with healthcare providers.

## Features

### Core Functionality
- **Patient Management**
  - Patient registration and profile management
  - Storage of basic information and contact details
  - Insurance information tracking
- **Doctor Management**
  - Doctor profiles with specializations
  - Availability schedule management
  - Time-off requests
- **Appointment Scheduling**
  - Book appointments between patients and doctors
  - Conflict detection to prevent double-booking
  - Appointment status tracking (Scheduled, Confirmed, Completed, etc.)

### Bonus Features
- Medical records system with access controls
- Prescription management
- Notification system

## Technology Stack

- **Backend**: Django 4.2
- **Database**: PostgreSQL (recommended)
- **Authentication**: Django's built-in authentication with custom user model
- **API**: Django REST Framework (optional)

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL (or SQLite for development)
- pip package manager

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/MuchokiDavid/hospital-appointment.git
   cd hospital-appointment
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure database settings in `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': 'appointment.db',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```
## Database Schema
The system includes a robust database schema which is also scalable.
Access the schema at [https://github.com/MuchokiDavid/hospital-appointment/blob/main/Appointment_API_schema_diagram.pdf](https://github.com/MuchokiDavid/hospital-appointment/blob/main/Appointment_API_schema_diagram.pdf)

## Admin Interface

The system includes a powerful admin interface with:
- Advanced search functionality
- Custom filters for all models
- Date-based hierarchies
- Raw ID fields for better performance

Access the admin panel at `http://localhost:8000/admin/`

## API Endpoints (Optional)

If you implement DRF, here are suggested endpoints:
-  `/api/v1/auth/register` - Doctor Register acccount
- `/api/v1/auth/register-patient/` - Patient CRUD operations
- `/api/v1/auth/doctor-profile/` - Doctor management
- `/api/v1/appointment/` - Appointment scheduling
- `/api/medical-record/` - Medical records access
- More endpoints the documentation


## Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure a production database
3. Set up a proper web server (Gunicorn recommended)
4. Configure static files collection

## API Documentation

We provide comprehensive interactive documentation for all API endpoints:

| Documentation Type | URL |
|--------------------|-----|
| **Swagger UI** (Interactive) | [https://hospital-appointment-tvid.onrender.com/swagger/](https://hospital-appointment-tvid.onrender.com/swagger/) |
| **ReDoc** (Alternative) | [https://hospital-appointment-tvid.onrender.com/documentation/]([https://hospital-appointment-tvid.onrender.com/documentation/) |

**Features:**
- Try-it-out functionality for testing endpoints
- Detailed request/response examples
- Authentication instructions
- Model schemas

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Project Maintainer - [David Muchoki](mailto:dmmuchoki7@gmail.com)

Project Link: [https://github.com/MuchokiDavid/hospital-appointment](https://github.com/MuchokiDavid/hospital-appointment)