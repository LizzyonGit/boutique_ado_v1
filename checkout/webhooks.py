from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe
"""We'll need our settings file to get the webhook and the stripe API secrets.
We need HttpResponse so these exception handlers will work.
We'll need our webhook handler class and of course stripe."""

"""And last we need two decorators require_post which as the name implies will make
this view require a post request and will reject get requests.
And CSRF exempt since stripe won't send a CSRF token like we'd normally need."""
@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    # we'll need to set up the stripe API key and the webhook secret which will be used to verify that the webhook actually came from stripe. 
    wh_secret = settings.STRIPE_WH_SECRET 
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WH_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    except Exception as e:
        return HttpResponse(content=e, status=400)  #I'll also add a generic exception handler to catch any exceptions other than the two stripe has provided.

