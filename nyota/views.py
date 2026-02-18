from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import PayheroService
from .models import LoanApplication, Transaction
from django.shortcuts import render, redirect, get_object_or_404
import json
import uuid
from django.db import transaction as db_transaction

def landing(request):
    limits = [
        {'amount': '5,000', 'charge': '100'},
        {'amount': '10,000', 'charge': '250'},
        {'amount': '15,000', 'charge': '500'},
        {'amount': '25,000', 'charge': '1,000'},
        {'amount': '35,000', 'charge': '1,500'},
        {'amount': '45,000', 'charge': '2,500'},
        {'amount': '55,000', 'charge': '3,500'},
        {'amount': '65,000', 'charge': '4,500'},
        {'amount': '75,000', 'charge': '5,500'}
    ]
    return render(request, 'nyota/landing.html', {'limits': limits})

@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            fee_amount = data.get('fee_amount') or data.get('amount')
            loan_amount = data.get('loan_amount', '0')
            full_name = data.get('full_name', 'User')
            county = data.get('county', 'Nairobi')
            reason = data.get('reason', 'General')
            
            # Remove commas from amount strings
            fee_amount = float(str(fee_amount).replace(',', ''))
            loan_amount = float(str(loan_amount).replace(',', ''))
            
            reference = str(uuid.uuid4())[:8].upper()
            description = f"Nyota Fund Fee - {reference}"
            
            with db_transaction.atomic():
                # Create Loan Application record
                application = LoanApplication.objects.create(
                    full_name=full_name,
                    phone_number=phone_number,
                    county=county,
                    reason=reason,
                    amount=loan_amount,
                    fee=fee_amount,
                    status='PENDING'
                )
                
                # Create Transaction record
                payment_tx = Transaction.objects.create(
                    application=application,
                    reference=reference,
                    amount=fee_amount,
                    phone_number=phone_number,
                    status='PENDING'
                )
            
            payhero = PayheroService()
            result = payhero.initiate_stk_push(
                phone_number=phone_number,
                amount=fee_amount,
                reference=reference,
                description=description
            )
            
            if result.get('success'):
                # Store reference in session for tracking on status page
                request.session['current_tx_ref'] = reference
                # Update checkout request ID if returned
                data_resp = result.get('data', {})
                payment_tx.checkout_request_id = data_resp.get('CheckoutRequestID', '')
                payment_tx.save()
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def dashboard(request):
    """User dashboard showing loan status and data."""
    # In a real app, this would be filtered by the logged-in user
    # For now, we'll show the most recent applications as an example
    applications = LoanApplication.objects.all().order_by('-created_at')[:5]
    return render(request, 'nyota/dashboard.html', {'applications': applications})

def offer_selection(request):
    """Enhanced offer selection page with dynamic slider logic."""
    limits = [
        {'amount': '5,000', 'charge': '100'},
        {'amount': '10,000', 'charge': '250'},
        {'amount': '15,000', 'charge': '500'},
        {'amount': '25,000', 'charge': '1,000'},
        {'amount': '35,000', 'charge': '1,500'},
        {'amount': '45,000', 'charge': '2,500'},
        {'amount': '55,000', 'charge': '3,500'},
        {'amount': '65,000', 'charge': '4,500'},
        {'amount': '75,000', 'charge': '5,500'}
    ]
    return render(request, 'nyota/offer_selection.html', {'limits': limits})

def payment_status(request):
    """Payment status page with auto-refresh/polling logic."""
    reference = request.GET.get('reference') or request.session.get('current_tx_ref')
    if not reference:
        return redirect('landing')
        
    transaction = get_object_or_404(Transaction, reference=reference)
    return render(request, 'nyota/payment_status.html', {'transaction': transaction})

def check_payment_status_api(request, reference):
    """API endpoint for polling payment status."""
    transaction = get_object_or_404(Transaction, reference=reference)
    return JsonResponse({
        'status': transaction.status,
        'app_status': transaction.application.status
    })

@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa payment callback from Payhero.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger_data = json.dumps(data, indent=2)
            print(f"Callback received: {logger_data}")
            
            # Get external reference from Payhero response
            # Note: Payhero structure usually has external_reference at the top level
            reference = data.get('external_reference')
            status_code = data.get('status_code') # 200 for success
            
            if reference:
                try:
                    with db_transaction.atomic():
                        payment_tx = Transaction.objects.get(reference=reference)
                        payment_tx.response_data = data
                        
                        if str(status_code) == "200":
                            payment_tx.status = 'SUCCESS'
                            # Update application as well
                            app = payment_tx.application
                            app.status = 'PROCESSING' # Moves to processing after payment
                            app.save()
                        else:
                            payment_tx.status = 'FAILED'
                        
                        payment_tx.save()
                except Transaction.DoesNotExist:
                    print(f"Transaction with reference {reference} not found.")
            
            return JsonResponse({'status': 'Received'})
        except Exception as e:
            print(f"Callback error: {str(e)}")
            return JsonResponse({'status': 'Error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'Method not allowed'}, status=405)
