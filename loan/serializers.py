from rest_framework import serializers
from .models import Customer,Loan
from datetime import datetime


# register customer 
class RegisterCustomerSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    age = serializers.IntegerField(required=False, allow_null=True)
    monthly_salary = serializers.IntegerField()
    phone_number = serializers.CharField()
    

class RegisteredCustomerResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = [
            "customer_id","name","age","monthly_salary","approved_limit","phone_number"
        ]
    def get_name(self,obj):
        return f"{obj.first_name} {obj.last_name}"



# check-eligibility
class CheckEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class CheckEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()
    
    
# create-loan
class CreateLoanRequestSerializer(serializers.Serializer):
    customer_id =serializers.IntegerField()
    loan_amount=serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null= True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.FloatField()
  
    
    
# view loan with loan id(loan details of a customer )
class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age']
    
class ViewLoanSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer
    class Meta :
        model = Loan
        fields=['loan_id', 'customer', 'loan_amount','interest_rate', 'monthly_installment', 'tenure']
   
   
        
# View Loans of The customer
class CustomerLoanSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()
    
    class Meta :
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']        
        
# emis left based on tenure and passed months from  start point to current date
        
# E = P x R x (1+r)^n/((1+r)^N – 1, where 

# E = Equated Monthly Instalment
# P = stands for principal amount
# R = denotes applicable rate of interest
# N = stands for the loan term or tenure


# TODO :- check this again
    def get_repayments_left(self,obj):
        now = datetime.now().date()
        months_passed = ((now.year - obj.start_date.year)*12)+(now.month - obj.start_date.month)
        repayments_left = obj.tenure - months_passed
        return max(repayments_left,0)
        