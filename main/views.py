from . import models, forms
from django.core.mail import send_mail
from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.utils.text import slugify
import re


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

class SignUpView(FormView):

    template_name="signup.html"
    form_class=forms.UserCreationForm
    
    def get_success_url(self):
        redirect_to=reverse_lazy('login')
        return redirect_to
    
    def form_valid(self,form):
        response=super().form_valid(form)
        form.save()
        email=form.cleaned_data.get("email")
        raw_password=form.cleaned_data.get("password1")
        user=authenticate(email=email,password=raw_password)
        login(self.request,user)
        form.send_mail()
        messages.info(self.request,"You signed up successfully.")
        return response

@login_required
def client_dashboard(request):

    clients=models.client.objects.filter(users=request.user)

    context={"clients":clients}

    return render(request,"client_dashboard.html",context)

class createClientView(TemplateView):
    template_name="new_client.html"

    def get(self,request,*args,**kwargs):
        data=dict()
        new_client_form=forms.NewClientForm()
        context_object={'form':new_client_form}
        data['html_form']=render_to_string('new_client.html',context_object,request=request)
        return JsonResponse(data)

    def post(self,request,*args,**kwargs):
        data=dict()
        name=request.POST.get('name')
        number=request.POST.get('number')
        users=request.POST.get('users')
        slug=slugify(name)

        instance=models.client.objects.create(name=name,number=number,slug=slug)
        instance.users.set(users)
        user=request.user

        clients=models.client.objects.filter(users=user)
        context={"clients":clients}

        data['clients']=render_to_string('client_list.html',{'clients':context['clients']},request=request)
        
        data['form_is_valid']=True
        data['html_form']=render_to_string('new_client.html',context,request=request)

        return JsonResponse(data)

class CreateEngagement(TemplateView):
    template_name="new_engagement.html"

    def get(self,request, slug, *args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        new_engagement_form=forms.NewEngagementForm()
        context_object={'form':new_engagement_form, "client":client}
        data['html_form']=render_to_string('new_engagement.html',context_object,request=request)
        return JsonResponse(data)

    def post(self,request,slug,*args,**kwargs):
        data=dict()
        name=request.POST.get('name')
        date=request.POST.get('date')
        date_pattern=re.compile("[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]")

        if date_pattern.match(date):
            pass
        else:
            date=(date[-4:]+"-"+date[0-2]+"-"+date[3-5])
        print(date)
        

        slug_name=slugify(name)

        client=models.client.objects.get(slug=slug)

        instance=models.engagement.objects.create(name=name,date=date,slug=slug_name, client=client)



        engagements=models.engagement.objects.filter(client=client)
        context={"engagements":engagements,"client":client}

        data['engagements']=render_to_string('engagement_list.html',{'engagements':context['engagements']},request=request)
        
        data['form_is_valid']=True
        data['html_form']=render_to_string('new_engagement.html',context,request=request)

        return JsonResponse(data)    


@login_required
def client_page(request,slug):
    client=models.client.objects.get(slug=slug)
    engagements=models.engagement.objects.filter(client=client)
    context={"client":client,"engagements":engagements}

    return render(request,"client_page.html",context)

