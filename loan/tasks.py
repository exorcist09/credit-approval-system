# loan/tasks.py
import pandas as pd
from datetime import datetime
from celery import shared_task
from .models import Customer, Loan

@shared_task
def ingest_excel_data():
    customer_df = pd.read_excel('/app/customer_data.xlsx')
    loan_df = pd.read_excel('/app/loan_data.xlsx')

    for _, row in customer_df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['customer_id'],
            defaults={
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "phone_number": str(row['phone_number']),
                "monthly_salary": row['monthly_salary'],
                "approved_limit": row['approved_limit'],
                "current_debt": row['current_debt']
            }
        )

    for _, row in loan_df.iterrows():
        customer = Customer.objects.get(customer_id=row['customer_id'])
        Loan.objects.update_or_create(
            loan_id=row['loan_id'],
            defaults={
                "customer": customer,
                "loan_amount": row['loan_amount'],
                "tenure": row['tenure'],
                "interest_rate": row['interest_rate'],
                "monthly_repayment": row['monthly_repayment'],
                "emis_paid_on_time": row['EMIs paid on time'],
                "start_date": datetime.strptime(row['start_date'], "%Y-%m-%d"),
                "end_date": datetime.strptime(row['end_date'], "%Y-%m-%d"),
                "loan_approved": True
            }
        )
