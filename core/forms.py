from django import forms
from django_countries.fields import CountryField

from django_countries.widgets import CountrySelectWidget

PAYMENT_OPTOINS = (
    ('S', 'Stripe'),
    ('P', 'Paypal'),
)



class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder' : '1234 Main St',
    }))

    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder' : 'Apartment or suite',
    }))

    country = CountryField(blank_label="(select country)").formfield(
        widget=CountrySelectWidget(attrs={ 'class' : 'custom-select d-block w-100',
    }))

    zip = forms.CharField(widget=forms.TextInput(attrs={
        'calss' : 'form-control'
    }))




class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Promo Code..',
        'aria-label' : 'Recipient\'s username',
        'aria-describedby' : 'basic-addon2',
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows' : 4,
    }))
    email = forms.EmailField()


class ConfirmRefundForm(forms.Form):
    ref_code = forms.CharField()