# -*- coding: utf8 -*-
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path('classroom/', views.ClassroomList.as_view()),
    path('classroom/create/', views.ClassroomCreate.as_view()),    
    path('classroom/<int:pk>/update/', views.ClassroomUpdate.as_view()),  
    #列出所有學生帳號
    path('student/list/', views.StudentListView.as_view()),
	#大量匯入帳號
    path('import/upload/', views.import_sheet),
    path('import/student/', views.import_student),
    #修改資料
    path('password/<int:user_id>/', views.password),
    path('nickname/<int:user_id>/', views.nickname),
    # 分組
    path('group/number/<int:pk>', views.GroupUpdate.as_view()),    
    path('group/size/<int:pk>', views.GroupUpdate2.as_view()),  	
    path('group/make/<int:classroom_id>/<int:action>/', views.make),  
]