from django.db.models.signals import post_save, post_delete

from django.dispatch import receiver

from .models import OrderLineItem

"""So this implies these signals are sent by django to the entire application
after a model instance is saved and after it's deleted respectively.
To receive these signals we can import receiver from django.dispatch.
Of course since we'll be listening for signals from the OrderLineItem model"""

# Now to execute this function anytime the post_save signal is sent.
# I'll use the receiver decorator. Telling it we're receiving post saved signals.
# From the OrderLineItem model.
@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    So these parameters refer to the sender of the signal. In our case OrderLineItem.
    The actual instance of the model that sent it.
    A boolean sent by django referring to whether this is a new instance or one being updated.
    And any keyword arguments.
    """
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    To handle updating the various totals when a line item is deleted.
    We can just copy the whole function. Change the signal,
    And remove the created parameter because it's not sent by this signal.
    """
    instance.order.update_total()
