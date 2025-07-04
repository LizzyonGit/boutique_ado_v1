from django.contrib import admin
from .models import Order, OrderLineItem

# Register your models here.

class OrderLineItemAdminInline(admin.TabularInline):
    """This inline item is going to allow us to add and edit line items in the admin
    right from inside the order model.
    So when we look at an order. We'll see a list of editable line items on the same page.
    Rather than having to go to the order line item interface.
    """
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)

class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)
    readonly_fields = ('order_number', 'date', 'delivery_cost',
                       'order_total', 'grand_total', 'original_bag', 'stripe_pid')
    fields = ('order_number', 'user_profile', 'date', 'full_name', 'email', 'phone_number',
              'country', 'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost', 'order_total', 'grand_total', 'original_bag', 'stripe_pid')
    list_display = ('order_number', 'date', 'full_name', 
                    'order_total', 'delivery_cost', 'grand_total',)
    ordering = ('-date',)

admin.site.register(Order, OrderAdmin)