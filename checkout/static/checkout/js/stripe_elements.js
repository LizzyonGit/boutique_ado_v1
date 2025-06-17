/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

/*Remember those little script elements contain the values we need as their text.
So we can get them just by getting their ids and using the .text function.
I'll also slice off the first and last character on each
since they'll have quotation marks which we don't want.*/
let stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
let clientSecret = $('#id_client_secret').text().slice(1, -1);

/*All we need to do to set up stripe is create a variable using our stripe public key.
Now we can use it to create an instance of stripe elements.
Use that to create a card element.
And finally, mount the card element to the div we created in the last video. */
let stripe = Stripe(stripePublicKey);
let elements = stripe.elements();
let style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
let card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle realtime validation error on card element
/*Looking at the site now it's more clear what the issue is if the user experience is an error.
As we've rendered the error from stripe with a nice little icon next to it. */
card.addEventListener('change', function (event) {
    let errorDiv = document.getElementById('card-errors');
    if (event.error) {
        let html = `
        <span class='icon' roles='alert'>
            <i class="fas fa-times"></i>
        </span>
        <span>${event.error.message}</span>`;
        $(errorDiv).html(html);
    } else{
        errorDiv.textContent = '';
    }

    }
);

// Handle form submit
let form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();  // After getting the form element the first thing the listener does is prevent its default action which in our case is to post.
    card.update({ 'disabled': true});

    
    $('#submit-button').attr('disabled', true);  // Here before we call out to stripe. We'll want to disable both the card element and the submit button to prevent multiple submissions.
    $('#payment-form').fadeToggle(100);  // Payment-form comes from Stripe when authentication is needed?
    $('#loading-overlay').fadeToggle(100);

    let saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form
    let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    // create object to pass this to view
    let postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };

    let url = '/checkout/cache_checkout_data/';
    // post postdata to the url
    $.post(url,postData).done(function(){
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                //Basically since the payment intent .succeeded webhook will be coming from stripe
                //and not from our own code into the webhook handler, we need to somehow stuff the
                //form data into the payment intent object so we can retrieve it once we receive the webhook.
                //Most of this we can do by simply adding the form data to the
                //confirmed card payment method. For example if you were to look at the
                //stripe documentation and see the structure of a payment intent object.
                //You'd see it has a spot for a billing details object we can add right here under the card.

                //It can take a name, email, phone number, and an address with mostly
                //the same fields we've got in our form. I'll add all this in getting the data
                //from our form and using the trim method to strip off any excess whitespace.
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address:{
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            },
            //We can also add some shipping information with all the same fields
            //except for email. By the way, you'll notice I've also only added postcode to the shipping
            //information since the billing postal code will come from the card
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            },
        
        }).then(function(result) {  //So we call the confirm card payment method. Provide the card to stripe and then execute this function on the result.
            if (result.error) {
                let errorDiv = document.getElementById('card-errors');
                let html = `<span class="icon" role="alert"><i class="fas fa-times"></i></span><span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                // Reverses prev fadetoggles that if there's any error. Don't really understand this.
                $('#payment-form').fadeToggle(100); 
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);  // allows user to fix it when error
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    
                    form.submit();
                }
            }
        });
    }).fail(function () {
        // just reloads the page, the error will be in django messages
        location.reload();
    })

    
    
});