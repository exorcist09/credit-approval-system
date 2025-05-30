# Credit Approval System – Django + Docker

This is a Dockerized backend for a Credit Approval System built with Django.

## 🚀 How to Run

### Requirements

- Docker
- Docker Compose

### Steps

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/credit-system-django.git
cd credit-system-django
Run the containers:

bash
Copy
Edit
sudo docker-compose up
Open the app in your browser:

arduino
Copy
Edit
http://localhost:8000
Django and Celery will automatically start, and the PostgreSQL and Redis services will be set up.

Run migrations (first time only):

bash
Copy
Edit
sudo docker-compose exec web python manage.py migrate



🔧 Step-by-Step for the user
1. Clone the repo
bash
Copy
Edit
git clone https://github.com/YOUR_USERNAME/credit-system-django.git
cd credit-system-django
2. Run Docker Compose
bash
Copy
Edit
sudo docker-compose up --build
This will:

Build the Docker image for your Django app.

Spin up all services: Django backend, PostgreSQL, Redis, etc.

Run everything as specified in your docker-compose.yml.

