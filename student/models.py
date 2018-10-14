# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
from teacher.models import Classroom
from django.utils import timezone
from django.core.validators import RegexValidator, validate_comma_separated_integer_list

# 學生選課資料
class Enroll(models.Model):
    # 學生序號
    student_id = models.IntegerField(default=0)
    # 班級序號
    classroom_id = models.IntegerField(default=0)
    # 座號
    seat = models.IntegerField(default=0)
    # 組別
    group = models.IntegerField(default=0)
    # 創意秀組別
    #groupshow = models.CommaSeparatedIntegerField(max_length=200)
    groupshow = models.CharField(validators=[validate_comma_separated_integer_list], max_length=200)   
    
    @property
    def classroom(self):
        return Classroom.objects.get(id=self.classroom_id)

    @property
    def student(self):
        return User.objects.get(id=self.student_id)      

    def __str__(self):
        return str(self.id) + ":" + str(self.classroom_id)

    class Meta:
        unique_together = ('student_id', 'classroom_id',)
        
    def set_foo(self, x):
        self.groupshow = json.dumps(x)

    def get_groupshow(self):
        return json.loads(self.groupshow)     	
		
class StudentGroup(models.Model):
    group_id = models.IntegerField(default=0)
    enroll_id = models.IntegerField(default=0)

    class Meta:
        unique_together = ('enroll_id', 'group_id')