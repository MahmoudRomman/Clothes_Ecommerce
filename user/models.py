from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# Create our model from the abstractuser model (our customzed model)
class Profile(models.Model):
    staff = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=11, null=True, blank=True)

    def __str__(self):
        return f"{self.staff.username}"
