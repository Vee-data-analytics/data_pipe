from django.db import models


class Production(models.Model):
    date = models.DateTimeField()

    CATEGORY_CHOICES = (
        ('U2', 'SMT-U1'),
        ('U1', 'SMT-U2'),
        ('P1', 'SMT-P1'),
        ('P2', 'SMT-P2'),
        ('P3', 'SMT-P3'),
        ('BPR1', 'BPR1'),
        ('BPR2', 'BPR2'),
        ('Conventional line 1 H/I', 'Conventional line 1 H/I'),
        ('Conventional line 2 H/I', 'Conventional line 2 H/I'),
        ('Conventional line 3 H/I', 'Conventional line 3 H/I'),
        ('Conventional line 1 H/A', 'Conventional line 1 H/A'),
        ('Conventional line 2 H/A', 'Conventional line 2 H/A'),
        ('Conventional line 3 H/A', 'Conventional line 3 H/A'),
        ('Test', 'Test'),
    )

    CAT_CHOICES = [(code, labels) for code, labels in CATEGORY_CHOICES.items()]
    name = models.TextField(choices=CAT_CHOICES, max_length=50, null=True)
    product = models.TextField(max_length=250, null=True)

    date_of_upload = models.DateTimeField(default=timezone.now, null=True)

    department = models.CharField(choices=CATEGORY_CHOICES, max_length=250, default='', null=True)

    CUSTOMER_CHOICES = (
        ('L_G', 'LG'),
        ('Landis', 'Landis & Gyr'),
        ('DME', 'Digital Matter'),
        ('CarTck', 'Cartrack'),
        ('etv', 'ETV'),
    )



class Department(models.Model):
    name = models.TextField(null = True, blank=True, max_length=120)
    description=models.TextField(null = True, blank=True, max_length=120)

class Client(model.Model):
    name = TextField(null = True, blank=True, max_length=120)
    description=models.TextField(null = True, blank=True, max_length=120)



class Product(models.Model):
    name = TextField(null = True, blank=True, max_length=120)
    revision =  TextField(null = True, blank=True, max_length=120)
