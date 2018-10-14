from django import forms
from account.models import *
from teacher.models import *
from student.models import *

#上傳檔案
class UploadFileForm(forms.Form):
    file = forms.FileField()
	
# 新增一個分組表單
class GroupForm(forms.ModelForm):
        class Meta:
           model = Classroom
           fields = ['group_number']
        
        def __init__(self, *args, **kwargs):
            super(GroupForm, self).__init__(*args, **kwargs)
            self.fields['group_number'].label = "分組數目"	

# 新增一個分組表單
class GroupForm2(forms.ModelForm):
        class Meta:
           model = Classroom
           fields = ['group_size']
        
        def __init__(self, *args, **kwargs):
            super(GroupForm2, self).__init__(*args, **kwargs)
            self.fields['group_size'].label = "小組人數"				