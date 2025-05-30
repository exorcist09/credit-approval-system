# 🪙 Credit Approval System

####  <b>Built with Django, Django REST Framework, Docker, PostgreSQL, Celery & Redis</b>

A backend system built using <b>Django, Django REST Framework, Celery, Redis, and PostgreSQL </b>that automates the ingestion of customer and loan data from Excel files, registers new customers, checks credit eligibility, and manages loans.

---

## 🚀 Tech Stack & Requirements

### 📦 Python Libraries (see `requirements.txt`)
| Library | Purpose |
|--------|---------|
| **Django** | Web framework to build and manage the server-side backend. |
| **djangorestframework** | Toolkit for providing RESTful API capabilities to Django. |
|**PostgreSQL** | 	Relational database for structured and transactional data |
| **psycopg2-binary** | PostgreSQL adapter to connect Django ORM with the PostgreSQL database. |
| **celery** | Handles asynchronous background task processing (used for Excel ingestion). |
| **redis** | In-memory broker and result backend for Celery task queuing. |
| **pandas** | Parses and processes structured Excel data. |
| **openpyxl** | Reads `.xlsx` files for loan and customer data ingestion. |
| **django-cors-headers** | Allows cross-origin requests from frontend clients. |

---

## 🗂️ Project Structure

```
credit-system/
│
├── core/                # Main Django project configs
│   ├── settings.py      # Includes DB, Redis, Celery, CORS, etc.
│   ├── urls.py          # Root URL mappings
│   ├── wsgi.py/asgi.py  # Web server entry points
│   └── celery.py        # Celery config
│
├── loan/                # Main application logic
│   ├── models.py        # Customer & Loan models
│   ├── serializers.py   # API serializers
│   ├── views.py         # View logic and endpoints
│   ├── tasks.py         # Background Excel ingestion tasks
│   ├── urls.py          # Endpoint routes
│
├── customer_data.xlsx   # Sample customer dataset
├── loan_data.xlsx       # Sample loan dataset
├── Dockerfile           # Django Docker setup
├── docker-compose.yml   # Services: Django, PostgreSQL, Redis
├── requirements.txt     # Python dependencies
└── manage.py            # Django entry point
```



---

## 🔧 Setup & Running the Project

### ✅ Requirements
- Docker
- Docker Compose

---

### 🛠️ Step-by-Step for Users

1. **Clone the repository**

```bash
git clone https://github.com/exorcist09/credit-approval-system
cd credit-approval-system
```

2. **Run Docker Compose**

```bash
sudo docker-compose up --build
```

This will:

* Build the Docker image for your Django app(credit-approval-system).
* Spin up services for Django, PostgreSQL, Redis.
* Start Celery for background task processing.

3. **Run database migrations**

```bash
sudo docker-compose exec web python manage.py migrate
```

4. **Open the app**


<b>Visit: [http://localhost:8000](http://localhost:8000)</b>


---

## 🔌 API Endpoints (`loan/urls.py`)

All endpoints are prefixed with <b>/api</b>.
</br>
Example: POST <b>/api/register</b> instead of just /register.


| Endpoint                    | Method | Description                                         |
| --------------------------- | ------ | --------------------------------------------------- |
| `/trigger-ingestion`        | POST   | Trigger Celery task to ingest data from Excel files |
| `/register`                 | POST   | Register a new customer                             |
| `/check-eligibility`        | POST   | Check if a customer is eligible for a loan          |
| `/create-loan`              | POST   | Create a new loan                                   |
| `/view-loan/<loan_id>`      | GET    | View details of a specific loan                     |
| `/view-loans/<customer_id>` | GET    | View all loans of a customer                        |

---




## ⚙️ Celery Setup

Celery is automatically started by Docker Compose and uses Redis for task queueing.

Configuration is loaded from:

```python
# core/settings.py
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
```



## 🔒 Security Settings

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOW_ALL_ORIGINS = True
```

---

## 🧪 Testing

You can run tests using:


```bash
# loan/tests.py
sudo docker-compose exec web python manage.py test
```

---

## 📦 Static Files

Collected to:

```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

Use `python manage.py collectstatic` 

---

## 🔃 Summary

* Django and DjangoRESTframework for the backend logic and REST APIs  
* PostgreSQL for relational data storage  
* Celery + Redis for background ingestion of Excel data  
* Docker for seamless containerization  
* Excel parsing via `pandas` and `openpyxl`
