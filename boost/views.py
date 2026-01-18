from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import PayheroService
import json
import uuid

def landing(request):
    limits = [
        {'amount': '5,000', 'charge': '99'},
        {'amount': '6,800', 'charge': '130'},
        {'amount': '9,800', 'charge': '190'},
        {'amount': '16,800', 'charge': '250'},
        {'amount': '25,600', 'charge': '400'},
        {'amount': '35,400', 'charge': '590'},
        {'amount': '44,200', 'charge': '1,010'},
        {'amount': '50,000', 'charge': '1,000'}
    ]
    return render(request, 'boost/landing.html', {'limits': limits})

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
            description = f"Fuliza Boost Charge - {reference}"
            
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
