from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    phone_number = models.CharField(unique=True)
    question = models.TextField(blank=True,null=True)
    answer = models.TextField(blank=True,null=True)
    assigned_staff = models.ForeignKey('StaffUser',on_delete=models.SET_NULL,blank=True,null=True,related_name="assigned_staff")
    class Meta:
        permissions = (
            ("can_assign_staff","Can Assign Staff to Users"),
        )
    

class StaffUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL,null=True)
    def __str__(self) -> str:
        return f"{self.user}"