from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, TemplateView
from . import models
from . import forms
import string
import random
import datetime
from datetime import datetime, date, timedelta
from django.utils import timezone

import stripe
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q


# Create your views here.


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))




class HomeView(ListView):
    model = models.Item
    paginate_by = 8
    template_name = 'core/home.html'

    


    def get_queryset(self):
        query_to_search_by = self.request.GET.get('query')
        if query_to_search_by:
                multiple_query = Q(
                Q(title__icontains=query_to_search_by) | 
                Q(category__icontains=query_to_search_by) |
                Q(description__icontains=query_to_search_by)
                ) 
                data = models.Item.objects.filter(multiple_query)
                object_list = data
        else:
                data = models.Item.objects.all()
                object_list = data
        return object_list

    

class ProductDetailView(LoginRequiredMixin, DetailView):
    login_url = 'user-login'
    model = models.Item
    template_name = 'core/product.html'



class OrderSummaryView(LoginRequiredMixin, View):
    login_url = 'user-login'

    def get(self, *args, **kwargs):
        try:
            order = models.Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object' : order,
                'couponform' : forms.CouponForm(),
                'DISPLAY_COUPON_FORM' : True,
            }
            return render(self.request, 'core/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an active order")
            return redirect("/")

    





# Take the customer information through the checkout.html page 
# and also show the customer cart inside it...
class CheckoutView(LoginRequiredMixin, View):
    login_url = 'user-login'

    def get(self, *args, **kwargs):
        try:
            order = models.Order.objects.get(user=self.request.user, ordered=False)
            form = forms.CheckoutForm()
            context = {
                'form' : form,
                'order' : order,
                'object' : order,
                'couponform' : forms.CouponForm(),
                'DISPLAY_COUPON_FORM' : False,
            }
            return render(self.request, 'core/checkout.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You don't have an active order.")
            return redirect("core:chekcout")


    

    def post(self, *args, **kwargs):
        form = forms.CheckoutForm(self.request.POST or None)
        try:
            order = models.Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')

                billing_address = models.BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zip = zip,
                )

                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect("core:create-checkout-session")
            messages.warning(self.request, "Failed checkout")
            return redirect("core:checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an active order")
            return redirect("core:order-summary")


stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateStripeCheckoutSessionView(LoginRequiredMixin, View):
    login_url = 'user-login'

    """
    Create a checkout session and redirect the user to Stripe's checkout page
    """
    def get(self, *args, **kwargs):
        try:
            order = models.Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order' : order,
                'object' : order,
                'DISPLAY_COUPON_FORM' : False,
            }
            return render(self.request, 'core/payment.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You don't have an active order.")
            return redirect("core:chekcout")
        

    def post(self, *args, **kwargs):
        order = models.Order.objects.get(user=self.request.user, ordered=False)
        order_count = models.Order.objects.filter(user=self.request.user, ordered=False).count()
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(order.get_total() * 100),
                        "product_data": {
                            "name": order.user.username,
                        },
                    },
                    "quantity": order_count,
                }
            ],
            # metadata={"product_id": price.product.id},
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )



        order_items = order.items.all()
        order_items.update(ordered = True)
        for item in order_items:
            item.save()

        
        order.ordered = True
        order.done_ordered_time = timezone.now()
        order.refund_code = create_ref_code()
        order.session_id = checkout_session.stripe_id
        order.save()

        # Send an email to the order owner...
        data = {
            "fname" : order.user.first_name,
            "lname" : order.user.last_name,
            "date" : order.ordered_date,
            "ref_code" : order.refund_code,
            "order" : order,
            'couponform' : forms.CouponForm(),
            'DISPLAY_COUPON_FORM' : True,
        }

        message = get_template('core/email_order.html').render(data)
        email = EmailMessage(
            "About your requested order from Shirt-Shop Website.",
            message,
            settings.EMAIL_HOST_USER,
            [order.user.email],
        )
        email.content_subtype = "html"
        email.send()


        return redirect(checkout_session.url)



class SuccessView(LoginRequiredMixin, TemplateView):
    login_url = 'user-login'

    template_name = "core/success.html"


class CancelView(LoginRequiredMixin, TemplateView):
    login_url = 'user-login'

    template_name = "core/cancel.html"




@login_required(login_url='user-login')
def add_to_cart(request, slug):

    # get the item
    item = get_object_or_404(models.Item, slug=slug)
    
    # create an order item or that order or get it if it exists
    order_item, created = models.OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )
    
    order_qs = models.Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item.quantity += 1
            order_item.save()

            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")


    else:    
        ordered_date = timezone.now()
        order = models.Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")








@login_required(login_url='user-login')
def remove_from_cart(request, slug):
    # get the item
    item = get_object_or_404(models.Item, slug=slug)
    
    order_qs = models.Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item = models.OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")

        else:
            messages.info(request, "This item is not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You don't have an active order.")
        return redirect("core:product", slug=slug)







