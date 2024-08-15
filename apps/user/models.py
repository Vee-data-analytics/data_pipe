from django.db import models
from django.contrib.auth.models import User

class Programer(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   name = models.CharField(max_length=15)
   surname = models.CharField(max_length=15)

   def __str__(self):
      return self.name.surname

	
	
