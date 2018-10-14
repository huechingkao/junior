from django import template
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

register = template.Library()

@register.filter(takes_context=True)
def realname(user_id):
    try: 
        user = User.objects.get(id=user_id)
        return user.first_name
    except :
        pass
    return ""
	
@register.filter(name='has_group') 
def has_group(user, group_name):
    try:
        group =  Group.objects.get(name=group_name) 
    except ObjectDoesNotExist:
        group = None
    return group in user.groups.all()