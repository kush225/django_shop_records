from django.db import models

# Create your models here.

columns=["s_no", "rc_number", "scheme", "type", "receipt_number", "date", "wheat", "rice", "sugar", "pm_wheat", "pm_rice", "amount", "portability", "auth_time"]

class Records(models.Model):
	id = models.AutoField(primary_key=True)
	s_no = models.IntegerField()
	rc_number = models.CharField(max_length=50)
	scheme = models.CharField(max_length=50)
	type = models.CharField(max_length=50)
	receipt_number = models.CharField(max_length=50)
	date = models.DateField()
	kejriwal_wheat = models.FloatField()
	kejriwal_rice = models.FloatField()
	kejriwal_sugar = models.FloatField()
	pm_wheat = models.FloatField()
	pm_rice = models.FloatField()
	amount = models.FloatField()
	portability = models.CharField(max_length=50)
	auth_time = models.FloatField()

	
