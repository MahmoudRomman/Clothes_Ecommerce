from django.contrib import admin
from . import models 
# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display =  ['user', 'ordered', 'billing_address', 'coupon']
    list_display_links = ['user', 'billing_address', 'coupon']
    list_filter =  ['ordered']
    search_fields = ['user__username', 'ref_code']


admin.site.register(models.Item)
admin.site.register(models.OrderItem)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.BillingAddress)
admin.site.register(models.Coupon)
admin.site.register(models.Refund)



