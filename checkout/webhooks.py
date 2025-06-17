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
    
    #print('Success!')
    #return HttpResponse(status=200)

    #set up webhook handler
    """First I'll just create an
    instance of it passing in the request. Then I'll create a dictionary called event map
    and the dictionaries keys will be the names of the webhooks coming from stripe. While its values will be the actual methods inside the handler."""
    handler = StripeWH_Handler(request)

    # map webhook events to relevant handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # get the webhook type from stripe
    """Now let's get the type of the event from stripe which will be stored in a key called type."""
    event_type = event['type']
    """And then we'll look up the key in the dictionary.
    And assign its value to a variable called event handler"""
    event_handler = event_map.get(event_type, handler.handle_event)

    # call the evnet handler with the event
    response = event_handler(event)
    return response


