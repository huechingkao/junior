from django.shortcuts import render, redirect
from teacher.models import *
from student.models import *
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, RedirectView
from teacher.forms import *
from account.forms import PasswordForm, NicknameForm
import django_excel as excel
from django.http import HttpResponse, HttpResponseRedirect

def is_assistant(user, classroom_id):
    assistants = Assistant.objects.filter(classroom_id=classroom_id, user_id=user.id)
    if len(assistants)>0 :
        return True
    return False

# 判斷是否為授課教師
def is_teacher(user, classroom_id):
    return user.groups.filter(name='teacher').exists() and Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists()

def in_teacher_group(user):
    if not user.groups.filter(name='teacher').exists():
        if not Assistant.objects.filter(user_id=user.id).exists():
            return False
    return True

class ClassroomList(generic.ListView):
    model = Classroom
    ordering = ['-id']
    paginate_by = 3   
    
class ClassroomCreate(CreateView):
    model =Classroom
    fields = ["lesson", "name", "password"]
    success_url = "/teacher/classroom"   
    template_name = 'form.html'
      
    def form_valid(self, form):
        valid = super(ClassroomCreate, self).form_valid(form)
        classroom = form.save(commit=False)
        classroom.teacher_id = self.request.user.id
        classroom.save() 
        enroll = Enroll(classroom_id=classroom.id, student_id=classroom.teacher_id, seat=0)
        enroll.save()
        return valid
    
class ClassroomUpdate(UpdateView):
    model = Classroom
    fields = ["name", "password"]
    success_url = "/teacher/classroom"   
    template_name = 'form.html'
	
# 教師可以查看所有帳號
class StudentListView(ListView):
    context_object_name = 'users'
    paginate_by = 50
    template_name = 'teacher/student_list.html'

    def get_queryset(self):
        username = username__icontains=self.request.user.username+"_"
        if self.request.GET.get('account') != None:
            keyword = self.request.GET.get('account')
            queryset = User.objects.filter(Q(username__icontains=username+keyword) | (Q(first_name__icontains=keyword) & Q(username__icontains=username))).order_by('-id')
        else :
            queryset = User.objects.filter(username__icontains=username).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(StudentListView, self).get_context_data(**kwargs)
        account = self.request.GET.get('account')
        context.update({'account': account})
        return context
		
# Create your views here.
def import_sheet(request):
    if not in_teacher_group(request.user):
        return redirect("/")
    if request.method == "POST":
        form = UploadFileForm(request.POST,
                              request.FILES)
        if form.is_valid():
            ImportUser.objects.all().delete()
            request.FILES['file'].save_to_database(
                name_columns_by_row=0,
                model=ImportUser,
                mapdict=['username', 'first_name', 'password'])
            users = ImportUser.objects.all()
            return render(request, 'teacher/import_student.html',{'users':users})
        else:
            return HttpResponseBadRequest()
    else:
        form = UploadFileForm()
    return render(
        request,
        'teacher/import_form.html',
        {
            'form': form,
            'title': 'Excel file upload and download example',
            'header': ('Please choose any excel file ' +
                       'from your cloned repository:')
        })

# Create your views here.
def import_student(request):
    if not in_teacher_group(request.user):
        return redirect("/")

    users = ImportUser.objects.all()
    username_list = [request.user.username+"_"+user.username for user in users]
    exist_users = [user.username for user in User.objects.filter(username__in=username_list)]
    create_list = []
    for user in users:
        username = request.user.username+"_"+user.username
        if username in exist_users:
            continue
        new_user = User(username=username, first_name=user.first_name, last_name=request.user.last_name, password=user.password, email=username+"@edu.tw")
        new_user.set_password(user.password)
        create_list.append(new_user)

    User.objects.bulk_create(create_list)
    new_users = User.objects.filter(username__in=[user.username for user in create_list])

    profile_list = []
    message_list = []
    poll_list = []
    title = "請洽詢任課教師課程名稱及選課密碼"
    url = "/student/classroom/add"
    message = Message(title=title, url=url, time=timezone.now())
    message.save()
    for user in new_users:
        profile = Profile(user=user)
        profile_list.append(profile)
        poll = MessagePoll(message_id=message.id, reader_id=user.id)
        poll_list.append(poll)

    Profile.objects.bulk_create(profile_list)
    MessagePoll.objects.bulk_create(poll_list)

    return redirect('/teacher/student/list')

# 修改密碼
def password(request, user_id):
    user = User.objects.get(id=user_id)
    if not user.username.startswith(request.user.username):
        return redirect("/")
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.set_password(request.POST['password'])
            user.save()
            return redirect('/teacher/student/list/')
    else:
        form = PasswordForm()
        user = User.objects.get(id=user_id)

    return render(request, 'form.html',{'form': form, 'user':user})

# 修改暱稱
def nickname(request, user_id):
    user = User.objects.get(id=user_id)
    if not user.username.startswith(request.user.username):
        return redirect("/")
    if request.method == 'POST':
        form = NicknameForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.first_name =form.cleaned_data['first_name']
            user.save()
            return redirect('/teacher/student/list/')
    else:
        user = User.objects.get(id=user_id)
        form = NicknameForm(instance=user)
    return render(request, 'form.html',{'form': form})
	
class GroupUpdate(UpdateView):
    model = Classroom
    form_class = GroupForm	
    template_name = 'form.html'
    def get_success_url(self):
        succ_url =  '/student/group/'+str(self.kwargs['pk'])
        return succ_url
			
    def form_valid(self, form):
        classroom = Classroom.objects.get(id=self.kwargs['pk'])
        if is_teacher(self.request.user, classroom.id) or is_assistant(self.request.user, classroom.id):
            reduce = classroom.group_number - form.cleaned_data['group_number']
            if reduce > 0:
                for i in range(reduce):
                    StudentGroup.objects.filter(group_id=classroom.group_number-i).delete()
            form.save()
        return HttpResponseRedirect(self.get_success_url())
			
class GroupUpdate2(UpdateView):
    model = Classroom
    form_class = GroupForm2	
    template_name = 'form.html'
    def get_success_url(self):
        succ_url =  '/student/group/'+str(self.kwargs['pk'])
        return succ_url
			
    def form_valid(self, form):
        classroom = Classroom.objects.get(id=self.kwargs['pk'])
        if is_teacher(self.request.user, classroom.id) or is_assistant(self.request.user, classroom.id):
            form.save()
        return HttpResponseRedirect(self.get_success_url())
			
# 分組
def make(request, classroom_id, action):
        classroom = Classroom.objects.get(id=classroom_id)
        if is_teacher(request.user, classroom.id) or is_assistant(request.user, classroom.id):
            if action == 1:            
                classroom.group_open = True   
            else : 
                classroom.group_open = False
            classroom.save()      
        return redirect("/student/group/"+str(classroom.id))