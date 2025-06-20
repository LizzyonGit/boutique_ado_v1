from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import json
import time
import stripe

class StripeWH_Handler:
    """Handle Stripe webhooks
    
    The init method of the class is a setup method that's called every time an instance of the class is created.
For us we're going to use it to assign the request as an attribute of the class
just in case we need to access any attributes of the request coming from stripe.
"""

    def __init__(self, request):
        self.request = request


    def _send_confirmation_email(self, order):  # private method
        """Send user confirmation email"""
        cust_email = order.email  # email address
        """Then we can use the render_to_string method to render both the files we just created two strings.
            With the first parameter being the file we want to render.
            And the second being at context just like we would pass to a template.
            This is how we'll be able to render the various context variables in the confirmation email."""
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        
        # send email
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [cust_email])


    
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

        
        # update profile info when save_info is checked
        profile = None  # so anonymous users can check out
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number=shipping_details.phone,
                profile.default_country=shipping_details.address.country,
                profile.default_postcode=shipping_details.address.postal_code,
                profile.default_town_or_city=shipping_details.address.city,
                profile.default_street_address1=shipping_details.address.line1,
                profile.default_street_address2=shipping_details.address.line2,
                profile.default_county=shipping_details.address.state,
                profile.save()



        # in normal situation, the order goes through and is in database when we receive this webhook let's assume it does not exist
        order_exists = False

        attempt = 1
        while attempt <= 5:
            # Then we'll try to get the order using all the information from the payment intent. And I'm using the iexact lookup field to make it an exact match but case-insensitive.
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,  # so it is unique, not double order, in case order has same bag
                )

                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)     # sleep one second   
        
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                    status=200)
        else:
                order = None
                # from views.py with some changes
                try:
                    order = Order.objects.create(
                        full_name=shipping_details.name,
                        user_profile=profile,  # add profile to order
                        email=billing_details.email,
                        phone_number=shipping_details.phone,
                        country=shipping_details.address.country,
                        postcode=shipping_details.address.postal_code,
                        town_or_city=shipping_details.address.city,
                        street_address1=shipping_details.address.line1,
                        street_address2=shipping_details.address.line2,
                        county=shipping_details.address.state,
                        original_bag=bag,
                        stripe_pid=pid,

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
        

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)  # If we got to this point in the code, we know the order was created in webhook handler.
    
    def handle_payment_intent_payment_failed(self, event):
        """Handle payment_intent.payment_failed from Stripe"""

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

