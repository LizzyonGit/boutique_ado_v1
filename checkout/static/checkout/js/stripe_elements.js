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
let stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
let client_secret = $('#id_client_secret').text().slice(1, -1);

/*All we need to do to set up stripe is create a variable using our stripe public key.
Now we can use it to create an instance of stripe elements.
Use that to create a card element.
And finally, mount the card element to the div we created in the last video. */
let stripe = Stripe(stripe_public_key);
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
    let errorDiv = document.getElementById('card-error');
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