from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)  # render all fields except for user, that sjould never change
        
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field

        First we call the default init method to set the form up as it would be by default.
        After that, I've created a dictionary of placeholders which will show up
        in the form fields 
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        # Next we're setting the autofocus attribute on the full name field to true so the cursor will start in the full name field when the user loads the page.
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True

        # And finally we iterate through the forms fields adding a star to the placeholder if it's a required field on the model.
        # Setting all the placeholder attributes to their values in the dictionary above.
        # Adding a CSS class we'll use later.
        # And then removing the form fields labels.
        for field in self.fields:
            if field != 'default_country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False    