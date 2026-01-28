from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import PayheroService
import json
import uuid

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
            amount = data.get('amount')
            
            # Remove commas from amount string
            amount = float(amount.replace(',', ''))
            
            reference = str(uuid.uuid4())[:8].upper()
            description = f"Nyota Fund Charge - {reference}"
            
            payhero = PayheroService()
            result = payhero.initiate_stk_push(
                phone_number=phone_number,
                amount=amount,
                reference=reference,
                description=description
            )
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa payment callback from Payhero.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Log the callback data for debugging
            print(f"Callback received: {json.dumps(data, indent=2)}")
            
            # Here you would typically update a transaction record in your database
            
            return JsonResponse({'status': 'Received'})
        except Exception as e:
            return JsonResponse({'status': 'Error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'Method not allowed'}, status=405)
