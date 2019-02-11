# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid

# Create your models here.
class Post(models.Model):
    data = models.TextField()
    likes = models.TextField(null=True,blank=True)
