from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'  # all fields
    
    image = forms.ImageField(label='image', required=False, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # override init method
        categories = Category.objects.all()
        """And create a list of tuples of the friendly names associated with their category ids.
        This special syntax is called the list comprehension.
        And is just a shorthand way of creating a for loop that adds items to a list.
        get_friendly_name is method in Category model"""
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        
        """Update the category field on the form to use those for choices instead of using the id."""
        self.fields['category'].choices = friendly_names

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'

        

