from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterCustomerSerializer, RegisteredCustomerResponseSerializer, CheckEligibilityRequestSerializer,CreateLoanRequestSerializer,CreateLoanResponseSerializer,CustomerLoanSerializer
from .models import Customer, Loan
from datetime import datetime,timedelta


# Register Controller
class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            monthly_salary = data.get('monthly_salary')
            if monthly_salary is None:
                return Response(
                    {"error": "monthly_salary is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            approved_limit = round(36 * monthly_salary, -5)  # nearest lakh

            customer = Customer.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                age=data['age'],
                monthly_salary=monthly_salary,
                approved_limit=approved_limit,
                phone_number=data['phone_number']
            )

            response_data = RegisteredCustomerResponseSerializer(customer).data
            return Response({
                'message': 'Customer Registered',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def calculate_emi(principal, rate, tenure_months):
    monthly_rate = rate / (12 * 100)
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    return round(emi, 2)


# Check Eligiblity Controller
class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = CheckEligibilityRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            customer_id = data["customer_id"]
            loan_amount = data["loan_amount"]
            interest_rate = data["interest_rate"]
            tenure = data["tenure"]

            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            all_loans = Loan.objects.filter(customer=customer)
            now = datetime.now().date()

            past_loans_paid_on_time = sum([l.emis_paid_on_time for l in all_loans])
            total_loans_taken = all_loans.count()
            loans_this_year = all_loans.filter(start_date__year=now.year).count()
            total_loan_volume = sum([l.loan_amount for l in all_loans])
            current_debt = sum([l.loan_amount for l in all_loans if l.end_date >= now or l.end_date is None])

            credit_score = 100
            credit_score -= (total_loans_taken * 2)
            credit_score += past_loans_paid_on_time * 1
            credit_score += loans_this_year * 2
            credit_score += int(total_loan_volume / 100000)

            if current_debt > customer.approved_limit:
                credit_score = 0

            emi = calculate_emi(loan_amount, interest_rate, tenure)
            total_current_emi = sum([l.monthly_installment for l in all_loans if l.end_date >= now or l.end_date is None])

            approval = False
            corrected_interest_rate = interest_rate  # default

            if total_current_emi + emi > 0.5 * customer.monthly_salary:
                approval = False
                corrected_interest_rate = 0  # indicate rejection
            else:
                if credit_score > 50:
                    approval = True
                elif 30 < credit_score <= 50:
                    approval = interest_rate > 12
                    if not approval:
                        corrected_interest_rate = 12
                elif 10 < credit_score <= 30:
                    approval = interest_rate > 16
                    if not approval:
                        corrected_interest_rate = 16
                else:
                    approval = False
                    corrected_interest_rate = 0

            response = {
                "customer_id": customer_id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": corrected_interest_rate,
                "tenure": tenure,
                "monthly_installment": emi if approval else 0
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Create-Loan controller
class CreateLoanView(APIView):
    def post(self, request):
        serializer = CreateLoanRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            customer_id = data["customer_id"]
            loan_amount = data["loan_amount"]
            interest_rate = data["interest_rate"]
            tenure = data["tenure"]

            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=404)

            # Fetch all current loans of customer
            all_loans = Loan.objects.filter(customer=customer)
            now = datetime.now().date()
            current_loans = all_loans.filter(end_date__gte=now)

            past_loans_paid_on_time = sum([l.emis_paid_on_time for l in all_loans])
            total_loans_taken = all_loans.count()
            loans_this_year = all_loans.filter(start_date__year=now.year).count()
            total_loan_volume = sum([l.loan_amount for l in all_loans])
            current_debt = sum([l.loan_amount for l in current_loans])

            credit_score = 100
            if total_loans_taken > 0:
                credit_score -= (total_loans_taken * 2)
            if past_loans_paid_on_time > 0:
                credit_score += past_loans_paid_on_time
            if loans_this_year > 0:
                credit_score += loans_this_year * 2
            if total_loan_volume > 0:
                credit_score += int(total_loan_volume / 100000)

            if current_debt > customer.approved_limit:
                credit_score = 0

            # Calculate EMI and check eligibility
            emi = calculate_emi(loan_amount, interest_rate, tenure)
            total_emi = sum([l.monthly_installment for l in current_loans])
            if total_emi + emi > 0.5 * customer.monthly_salary:
                approved = False
            elif credit_score > 50:
                approved = True
            elif 30 < credit_score <= 50:
                approved = interest_rate >= 12
            elif 10 < credit_score <= 30:
                approved = interest_rate >= 16
            else:
                approved = False

            if not approved:
                return Response({
                    "loan_id": None,
                    "customer_id": customer_id,
                    "loan_approved": False,
                    "message": "Loan not approved due to eligibility criteria",
                    "monthly_installment": emi
                }, status=200)

            # Create loan
            new_loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                tenure=tenure,
                monthly_installment=emi,
                emis_paid_on_time=0,
                start_date=now,
                end_date=now + timedelta(days=tenure*30)
            )

            return Response({
                "loan_id": new_loan.loan_id,
                "customer_id": customer_id,
                "loan_approved": True,
                "message": "Loan approved successfully",
                "monthly_installment": emi
            }, status=201)

        return Response(serializer.errors, status=400)



# View-loan Details Controller
class ViewLoanDetails(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=404)

        data = {
            "loan_id": loan.loan_id,
            "customer": {
                "customer_id": loan.customer.customer_id,
                "first_name": loan.customer.first_name,
                "last_name": loan.customer.last_name,
                "phone_number": loan.customer.phone_number,
                "age": loan.customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure
        }
        return Response(data, status=200)

    
# View-Loans of Customer Controller
class ViewLoansByCustomer(APIView):
    def get(self,request,customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error":"Customer not found"}, status = 404)
        
        now = datetime.now().date()
        # orm mapping
        current_loans = Loan.objects.filter(customer = customer , end_date__gte = now)
        
        serializer = CustomerLoanSerializer(current_loans,many=True)
        return Response(serializer.data, status = 200)