@login_required(login_url='user-login')
def remove_single_item_from_cart(request, slug):
    # get the item
    item = get_object_or_404(models.Item, slug=slug)
    
    order_qs = models.Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item = models.OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect("core:order-summary")
            else:
                order.items.remove(order_item)
                order_item.save()
                messages.info(request, "This item was deleted from your cart.")
                return redirect("core:order-summary")


        else:
            messages.info(request, "This item is not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You don't have an active order.")
        return redirect("core:product", slug=slug)





@login_required(login_url='user-login')
def get_coupon(request, code):
    try:
        coupon = models.Coupon.objects.get(code = code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon doesn't exist.")
        return redirect("core:checkout")


@login_required(login_url='user-login')
def add_coupon(request):
    if request.method == "POST":
        form = forms.CouponForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = models.Order.objects.get(user=request.user, ordered=False)
                order.coupon = get_coupon(request, code)
                order.save()
                messages.success(request, "This coupon is successfully applied.")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(request, "You don't have an active order.")
                return redirect("core:chekcout")
    return None





class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = forms.RefundForm()
        context = {
            'form' : form,
        }
        return render(self.request, 'core/request_refund.html', context)
    
    def post(self, *args, **kwargs):
        form = forms.RefundForm(self.request.POST)
        if form.is_valid():
            refund_code = form.cleaned_data.get("ref_code")
            message = form.cleaned_data.get("message")
            email = form.cleaned_data.get("email")

            try:
                order = models.Order.objects.get(refund_code = refund_code) 
                if order.refund_status == False:
                    order.refund_status = True

                    refund = models.Refund()
                    refund.order = order
                    refund.reason = message
                    refund.email = email


                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    session_id = order.session_id
                    payment_intent = stripe.checkout.Session.retrieve(str(session_id),)
                    order.payment_intent_id = payment_intent["payment_intent"]

                    order.save()
                    refund.save()

                    data = {
                        "name" : order.user.username,
                        "date" : date.today(),
                        "ref_code" : order.refund_code,
                        "order" : order,
                    }

                    message = get_template('core/email_refund.html').render(data)
                    email = EmailMessage(
                        "About your refund request for an order from Shirt-Shop Website.",
                        message,
                        settings.EMAIL_HOST_USER,
                        [order.user.email],
                    )
                    email.content_subtype = "html"
                    email.send()

                    messages.info(self.request, "Your refund request was recived, check your mail to confirm it.")
                    return redirect("core:home")
                else:
                    messages.warning(self.request, "This refund request was recived before.")
                    return redirect("core:request-refund")
            except ObjectDoesNotExist:
                messages.warning(self.request, "This order doesn't exist.")
                return redirect("core:request-refund")
                




class ConfirmRefundView(View):
    def get(self, *args, **kwargs):
        form = forms.ConfirmRefundForm()
        context = {
            'form' : form,
        }
        return render(self.request, 'core/confirm_refund.html', context)
    
    def post(self, *args, **kwargs):
        form = forms.ConfirmRefundForm(self.request.POST)
        if form.is_valid():
            refund_code = form.cleaned_data.get("ref_code")
            try:
                order = models.Order.objects.get(refund_code = refund_code)
                if order.refund_status == True:
                    refund = models.Refund.objects.get(order=order)
                    if refund.accepted == False:
                        refund.accepted = True


                        stripe.api_key = settings.STRIPE_SECRET_KEY
                        payment_intent_id = order.payment_intent_id
                        stripe.Refund.create(payment_intent = str(payment_intent_id),)


                        order.save()
                        refund.save()

                        messages.info(self.request, "Your order was refunded successfully and your money was recevied, check your wallet right now.")
                        return redirect("core:home")
                    else:
                        messages.warning(self.request, "This order was already refunded.")
                        return redirect("core:confirm-refund")
                else:
                    messages.warning(self.request, "This refund confirmation cann't be done, make an refund request first then check your mail again.")
                    return redirect("core:request-refund")
            except ObjectDoesNotExist:
                messages.warning(self.request, "This refund code is invalid, please try again.")
                return redirect("core:confirm-refund")
        else:
            messages.warning(self.request, "This form isn't valid.")
            return redirect("core:confirm-refund")

                

 


            


class SearchView(ListView):
    def get(self, request):
        items = models.Item.objects.filter(category='S')

        context = {
            'object_list' : items,
        }
        return render(self.request, 'core/home.html', context)
    



class ShirtsView(ListView):
    def get(self, request):
        data = models.Item.objects.filter(category='S')
        
        paginator = Paginator(data, 9)
        page_number = request.GET.get('page')
        items = paginator.get_page(page_number)

        context = {
            'object_list' : items,
        }
        return render(self.request, 'core/home.html', context)
    



class Sport_WearView(ListView):
    def get(self, request):
        items = models.Item.objects.filter(category='SW')

        context = {
            'object_list' : items,
        }
        return render(self.request, 'core/home.html', context)
    


class Out_WearView(ListView):
    def get(self, request):
        items = models.Item.objects.filter(category='OW')

        context = {
            'object_list' : items,
        }
        return render(self.request, 'core/home.html', context)