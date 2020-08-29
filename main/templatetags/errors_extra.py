from django import template

register = template.Library()

@register.filter(name="find")
def find(value,arg):
    found=False
    for error in value:
        if error.error_message == arg:
            found=True
        
    return found

 