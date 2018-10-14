from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('dashboard/<int:action>',  views.MessageList.as_view()),
    path('login/<int:role>', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),  
    path('user/', views.UserList.as_view()),
    path('user/create/', views.UserCreate.as_view()),    
    path('user/<int:pk>', views.UserDetail.as_view()),
    path('user/<int:pk>/update/', views.UserUpdate.as_view()), 
    path('user/<int:pk>/password/', views.UserPasswordUpdate.as_view()), 
    path('user/<int:pk>/teacher/', views.UserTeacher.as_view()),    	
    #設定教師
    path('teacher/make/', views.make),  	
	#私訊
    path('dashboard/',  views.LineList.as_view()),   
    path('line/classmate/<int:classroom_id>/', views.LineClassmateList.as_view()),      
    path('line/<int:user_id>/<int:classroom_id>/create/', views.LineCreate.as_view()), 
    path('line/<int:pk>/', views.LineDetail.as_view()),	
    # 列所出有圖像
    path('avatar/', views.avatar),  	
] 