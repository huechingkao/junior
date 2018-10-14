from django.shortcuts import render
from teacher.models import *
from student.models import *
from student.forms import EnrollForm
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, RedirectView, TemplateView
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from account.models import Message, MessagePoll
from account.forms import LineForm
from django.contrib.auth.mixins import LoginRequiredMixin

# 判斷是否為授課教師
def is_teacher(user, classroom_id):
    return  user.groups.filter(name='teacher').exists() and Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists()

# 判斷是否為同班同學
def is_classmate(user, classroom_id):
    enroll_pool = [enroll for enroll in Enroll.objects.filter(classroom_id=classroom_id).order_by('seat')]
    student_ids = map(lambda a: a.student_id, enroll_pool)
    if user.id in student_ids:
        return True
    else:
        return False

class ClassroomList(LoginRequiredMixin,generic.ListView):
    model = Classroom
    paginate_by = 3   
    template_name = 'student/classroom_list.html'
       
    def get_context_data(self, **kwargs):
        context = super(ClassroomList, self).get_context_data(**kwargs)
        queryset = []
        enrolls = Enroll.objects.filter(student_id=self.request.user.id)
        classroom_ids = list(map(lambda a: a.classroom_id, enrolls))        
        classroom_dict = dict((f.classroom_id, f) for f in enrolls)
        classrooms = Classroom.objects.filter(id__in=classroom_ids)
        for classroom in classrooms:
            queryset.append([classroom, classroom_dict[classroom.id]])
        context['queryset'] = queryset 
        return context 

class ClassroomJoinList(LoginRequiredMixin,generic.ListView):
    model = Classroom
    template_name = 'student/classroom_join.html'    
    
    def get_context_data(self, **kwargs):
        context = super(ClassroomJoinList, self).get_context_data(**kwargs)
        queryset = []
        enrolls = Enroll.objects.filter(student_id=self.request.user.id)
        classroom_ids = list(map(lambda a: a.classroom_id, enrolls))        
        classrooms = Classroom.objects.all().order_by("-id")
        for classroom in classrooms:
            if classroom.id in classroom_ids:
                queryset.append([classroom, True])
            else:
                queryset.append([classroom, False])
        context['queryset'] = queryset 
        return context 

class ClassroomEnrollCreate(LoginRequiredMixin,CreateView):
    model = Enroll
    form_class = EnrollForm    
    success_url = "/student/classroom"  
    template_name = "form.html"
    
    def form_valid(self, form):
        valid = super(ClassroomEnrollCreate, self).form_valid(form)
        if form.cleaned_data['password'] == Classroom.objects.get(id=self.kwargs['pk']).password:
            enrolls = Enroll.objects.filter(student_id=self.request.user.id, classroom_id=self.kwargs['pk'])
            if not enrolls.exists():
                enroll = Enroll(student_id=self.request.user.id, classroom_id=self.kwargs['pk'], seat=form.cleaned_data['seat'])
                enroll.save()
        return valid

class ClassmateList(LoginRequiredMixin,generic.ListView):
    model = Enroll   
    template_name = 'student/classmate.html'
    
    def get_queryset(self):
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['pk'])
        return enrolls    
      
class ClassroomSeatUpdate(LoginRequiredMixin,UpdateView):
    model = Enroll
    fields = ['seat']
    success_url = "/student/classroom/"      
    template_name = "form.html"
	
