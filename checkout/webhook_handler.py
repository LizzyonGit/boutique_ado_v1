from django.http import HttpResponse

class StripeWH_Handler:
    """Handle Stripe webhooks
    
    The init method of the class is a setup method that's called every time an instance of the class is created.
For us we're going to use it to assign the request as an attribute of the class
just in case we need to access any attributes of the request coming from stripe.
"""

    def __init__(self, request):
        self.request = request

    
    def handle_event(self, event):
        """Handle generic/unknown/unexpected webhook event"""

        return HttpResponse(
            content=f'Unhandled webhook received: {event['type']}',
            status=200)
    
    def handle_payment_intent_succeeded(self, event):
        """Handle payment_intent.succeeded from Stripe"""

        return HttpResponse(
            content=f'Webhook received: {event['type']}',
            status=200)
    
    def handle_payment_intent_payment_failed(self, event):
        """Handle payment_intent.payment_failed from Stripe"""

        return HttpResponse(
            content=f'Webhook received: {event['type']}',
            status=200)

