from django.db import models
from django.contrib.gis.db import models as gismodels


class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    location = gismodels.PointField()
    describe = models.CharField(max_length=1000, default= True, blank=True)


class communicate(models.Model):
    username1 = models.CharField(max_length=50)
    text= models.CharField(max_length=100)
    username2 = models.CharField(max_length=50)