#新增一個公告
class AnnounceCreate(LoginRequiredMixin, CreateView):
    model = Message
    form_class = LineForm
    success_url = '/account/dashboard'    
    template_name = 'teacher/announce_form.html'     

    def form_valid(self, form):
        valid = super(AnnounceCreate, self).form_valid(form)
        self.object = form.save(commit=False)
        classroom = Classroom.objects.get(id=self.kwargs['classroom_id'])
        self.object.title = u"[公告]" + classroom.name + ":" + self.object.title
        self.object.author_id = self.request.user.id
        self.object.save()
        # 訊息
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id'])
        for enroll in enrolls :
            messagepoll = MessagePoll(message_id=self.object.id, reader_id=enroll.student_id)
            messagepoll.save()              
        return valid
      
    # 限本班教師
    def render_to_response(self, context):
        teacher_id = Classroom.objects.get(id=self.kwargs['classroom_id']).teacher_id
        if not teacher_id == self.request.user.id:
            return redirect('/')
        return super(AnnounceCreate, self).render_to_response(context)       
      
    def get_context_data(self, **kwargs):
        context = super(AnnounceCreate, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        return context				
			
# 選組所有組別
class GroupPanel(LoginRequiredMixin,ListView):
    context_object_name = 'groups'
    template_name = 'student/group_panel.html'
    
    def get_queryset(self):  
        classroom_id = self.kwargs['classroom_id']
        groups = []
        student_groups = {}
        enroll_list = []
        group_list = {}
        group_ids = []
        numbers = Classroom.objects.get(id=classroom_id).group_number
        enrolls = Enroll.objects.filter(classroom_id=classroom_id).order_by("seat")
        for enroll in enrolls:
            enroll_list.append(enroll.id)
        enroll_groups = StudentGroup.objects.filter(enroll_id__in=enroll_list)
        for enroll_group in enroll_groups:
            group_ids.append(enroll_group.enroll_id)
            group_list[enroll_group.enroll_id] = enroll_group.group_id
            enroll = Enroll.objects.get(id=enroll_group.enroll_id)
            if enroll_group.group_id in student_groups:
                student_groups[enroll_group.group_id].append(enroll)
            else:
                student_groups[enroll_group.group_id]=[enroll]	            
        for i in range(numbers):
            if i in student_groups:
                groups.append([i, student_groups[i]])
            else:
                groups.append([i, []])
					
        return groups


    def get_context_data(self, **kwargs):
        context = super(GroupPanel, self).get_context_data(**kwargs)        
        classroom_id = self.kwargs['classroom_id']
        classroom = Classroom.objects.get(id=classroom_id)
        context['classroom'] = classroom
        enroll_user = Enroll.objects.get(student_id=self.request.user.id, classroom_id=classroom_id)        
        context['enroll_id'] = enroll_user.id
        student_groups = {}        
        group_list = {}        
        enroll_list = []        
        group_ids = []        
        enrolls = Enroll.objects.filter(classroom_id=classroom_id).order_by("seat")
        for enroll in enrolls:
            enroll_list.append(enroll.id)
        enroll_groups = StudentGroup.objects.filter(enroll_id__in=enroll_list)
        for enroll_group in enroll_groups:
            group_ids.append(enroll_group.enroll_id)
            group_list[enroll_group.enroll_id] = enroll_group.group_id
            enroll = Enroll.objects.get(id=enroll_group.enroll_id)
            if enroll_group.group_id in student_groups:
                student_groups[enroll_group.group_id].append(enroll)
            else:
                student_groups[enroll_group.group_id]=[enroll]	  
        #找出尚未分組的學生
        no_group = []
        for enroll in enrolls:
            if not enroll.id in group_ids:
                no_group.append([enroll.seat, enroll.student])
        context['student_groups'] = student_groups                
        context['no_group'] = no_group 
        context['classroom_id'] = classroom_id
        return context

#加入某一組
class GroupJoin(LoginRequiredMixin, RedirectView):

    def get(self, request, *args, **kwargs):
        classroom_id = self.kwargs['classroom_id'] 
        enroll_id = self.kwargs['enroll_id']
        number = self.kwargs['number']
        try:
            group = StudentGroup.objects.get(enroll_id=enroll_id)
            group.group_id = number
        except ObjectDoesNotExist:
            group = StudentGroup(enroll_id=enroll_id, group_id=number)
        if Classroom.objects.get(id=classroom_id).group_open:
            group.save()	
        return super(GroupJoin, self).get(self, request, *args, **kwargs)        
        
    def get_redirect_url(self, *args, **kwargs):
        #TaxRate.objects.get(id=int(kwargs['pk'])).delete()   
        return '/student/group/'+str(self.kwargs['classroom_id']) 
