from django.http import HttpResponse

import Stripe 

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
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)
    
    def handle_payment_intent_succeeded(self, event):
        """Handle payment_intent.succeeded from Stripe"""
        # payment intent from stripe, should have metadata
        intent = event.data.object
        print(intent)

        pid = intent.id
        # get stuff from metadata
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        billing_details = stripe_charge.billing_details # updated
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2) # updated

        # clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # in normal situation, the order goes through and is in database when we receive this webhook let's assume it does not exist
        order_exists = False
        # Then we'll try to get the order using all the information from the payment intent. And I'm using the iexact lookup field to make it an exact match but case-insensitive.
        try:
            order = Order.objects.get(
                full_name__iexact=shipping_details.name,
                email__iexact=shipping_details.email,
                phone_number__iexact=shipping_details.phone,
                country__iexact=shipping_details.country,
                postcode__iexact=shipping_details.postal_code,
                town_or_city__iexact=shipping_details.city,
                street_address1__iexact=shipping_details.line1,
                street_address2__iexact=shipping_details.line2,
                county__iexact=shipping_details.state,
                grand_total=grand_total,
            )

            order_exists = True
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200
            )
        
        except Order.DoesNotExist:
            # from views.py with some changes
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=shipping_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.country,
                    postcode=shipping_details.postal_code,
                    town_or_city=shipping_details.city,
                    street_address1=shipping_details.line1,
                    street_address2=shipping_details.line2,
                    county=shipping_details.state,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(content=f'Webhook received: {event["type"]} | ERROR: {e}',
                                    status=500 )


        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
    
    def handle_payment_intent_payment_failed(self, event):
        """Handle payment_intent.payment_failed from Stripe"""

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

