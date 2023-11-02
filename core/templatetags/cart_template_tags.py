from django import template
from core import models
register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = models.Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
        else:
            return 0
    else:
        return 0