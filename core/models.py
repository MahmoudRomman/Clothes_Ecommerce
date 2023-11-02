import datetime
from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.contrib.auth.models import User

# Create your models here.

CATEGORIES_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'Out Wear')
)


LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)



class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    image = models.ImageField(default="no_product_img.png", upload_to="core_images", null=True, blank=True)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORIES_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    


    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("core:product", kwargs={"slug": self.slug})
    
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"slug":self.slug})
    
    def get_remove_from_cart_url(self):
      return reverse("core:remove-from-cart", kwargs={"slug":self.slug})
    


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.item.price * self.quantity
    
    def get_total_discount_item_price(self):
        return self.item.discount_price * self.quantity
    
    def get_amount_saved(self):
        return (self.item.price - self.item.discount_price) * self.quantity

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        else:
            return self.get_total_item_price()
    



    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    done_ordered_time = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    refund_code = models.CharField(max_length=20)
    refund_status = models.BooleanField(default=False)
    session_id = models.CharField(max_length=66)
    payment_intent_id = models.CharField(max_length=27)


    
    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
        


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=200)
    apartment_address = models.CharField(max_length=200)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username





class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField(default=0.00)


    def __str__(self):
        return self.code
    

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    # def __str__(self):
    #     return f"{self.pk}" 

    def __str__(self):
        return f"refund for {self.order.user.first_name} {self.order.user.last_name}" 