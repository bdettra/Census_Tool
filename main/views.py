from . import models, forms
from django.core.mail import send_mail
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.views.generic.edit import FormView, DeleteView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.utils.text import slugify
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
import pandas as pd
from . import plugin
from dateutil.relativedelta import relativedelta
from django.forms import modelformset_factory
from django.forms import formset_factory
from django.db.models import Avg, StdDev
import xlwt
from rest_framework import generics
from . import serializer
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


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

'''class SignUpView(FormView):
    Renders the sign up page.

    template_name="signup.html"
    form_class=forms.UserCreationForm
    
    def get_success_url(self):
        redirect_to=reverse_lazy('home')
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
        return response'''


@login_required
def client_dashboard(request):
    '''Renders the client dashboard page'''

    clients=models.client.objects.filter(users=request.user)

    context={"clients":clients}

    return render(request,"client_dashboard.html",context)


class createClientView(LoginRequiredMixin,TemplateView):
    '''Renders the create client modal'''

    template_name="new_client.html"
    login_url='/accounts/login/'

    def get(self,request,*args,**kwargs):
        data=dict()
        new_client_form=forms.NewClientForm()
        context_object={'form':new_client_form}
        data['html_form']=render_to_string('new_client.html',context_object,request=request)
        return JsonResponse(data)

    def post(self,request,*args,**kwargs):
        data=dict()
        form=forms.NewClientForm(request.POST)
        data['form_is_valid']=False
        if form.is_valid():
            name=request.POST.get('name')
            number=request.POST.get('number')
            users=request.POST.get('users')
            primary_user=request.user
            slug=slugify(name)
            instance=models.client.objects.create(name=name,number=number,slug=slug,primary_user=primary_user)
            instance.users.set(users)
            data['form_is_valid']=True

        user=request.user

        clients=models.client.objects.filter(users=user)
        context={"clients":clients,"form":form}
        

        #data['clients']=render_to_string('client_list.html',{'clients':context['clients'],},request=request)
        data['html_form']=render_to_string('new_client.html',context,request=request)
        
        return JsonResponse(data)


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Deletes a client from the database'''

    login_url='/accounts/login/'

    model=models.client
    slug_url_kwarg="slug"
    success_url=reverse_lazy('client_dashboard')
    template_name="client_dashboard.html"
    raise_exception = True

    
    def test_func(self):
        self.object=self.get_object()
        return self.request.user ==self.object.primary_user

class EngagementDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Deletes an engagement from the database'''
    model=models.engagement
    slug_url_kwarg="Eslug"
    template_name="client_page.html"
    login_url="/accounts/login/"

    def get_object(self,queryset=None):
        client_slug=self.kwargs["slug"]
        engagement_slug=self.kwargs["Eslug"]

        client = models.client.objects.get(slug=client_slug)
        obj = models.engagement.objects.get(client=client, slug=engagement_slug)

        return obj


    def test_func(self):
        
        self.object=self.get_object()
        print(self.object)
        
        return self.request.user == self.object.primary_user

    def get_success_url(self):
        client=self.object.client
        client_slug=client.slug

        return reverse_lazy('client_page',kwargs={"slug":client_slug})




class CreateEngagement(TemplateView):
    '''Creates a new engagement and adds it to the engagement table'''

    template_name="new_engagement.html"

    def get(self,request, slug, *args,**kwargs):
        data=dict()
        client_object=models.client.objects.get(slug=slug)
        new_engagement_form=forms.NewEngagementForm(client=client_object)
        print(new_engagement_form)
        context_object={'form':new_engagement_form, "client":client_object}
        data['html_form']=render_to_string('new_engagement.html',context_object,request=request)
        return JsonResponse(data)

    def post(self,request,slug,*args,**kwargs):
        data=dict()
        client_object=models.client.objects.get(slug=slug)
        form=forms.NewEngagementForm(client_object,request.POST)
        print(form.client)
        data['form_is_valid']=False
        if form.is_valid():
            name=request.POST.get('name')
            date=request.POST.get('date')
            #Creating a regular expression pattern in order to get the date in the correct format.
            date_pattern=re.compile("[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]")

            if date_pattern.match(date):
                pass
            else:
                date=(date[-4:]+"-"+date[0:2]+"-"+date[3:5])
        

            #Determining if there is a previous engagement with eligiblity rules to rollforward
            #and then getting that ruleset.
            previous_engagements= client_object.engagement_set.all()
            if previous_engagements:
                most_recent_engagement=client_object.engagement_set.latest('date')
                most_recent_eligibility_rules=most_recent_engagement.eligibility_rules_set.get()

            #Slugify the name data and then create a new engagement.
            slug_name=slugify(name) 
            primary_user=request.user
            instance=models.engagement.objects.create(name=name,date=date,slug=slug_name, client=client_object,primary_user=primary_user)
            data['form_is_valid']=True

            #Getting all engagements under this client.
            engagements=models.engagement.objects.filter(client=client_object)
        
            #Rolling forward previous eligiblity rules or creating ruleset for new client
            #with new engagements.
            if previous_engagements:
                models.eligibility_rules.objects.create(engagement=instance, age=most_recent_eligibility_rules.age, service_hours=most_recent_eligibility_rules.service_hours,
                service_days=most_recent_eligibility_rules.service_days, service_months= most_recent_eligibility_rules.service_months,
                service_years=most_recent_eligibility_rules.service_years, excluded_employees=most_recent_eligibility_rules.excluded_employees,
                entry_date=most_recent_eligibility_rules.entry_date,)
            else:
                models.eligibility_rules.objects.create(engagement=instance)
        else:
            engagements=models.engagement.objects.filter(client=client_object)
        
        context={"engagements":engagements,"client":client_object,"form":form}

        #data['engagements']=render_to_string('engagement_list.html',{'engagements':context['engagements'], 'client': context['client']},request=request)
        
        data['html_form']=render_to_string('new_engagement.html',context,request=request)

        return JsonResponse(data) 

class EditEngagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    login_url="/accounts/login/"

    def test_func(self):
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)
        primary_user = client.primary_user

        print(primary_user.email)
        return self.request.user == primary_user


    template_name="edit_engagement.html"

    def get(self,request,slug, Eslug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement = models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants = models.participant.objects.filter(engagement=engagement)
        form=forms.EditEngagementForm(instance=engagement,engagement=engagement)

        context_object={"client":client,"engagement":engagement,"form":form,"participants":participants}
        data['html_form']=render_to_string('edit_engagement.html',context_object,request=request)
        
        return JsonResponse(data)


    def post(self,request,slug,Eslug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement = models.engagement.objects.get(slug=Eslug)
        form=forms.EditEngagementForm(engagement,request.POST)
        data['form_is_valid']=False
        if form.is_valid():
            form.save()
            engagement=models.engagement.objects.get(slug=slugify(form.cleaned_data.get("name")))
            data['form_is_valid']=True
        data['engagement_slug']=engagement.slug
        data['client_slug']=client.slug
        eligibility_rules=get_object_or_404(models.eligibility_rules,engagement=engagement)
        participants = models.participant.objects.filter(engagement=engagement)
        
        context_object={"client":client,"form":form,"engagement":engagement,"participants":participants}
        data['html_form']=render_to_string('edit_engagement.html',context_object,request=request)
        print("WORKING")
        return JsonResponse(data)  


class ViewEngagementProfile(LoginRequiredMixin, TemplateView):

    login_url="/accounts/login/"

    def test_func(self):
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)
        primary_user = client.primary_user

        print(primary_user.email)
        return self.request.user == primary_user


    template_name="view_engagement_profile.html"

    def get(self,request,slug,Eslug,*args,**kwargs):
        data=dict()
        client = models.client.objects.get(slug=slug)
        engagement = models.engagement.objects.get(client=client,slug=Eslug)
        client_contacts = models.client_contact.objects.filter(engagement=engagement)


        context_object={"client":client,"engagement":engagement,"client_contacts":client_contacts}
        data['html_form']=render_to_string('view_engagement_profile.html',context_object,request=request)
        
        return JsonResponse(data)
    



'''@login_required
def client_page(request,slug):
    client=models.client.objects.get(slug=slug)
    engagements=models.engagement.objects.filter(client=client)
    context={"client":client,"engagements":engagements}

    return render(request,"client_page.html",context)'''

class ClientPageView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    login_url = "/accounts/login"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request,slug):
        client=models.client.objects.get(slug=slug)
        engagements=models.engagement.objects.filter(client=client)
        context={"client":client,"engagements":engagements}

        return render(request,"client_page.html",context)
    

class EngagementView(UserPassesTestMixin, TemplateView):

    template_name="engagement_page.html"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test



    def get(self,request, slug, Eslug, *args,**kwargs):

        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants = models.participant.objects.filter(engagement=engagement)
        census_form=forms.CensusFileForm()

        errors=False
        for participant in participants:
            if len(participant.error_set.all())>0:
                errors=True
                break

        context={'census_form':census_form,'client':client,'engagement':engagement,"eligibility_rules":eligibility_rules,"participants":participants,"errors":errors}

        return render(request,"engagement_page.html",context=context)
        


class EditEligibility(UserPassesTestMixin, TemplateView):
    template_name="edit_eligibility.html"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request, slug, Eslug, *args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligiblity_rules=models.eligibility_rules.objects.get(engagement=engagement)
        edit_eligibility_form=forms.EligibilityForm(instance=eligiblity_rules)
        context_object={'form':edit_eligibility_form, "client":client, "engagement":engagement}
        data['html_form']=render_to_string('edit_eligibility.html',context_object,request=request)
        return JsonResponse(data)

    def post(self,request,slug, Eslug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)

        form=forms.EligibilityForm(request.POST)

        if form.is_valid():
            form.save(engagement)
        
        client=models.client.objects.get(slug=slug)
        eligibility_rules=get_object_or_404(models.eligibility_rules,engagement=engagement)
        
        participants=models.participant.objects.filter(engagement=engagement)
        
        if len(participants)>0:
        
            for participant in participants:
                plugin.eligibility(participant,eligibility_rules,engagement)
                plugin.participating(participant)
                plugin.effective_deferral(participant)
                
        

        
                participant.save()
                if participant.eligible == False and participant.participating==True:
                    if participant.DOT!=None:
                        if participant.DOT > (engagement.date - relativedelta(years=1)) and participant.DOT < engagement.date:
                            pass
                        else:
                            messages.error(self.request,participant.first_name + " " + participant.last_name + " " + "is a ineligible employee who is participating. You should investigate further.")

                    else:
                        messages.error(self.request,participant.first_name + " " + participant.last_name + " " + "is a ineligible employee who is participating. You should investigate further.")

                if participant.excluded == True and participant.participating == True:
                    messages.error(self.request, participant.first_name + " " + participant.last_name + " " + " is an excluded employee who is participating. You should investigate further.")
        
        participants=models.participant.objects.filter(engagement=engagement)



        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants}

        data['engagements']=render_to_string('eligibility_rules.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client'],"eligibility_rules":context["eligibility_rules"]},request=request)
        
        data['form_is_valid']=True
        data['html_form']=render_to_string('edit_eligibility.html',context,request=request)
        
        return JsonResponse(data)


        
class KeyEmployee(UserPassesTestMixin, TemplateView):
    template_name="key_employee.html"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request, slug, Eslug, *args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligiblity_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants=models.participant.objects.filter(engagement=engagement)
        '''
        key_employee_form=forms.KeyEmployeeSelectForm(engagement=engagement)
        '''
        
        FormSet = modelformset_factory(models.participant, form=forms.KeyEmployee,extra=0)
        formset=FormSet(queryset=participants)
        '''
        FormSet=formset_factory(forms.KeyEmployeeSelectForm(engagement=engagement))
        formset=formset_factory(FormSet)
        '''
        context_object={'formset':formset, "client":client, "engagement":engagement}
        data['html_form']=render_to_string('key_employee.html',context_object,request=request)
        return JsonResponse(data)

    def post(self,request,slug, Eslug,*args,**kwargs):
        data=dict()
        FormSet = modelformset_factory(models.participant, form=forms.KeyEmployee,extra=0)
        formset=FormSet(request.POST,request.FILES)
        instance=formset.save()

        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        participants=models.participant.objects.filter(engagement=engagement)
      


        eligibility_rules=get_object_or_404(models.eligibility_rules,engagement=engagement)
        errors=False
        for participant in participants:
            if len(participant.error_set.all()) > 0:
                print("Numebr of Errors:" + str(len(participant.error_set.all())))
                errors=True
                break


        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants,"errors":errors}

        #data['engagements']=render_to_string('census_list.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client'],'errors':context['errors']},request=request)
        
        data['form_is_valid']=True
        data['html_form']=render_to_string('key_employee.html',context,request=request)

        return JsonResponse(data) 

class CensusStatistics(UserPassesTestMixin, TemplateView):

    template_name="census_statistics.html"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request,slug, Eslug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants=models.participant.objects.filter(engagement=engagement)
        number_of_employees=models.participant.objects.filter(engagement=engagement).count()
        contributing_employees=models.participant.objects.filter(engagement=engagement,participating=True).count()
        non_contributing_employees=models.participant.objects.filter(engagement=engagement,participating=False).count()
        eligible=models.participant.objects.filter(engagement=engagement,eligible=True).count()
        ineligible=models.participant.objects.filter(engagement=engagement,eligible=False).count()
        average_gross_wages=participants.aggregate(Avg("gross_wages"))
        employees_terminated=participants.exclude(DOT=None).count()
        key_employees=participants.filter(key_employee=True).count()
        standard_dev_wages=participants.aggregate(StdDev("gross_wages"))
        top_earners=participants.order_by('-gross_wages')
        top_earner=top_earners[0]
        lowest_earner=top_earners[(len(top_earners)-1)]
        number_selections=participants.filter(selection=True).count()
        number_of_cont_selections=participants.filter(selection=True,contributing=True).count()
        number_of_non_cont_selections=participants.filter(selection=True,contributing=False).count()
        number_of_errors=models.error.objects.filter(participant__id__in=participants).count()

        context_object={"number_of_errors":number_of_errors,"number_of_non_cont_selections":number_of_non_cont_selections,"number_of_cont_selections":number_of_cont_selections,"number_of_selections":number_selections,"lowest_earner":lowest_earner,"top_earner":top_earner,"standard_dev_wages":standard_dev_wages,"key_employees":key_employees,"employees_terminated":employees_terminated,"average_gross_wages":average_gross_wages,"ineligible":ineligible,"eligible":eligible,"non_contributing_employees":non_contributing_employees,"contributing_employees":contributing_employees,"number_of_employees":number_of_employees,"participants":participants, "client":client, "engagement":engagement,"eligibility_rules":eligibility_rules,}
        data['html_form']=render_to_string('census_statistics.html',context_object,request=request)
        return JsonResponse(data)


class MakeSelections(UserPassesTestMixin, TemplateView):

    template_name="make_selections.html"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request,slug, Eslug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants=models.participant.objects.filter(engagement=engagement)

        context_object={"client":client,"engagement":engagement,"eligibility_rules":eligibility_rules,"participants":participants}
        data['html_form']=render_to_string('make_selections.html',context_object,request=request)
        
        return JsonResponse(data)

    def post(self,request,slug, Eslug,*args,**kwargs):
        print("working")
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)

        x = plugin.generate_selections(engagement)
        print(x)

        #print(plugin.generate_selections_version_2(engagement,client))
        participants=models.participant.objects.filter(engagement=engagement)
        errors=False
        for participant in participants:
            if len(participant.error_set.all()) > 0:
                errors=True
                break

        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants,"errors":errors}

        #data['engagements']=render_to_string('census_list.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client']},request=request)
        
        data['form_is_valid']=True
        data['html_form']=render_to_string('make_selections.html',context,request=request)
    
        return JsonResponse(data) 

class EditSelections(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    login_url="/accounts/login/"

    def test_func(self):
        client_slug=self.kwargs.pop("slug")
        engagement_slug=self.kwargs.pop("Eslug")

        client = models.client.objects.get(slug=client_slug)
        engagement= models.engagement.objects.get(slug=engagement_slug)

        return self.request.user == engagement.primary_user   

    def get(self, request, slug, Eslug, *args, **kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants=models.participant.objects.filter(engagement=engagement)

        FormSet = modelformset_factory(models.participant, form = forms.EditSelection, extra=0)
        formset=FormSet(queryset=participants)

        context_object={'formset':formset,"client":client,"engagement":engagement,"eligibility_rules":eligibility_rules,"participants":participants}
        data['html_form']=render_to_string("edit_selections.html",context_object,request=request)

        return JsonResponse(data)

    def post(self,request, slug, Eslug, *args, **kwargs):
        data=dict()
        FormSet = modelformset_factory(models.participant, form=forms.EditSelection,extra=0)
        formset=FormSet(request.POST,request.FILES)
        instance=formset.save()

        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        participants=models.participant.objects.filter(engagement=engagement)
      


        eligibility_rules=get_object_or_404(models.eligibility_rules,engagement=engagement)
        


        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants,}

        #data['engagements']=render_to_string('census_list.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client'],'errors':context['errors']},request=request)
        
        data['form_is_valid']=True
        data['html_form']=render_to_string('edit_selections.html',context,request=request)

        return JsonResponse(data) 


class EditClient(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    login_url="/accounts/login/"

    def test_func(self):
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)
        primary_user = client.primary_user

        print(primary_user.email)
        return self.request.user == primary_user


    template_name="edit_client.html"

    def get(self,request,slug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        form=forms.EditClientForm(instance=client,client=client)

        context_object={"client":client,"form":form}
        data['html_form']=render_to_string('edit_client.html',context_object,request=request)
        
        return JsonResponse(data)

    def post(self,request,slug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        form=forms.EditClientForm(client,request.POST)
        data['form_is_valid']=False
        if form.is_valid():
            form.save()
            client=models.client.objects.get(slug=slugify(form.cleaned_data.get("name")))
            data['form_is_valid']=True
        data['slug']=client.slug
    
        
        engagements=models.engagement.objects.filter(client=client)
        context_object={"client":client,"form":form,"engagements":engagements}
        data['html_form']=render_to_string('edit_client.html',context_object,request=request)
        
        return JsonResponse(data)

class EditPrimaryClientUser(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    login_url="/accounts/login/"

    def test_func(self):
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)
        primary_user = client.primary_user

        print(primary_user.email)
        return self.request.user == primary_user


    template_name="edit_client_primary_user.html"

    def get(self,request,slug,*args,**kwargs):
        print("Working")
        data=dict()
        client=models.client.objects.get(slug=slug)
        form=forms.EditClientUserForm(instance=client,client=client)

        context_object={"client":client,"form":form}
        data['html_form']=render_to_string('edit_client_primary_user.html',context_object,request=request)
        
        return JsonResponse(data)

    def post(self,request,slug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        form=forms.EditClientUserForm(client,request.POST)
        data['form_is_valid']=False
        if form.is_valid():
            form.save()
            data['form_is_valid']=True
        data['slug']=client.slug
        client=models.client.objects.get(slug=slug)
    
        
        engagements=models.engagement.objects.filter(client=client)
        context_object={"client":client,"form":form,"engagements":engagements}
        data['html_form']=render_to_string('edit_client_primary_user.html',context_object,request=request)
        
        return JsonResponse(data)

        


class ViewSelections(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name="view_selections.html"

    login_url = "/accounts/login"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request,slug,Eslug):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants=models.participant.objects.filter(engagement=engagement)
        selections=participants.filter(selection=True).order_by("-contributing")

        context_object={"client":client,"engagement":engagement,"eligibility_rules":eligibility_rules,"participants":participants,"selections":selections}
        data['html_form']=render_to_string('view_selections.html',context_object,request=request)
        
        return JsonResponse(data)

class UploadCensus(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name="upload_census.html"

    login_url="/accounts/login/"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request,slug,Eslug):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        form=forms.CensusFileForm()

        context_object={"client":client,"form":form,"engagement":engagement}
        data['html_form']=render_to_string("upload_census.html",context_object,request=request)

        return JsonResponse(data)

    def post(self,request,slug,Eslug,*args,**kwargs):
        #Defining our client, engagement, eligiblity rules, census forms and participants objects
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        form=forms.CensusFileForm(request.POST, request.FILES)
        participants=models.participant.objects.filter(engagement=engagement)

        #Deleting existing participants in the engagement everytime a new census is uploaded.
        for instance in participants:
            instance.delete()
        
        #Redefining our particiapnts queryset after participants have been deleted
        participants=models.participant.objects.filter(engagement=engagement)

        #Creating out context object
        context={"client":client,"engagement":engagement,"eligibility_rules":eligibility_rules,"form":forms.CensusFileForm,"participants":participants}

        #Creating a previous year engagement variable and assigning it as false.
        py_engagement=False

        #Creating a previous year participants variable and assigning it as none.
        py_participants=None
        
        #Getting a queryset of engagements with a date before the current engagement date
        py_engagements=models.engagement.objects.filter(client=client,date__lt=engagement.date)

        #If py_engagement variable is more than 0 the previous year engagement is engagement with the latest date.
        if len(py_engagements) > 0 :
            py_engagement=py_engagements.latest('date')
            py_participants=models.participant.objects.filter(engagement=py_engagement)

        #Reading in the excel file that is uploaded as a pandas table
        try:
            data=pd.read_excel(request.FILES['filename'])
        except:
            messages.error(self.request,"The file that imported is not in excel format")
            return render(request,"engagement_page.html",context=context)
        
        #Creating a columns variable from our dataset 
        columns=data.columns
        location_dict=plugin.location_dict(columns)

    
        location_dict=plugin.location_dict(columns)
        found_columns=location_dict.keys()

        #These are the defined census columns that will show up in the application
        application_columns = ["First Name","Last Name","SSN","DOB","DOH","DOT","DORH",
                                "Excluded","Hours Worked","Gross Wages","Eligible Wages",
                                "EE pre-tax","ER pre-tax","EE Roth","ER Roth","EE Catch-up","ER Catch-up"]
        
        #If there is a column in the application census that is not in the excel file we are creating a column in dolumn dict that is equal to none.
        for i in application_columns:
            if i in found_columns:
                pass
            else:
                location_dict[i]=None


        #Going through columns in the location dict that are required in order to process the census
        #if any of these columns were not ofund in the excel file the census will not process.
        if location_dict["First Name"]==None:
            messages.error(self.request,"The census is missing a First Name column. Stopped processing")
            return render(request,"engagement_page.html",context=context)
        elif location_dict["Last Name"]==None:
            messages.error(self.request,"The census is missing a Last Name column. Stopped processing")
            return render(request,"engagement_page.html",context=context)
        elif location_dict["SSN"]==None:
            messages.error(self.request,"The census is missing a SSN column. Stopped processing")
            return render(request,"engagement_page.html",context=context)
        elif location_dict["DOB"]==None:
            messages.error(self.request,"The census is missing a DOB column. Stopped processing")
            return render(request,"engagement_page.html",context=context)
        elif location_dict["DOH"]==None:
            messages.error(self.request,"The census is missing a DOH column. Stopped processing")
            return render(request,"engagement_page.html",context=context)
        elif location_dict["DOT"]==None:
            messages.error(self.request,"The census is missing a DOT column. Stopped processing")
            return render(request,"engagement_page.html",context=context)
        elif location_dict["DORH"]==None:
            messages.error(self.request,"The census is missing a DORH column. Stopped processing")
            return render(request,"engagement_page.html",context=context)
        
        #Iterating through each row and data point in the census.
        for i,x in data.iterrows():

            '''If this row's SSN is missing return an error and stop processing the census.
               If it is found extract the SSN, make sure that it is a string that is in the SSN format in 
               order to make sure it isn't another string data point. If it matches the SSN pattern
               then continue processing'''

            if pd.isnull(data.iloc[i,location_dict['SSN']])==False:
                ssn = str(data.iloc[i,location_dict['SSN']])
                full_ssn_pattern=re.compile('[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]')
                partial_snn_pattern=re.compile('[0-9][0-9][0-9][0-9]')
                if full_ssn_pattern.fullmatch(ssn) != None or partial_snn_pattern.fullmatch(ssn) != None:
                    participant, created=models.participant.objects.update_or_create(SSN=data.iloc[i,location_dict['SSN']],engagement=engagement)
                else:
                    messages.error(self.request,"The SSN in row " + str(i+1) + " is not in the correct format. Census stopped processing at that employee.")
                    return render(request,"engagement_page.html",context=context)
            else:
                messages.error(self.request,"One of the employees is missing a SSN value. Census stopped processing at that employee.")
                return render(request,"engagement_page.html",context=context)


            '''If this row's First Name data point is null or missing stop processing the census and return an error.
            If it isn't null continue processing the census.'''
            
            if pd.isnull(data.iloc[i,location_dict['First Name']])==False:
                participant.first_name=data.iloc[i,location_dict['First Name']]
                participant.save()
            else:
                error=models.error.objects.create(participant=participant,error_message="First name data is missing")
                error.save()
                #messages.error(self.request,"One of the participants is missing a First Name Value")
                
            
            if pd.isnull(data.iloc[i,location_dict['Last Name']])==False:
                participant.last_name=data.iloc[i,location_dict['Last Name']]
                participant.save()
            else:
                error=models.error.objects.create(participant=participant,error_message="Last name data is missing")
                error.save()
                #messages.error(self.request,"One of the participants is missing a Last Name Value")

            if pd.isnull(data.iloc[i,location_dict['DOB']])==False:
                try:
                    data.iloc[i,location_dict['DOB']]=pd.to_datetime(data.iloc[i,location_dict['DOB']],format="%m/%d/%y")
                except:
                    messages.error(self.request,"There is an invalid data point in the DOB column at row " + str(i+1) +".")
                    return render(request,"engagement_page.html",context=context)

                participant.DOB=data.iloc[i,location_dict['DOB']].date()
            else:
                error=models.error.objects.create(participant=participant,error_message="DOB data is missing")
                error.save()
                messages.error(self.request,participant.first_name +" " + participant.last_name + "is missing a DOB value. Census stopped processing at that employee.")
                return render(request,"engagement_page.html",context=context)

            if pd.isnull(data.iloc[i,location_dict['DOH']])==False:
                try:
                    data.iloc[i,location_dict['DOH']]=pd.to_datetime(data.iloc[i,location_dict['DOH']],format="%m/%d/%y")
                except:
                    messages.error(self.request,"There is an invalid data point in the DOH column at row " + str(i+1) +".")
                    return render(request,"engagement_page.html",context=context)
                participant.DOH=data.iloc[i,location_dict['DOH']].date()
            else:
                error=models.error.objects.create(participant=participant,error_message="DOH data is missing")
                messages.error(self.request,participant.first_name +" " + participant.last_name + "is missing a DOH value. Census stopped processing at that employee.")
                return render(request,"engagement_page.html",context=context)

            if pd.isnull(data.iloc[i,location_dict['DOT']])==False:
                try:
                    data.iloc[i,location_dict['DOT']]=pd.to_datetime(data.iloc[i,location_dict['DOT']],format="%m/%d/%y")
                except:
                    messages.error(self.request,"There is an invalid data point in the DOT column at row " + str(i+1) +".")
                    return render(request,"engagement_page.html",context=context)

                participant.DOT=data.iloc[i,location_dict['DOT']].date()
                participant.save()
                if participant.DOT < (engagement.date - relativedelta(years=1)):
                    error=models.error.objects.create(participant=participant,error_message="DOT is before engagement year")
                    #messages.error(self.request,participant.first_name + " " + participant.last_name + " " + "has a date of termination that is before the engagement year. You should investigate further.")

            if pd.isnull(data.iloc[i,location_dict['DORH']])==False:
                try:
                    data.iloc[i,location_dict['DORH']]=pd.to_datetime(data.iloc[i,location_dict['DORH']],format="%m/%d/%y")
                except:
                    messages.error(self.request,"There is an invalid data point in the DOT column at row " + str(i+1) +".")
                    return render(request,"engagement_page.html",context=context)

                participant.DORH=data.iloc[i,location_dict['DORH']].date()

            if location_dict["Excluded"]==None:
                participant.excluded=False

            elif pd.isnull(data.iloc[i,location_dict["Excluded"]])==False:
                excluded=data.iloc[i,location_dict['Excluded']]

                no_values=[None,"No",'no']

                yes_values=["Yes","yes"]
                
                if data.iloc[i,location_dict['Excluded']] in no_values:
                    participant.excluded=False
                elif data.iloc[i,location_dict['Excluded']] in yes_values:
                    participant.excluded=True
                else:
                    messages.error(self.request,"There is an invalid data point in the Excluded colmun at row " + str(i+1) + ". Values in this column must be Yes/No. Census stopped processing on this row.")
                    return render(request,"engagement_page.html",context=context)
            else:
                participant.excluded=False

            if location_dict["Hours Worked"]==None:
                participant.hours_worked=0

            elif pd.isnull(data.iloc[i,location_dict['Hours Worked']])==False:
                try:
                    data.iloc[i,location_dict['Hours Worked']]=pd.to_numeric(data.iloc[i,location_dict['Hours Worked']])
                except:
                    messages.error(self.request, "There is an invalid data point in the Hours Worked column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)
                    
                participant.hours_worked=data.iloc[i,location_dict['Hours Worked']]
            else:
                error=models.error.objects.create(participant=participant,error_message="Hours worked data is missing")
                #messages.error(self.request,"One of the participants is missing an 'Hours Worked' value")


            if location_dict["Gross Wages"]==None:
                participant.gross_wages=0

            elif pd.isnull(data.iloc[i,location_dict['Gross Wages']])==False:
                try:
                    data.iloc[i,location_dict['Gross Wages']]=pd.to_numeric(data.iloc[i,location_dict['Gross Wages']])
                except:
                    messages.error(self.request, "There is an invalid data point in the Gross Wages column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)

                participant.gross_wages=data.iloc[i,location_dict['Gross Wages']]
            else:
                participant.gross_wages=0
            
            
            if location_dict["Eligible Wages"]==None:
                    participant.eligible_wages=0

            elif pd.isnull(data.iloc[i,location_dict['Eligible Wages']])==False:
                try:
                    data.iloc[i,location_dict['Eligible Wages']]=pd.to_numeric(data.iloc[i,location_dict['Eligible Wages']])
                except:
                    messages.error(self.request, "There is an invalid data point in the Eligible Wages column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)
                participant.eligible_wages=data.iloc[i,location_dict['Eligible Wages']]

            else:
                participant.eligible_wages=0



            if location_dict["EE pre-tax"]==None:
                participant.EE_pre_tax_amount=0

            elif pd.isnull(data.iloc[i,location_dict['EE pre-tax']])==False:
                try:
                    data.iloc[i,location_dict['EE pre-tax']]=pd.to_numeric(data.iloc[i,location_dict['EE pre-tax']])
                except:
                    messages.error(self.request, "There is an invalid data point in the EE pre-tax column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)
                participant.EE_pre_tax_amount=data.iloc[i,location_dict['EE pre-tax']]

            else:
                participant.EE_pre_tax_amount=0

            if location_dict["ER pre-tax"]==None:
                participant.ER_pre_tax_amount=0    

            elif pd.isnull(data.iloc[i,location_dict['ER pre-tax']])==False:
                try:
                    data.iloc[i,location_dict['ER pre-tax']]=pd.to_numeric(data.iloc[i,location_dict['ER pre-tax']])
                except:
                    messages.error(self.request, "There is an invalid data point in the ER pre-tax column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)
                participant.ER_pre_tax_amount=data.iloc[i,location_dict['ER pre-tax']]

            else:
                participant.ER_pre_tax_amount = 0

            if location_dict['EE Roth']==None:
                participant.EE_roth_amount=0

            elif pd.isnull(data.iloc[i,location_dict['EE Roth']])==False:
                try:
                    data.iloc[i,location_dict['EE Roth']]=pd.to_numeric(data.iloc[i,location_dict['EE Roth']])
                except:
                    messages.error(self.request, "There is an invalid data point in the EE Roth column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)

                participant.EE_roth_amount=data.iloc[i,location_dict['EE Roth']]

            else:
                participant.EE_roth_amount = 0


            if location_dict['ER Roth']==None:
                participant.ER_roth_amount=0

            elif pd.isnull(data.iloc[i,location_dict['ER Roth']])==False:
                try:
                    data.iloc[i,location_dict['ER Roth']]=pd.to_numeric(data.iloc[i,location_dict['ER Roth']])
                except:
                    messages.error(self.request, "There is an invalid data point in the ER Roth column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)

                participant.ER_roth_amount=data.iloc[i,location_dict['ER Roth']]
            
            else:
                participant.ER_roth_amount = 0

            if location_dict['EE Catch-up']==None:
                participant.EE_catch_up=0
            
            elif pd.isnull(data.iloc[i,location_dict['EE Catch-up']])==False:
                try:
                    data.iloc[i,location_dict['EE Catch-up']]=pd.to_numeric(data.iloc[i,location_dict['EE Catch-up']])
                except:
                    messages.error(self.request, "There is an invalid data point in the EE Catch-up column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)
                participant.EE_catch_up=data.iloc[i,location_dict['EE Catch-up']]
            
            else:
                participant.EE_catch_up=0

            if location_dict['ER Catch-up']==None:
                participant.ER_catch_up=0

            elif pd.isnull(data.iloc[i,location_dict['ER Catch-up']])==False:
                try:
                    data.iloc[i,location_dict['ER Catch-up']]=pd.to_numeric(data.iloc[i,location_dict['ER Catch-up']])
                except:
                    messages.error(self.request, "There is an invalid data point in the ER Catch-up column at row " + str(i+1) + ".")
                    return render(request,"engagement_page.html",context=context)
                participant.ER_catch_up=data.iloc[i,location_dict['ER Catch-up']]

            else:
                participant.ER_catch_up=0

            participant.total_EE_deferral= participant.EE_pre_tax_amount + participant.EE_roth_amount + participant.EE_catch_up
            participant.total_ER_deferral= participant.ER_pre_tax_amount + participant.ER_roth_amount + participant.ER_catch_up

            participant.key_employee=False
            participant.save()


            plugin.eligibility(participant,eligibility_rules,engagement)
            plugin.participating(participant)
            plugin.effective_deferral(participant)
            

            if py_engagement != False:
                error_messages=plugin.previous_year_check(participant,py_engagement)
                for key, value in error_messages.items():
                    if value != False:
                        messages.error(self.request,value)

            #Checking for Contribution & Wage Errors
            plugin.contribution_check(participant,engagement, location_dict)
            plugin.eligible_wages_check(participant,engagement)

            
            


            participant.save()
            if participant.eligible == False and participant.participating==True:
                if participant.DOT!=None:
                    if participant.DOT > (engagement.date - relativedelta(years=1)) and participant.DOT < engagement.date:
                        pass
                    else:
                        models.error.objects.create(participant=participant,error_message="Employee is ineligible and is participating")
                        participant.save()
                        #messages.error(self.request,participant.first_name + " " + participant.last_name + " " + "is a ineligible employee who is participating. You should investigate further.")

                else:
                    models.error.objects.create(participant=participant,error_message="Employee is ineligible and is participating")
                    #messages.error(self.request,participant.first_name + " " + participant.last_name + " " + "is a ineligible employee who is participating. You should investigate further.")

            if participant.excluded == True and participant.participating == True:
                messages.error(self.request, participant.first_name + " " + participant.last_name + " " + " is an excluded employee who is participating. You should investigate further.")

            

        participants=models.participant.objects.filter(engagement=engagement)

        errors=False
        for participant in participants:
            if len(participant.error_set.all()) > 0:
                errors=True
                break
        


        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants,"errors":errors,}

        return HttpResponseRedirect(reverse('engagement_page',args=(slug, Eslug)))

class AddClientContact(LoginRequiredMixin, TemplateView):

    template_name="add_client_contact.html"

    login_url = "/accounts/login"

    '''
    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test  
    '''

    def get(self,request,slug, Eslug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement = models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants = models.participant.objects.filter(engagement=engagement)
        form=forms.NewClientContact(engagement=engagement)

        context_object={"client":client,"engagement":engagement,"form":form,"participants":participants,"eligiblity_rules":eligibility_rules}
        data['html_form']=render_to_string('add_client_contact.html',context_object,request=request)
        
        print("Worked")
        return JsonResponse(data)


    def post(self,request,slug,Eslug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement = models.engagement.objects.get(slug=Eslug)
        form=forms.NewClientContact(engagement,request.POST)
        data['form_is_valid']=False
        if form.is_valid():
            form.save()
            data['form_is_valid']=True
        data['engagement_slug']=engagement.slug
        data['client_slug']=client.slug
        eligibility_rules=get_object_or_404(models.eligibility_rules,engagement=engagement)
        participants = models.participant.objects.filter(engagement=engagement)
        
        print(data["form_is_valid"])
        context_object={"client":client,"form":form,"engagement":engagement,"participants":participants}
        data['html_form']=render_to_string('add_client_contact.html',context_object,request=request)
        return JsonResponse(data)  

class DeleteClientContact(LoginRequiredMixin,TemplateView):

    template_name="delete_client_contact.html"
    login_url="/accounts/login/"
    
    def get(self,request,slug,Eslug,*args,**kwargs):
        print(slug)
        data=dict()
        client = models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        client_contacts = models.client_contact.objects.filter(engagement=engagement)

        FormSet=modelformset_factory(models.client_contact,forms.ContactDeleteForm,extra=0,can_delete=True)
        formset = FormSet(queryset=client_contacts)

        context_object = {'formset':formset,'client':client,'engagement':engagement,'client_contacts':client_contacts}

        data['html_form'] = render_to_string('delete_client_contact.html',context_object,request=request)

        return JsonResponse(data)

    def post(self,request,slug, Eslug, *args, **kwargs):

        data=dict()
        FormSet = modelformset_factory(models.client_contact, forms.ContactDeleteForm,extra=0,can_delete=True)
        formset=FormSet(request.POST,request.FILES)
        instance=formset.save()
        

        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        participants=models.participant.objects.filter(engagement=engagement)
      
        eligibility_rules=get_object_or_404(models.eligibility_rules,engagement=engagement)
        

        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants,}
        

        #data['engagements']=render_to_string('census_list.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client'],'errors':context['errors']},request=request)
        data['form_is_valid']=True
        data['html_form']=render_to_string('delete_client_contact.html',context,request=request)

        return JsonResponse(data) 


@login_required  
def export_selections(request,slug,Eslug):
    print('Working')

    client=models.client.objects.get(slug=slug)

    engagement=models.engagement.objects.get(slug=Eslug)

    participants=models.participant.objects.filter(engagement=engagement)

    selections=participants.filter(selection=True)

    response=HttpResponse(content_type='application/ms-excel')

    response['Content-Disposition'] = 'attachemnt; filename="Selections.xls"'

    #creating workbook
    wb = xlwt.Workbook(encoding="utf-8")

	#adding sheet
    ws = wb.add_sheet("Selections")

	# Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

	#column header names, you can use your own headers here
    columns = ['Selection #', 'First Name', 'Last Name', 'SSN','DOB','DOH','DOT','DORH','Excluded','Gross Wages','Eligible Wages','Hours Worked',
    'Employee Pre-Tax', 'Employer Pre-Tax','Employee Roth','Employer Roth','Employee Catch-Up',
    'Employer Catch-Up','Effective Deferral %' ]

	#write column headers in sheet
    for col_num in range(len(columns)):
	    ws.write(row_num, col_num, columns[col_num], font_style)

	# Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    date_xf = xlwt.easyxf(num_format_str='MM/DD/YYYY')
    
    currency_format = xlwt.XFStyle()
    currency_format.num_format_str = '$#,##0.00'
    number_format=xlwt.XFStyle()
    number_format.number_format_str = "#,##0.00"

    percentage_format=xlwt.XFStyle()
    percentage_format.number_format_str='0.00%'

	#get your data, from database or from a text file...
    for selection in selections:
        row_num = row_num + 1
        ws.write(row_num, 0, row_num, font_style)
        ws.write(row_num, 1, selection.first_name, font_style)
        ws.write(row_num, 2, selection.last_name, font_style)
        ws.write(row_num, 3, selection.SSN, font_style)
        ws.write(row_num, 4, selection.DOB, date_xf)
        ws.write(row_num, 5, selection.DOH, date_xf)
        ws.write(row_num, 6, selection.DOT, date_xf)
        ws.write(row_num, 7, selection.DORH,date_xf)
        ws.write(row_num, 8, selection.excluded, font_style)
        ws.write(row_num, 9, selection.gross_wages, currency_format)
        ws.write(row_num, 10, selection.eligible_wages, currency_format)
        ws.write(row_num, 11, selection.hours_worked, number_format)
        ws.write(row_num, 12, selection.EE_pre_tax_amount, currency_format)
        ws.write(row_num, 13, selection.ER_pre_tax_amount, currency_format)
        ws.write(row_num, 14, selection.EE_roth_amount, currency_format)
        ws.write(row_num, 15, selection.ER_roth_amount, currency_format)
        ws.write(row_num, 16, selection.EE_catch_up, currency_format)
        ws.write(row_num, 17, selection.ER_catch_up, currency_format)
        ws.write(row_num, 18, selection.effective_deferral_percentage, percentage_format)

    wb.save(response)
    return response

class PreviousSelections(LoginRequiredMixin,UserPassesTestMixin, TemplateView):
    template_name="py_selections.html"

    login_url="/accounts/login/"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request,slug,Eslug,*args,**kwargs):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        try:
            py_engagement=models.engagement.objects.get(client=client,date=engagement.date-relativedelta(years=1))
        except:
            py_engagement=None

        py_selections=models.participant.objects.filter(selection=True,engagement=py_engagement).order_by("-contributing")

        context={"client":client,"engagement":engagement,"py_engagement":py_engagement,"selections":py_selections}

        data['html_form']=render_to_string('py_selections.html',context,request=request)
        return JsonResponse(data)



class ViewErrors(LoginRequiredMixin,UserPassesTestMixin, TemplateView):
    template_name="view_errors_updated.html"

    login_url="/accounts/login/"

    def test_func(self):
        user = self.request.user
        
        client_slug = self.kwargs.pop("slug")
        client = models.client.objects.get(slug=client_slug)

        if client in user.client_set.all():
            test=True
        else:
            test=False
        
        return test

    def get(self,request,slug, Eslug,*args,**kwargs):
        data=dict()

        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(client=client,slug=Eslug)
        participants=models.participant.objects.filter(engagement=engagement)
        errors=models.error.objects.filter(participant__id__in=participants)

        FormSet=modelformset_factory(models.error,forms.ErrorForm,extra=0,can_delete=True)
        formset=FormSet(queryset=errors)
        errors=models.error.objects.filter(participant__id__in=participants)

        context={'formset':formset,"census_errors":errors,"client":client,"engagement":engagement,"participants":participants}
        
        data['html_form']=render_to_string('view_errors_updated.html',context,request=request)

        return JsonResponse(data)
    
    def post(self,request,slug,Eslug,*args,**kwargs):
        data=dict()
        FormSet = modelformset_factory(models.error, forms.ErrorForm,extra=0,can_delete=True)
        formset=FormSet(request.POST,request.FILES)
        instance=formset.save()
        

        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        participants=models.participant.objects.filter(engagement=engagement)
      
        eligibility_rules=get_object_or_404(models.eligibility_rules,engagement=engagement)

        errors=False
        for participant in participants:
            if len(participant.error_set.all()) > 0:
                print("Number of Errors:" + str(len(participant.error_set.all())))
                errors=True
                break
        

        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants,"errors":errors}
        

        #data['engagements']=render_to_string('census_list.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client'],'errors':context['errors']},request=request)
        data['form_is_valid']=True
        data['html_form']=render_to_string('view_errors_updated.html',context,request=request)

        return JsonResponse(data) 




@login_required  
def export_errors(request,slug,Eslug):
    print('Working')

    client=models.client.objects.get(slug=slug)

    engagement=models.engagement.objects.get(slug=Eslug)

    participants=models.participant.objects.filter(engagement=engagement)

    errors=models.error.objects.filter(participant__id__in=participants)

    response=HttpResponse(content_type='application/ms-excel')

    response['Content-Disposition'] = 'attachemnt; filename="Census_Errors.xls"'

    #creating workbook
    wb = xlwt.Workbook(encoding="utf-8")

	#adding sheet
    ws = wb.add_sheet("Errors")

	# Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

	#column header names, you can use your own headers here
    columns = ['Selection #', 'First Name', 'Last Name', 'SSN','DOB','DOH','DOT','DORH','Excluded','Gross Wages','Eligible Wages','Hours Worked',
    'Employee Pre-Tax', 'Employer Pre-Tax','Employee Roth','Employer Roth','Employee Catch-Up',
    'Employer Catch-Up','Effective Deferral %','Error Message' ]

	#write column headers in sheet
    for col_num in range(len(columns)):
	    ws.write(row_num, col_num, columns[col_num], font_style)

	# Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    date_xf = xlwt.easyxf(num_format_str='MM/DD/YYYY')
    
    currency_format = xlwt.XFStyle()
    currency_format.num_format_str = '$#,##0.00'
    number_format=xlwt.XFStyle()
    number_format.number_format_str = "#,##0.00"

    percentage_format=xlwt.XFStyle()
    percentage_format.number_format_str='0.00%'

	#get your data, from database or from a text file...
    for error in errors:
        row_num = row_num + 1
        ws.write(row_num, 0, row_num, font_style)
        ws.write(row_num, 1, error.participant.first_name, font_style)
        ws.write(row_num, 2, error.participant.last_name, font_style)
        ws.write(row_num, 3, error.participant.SSN, font_style)
        ws.write(row_num, 4, error.participant.DOB, date_xf)
        ws.write(row_num, 5, error.participant.DOH, date_xf)
        ws.write(row_num, 6, error.participant.DOT, date_xf)
        ws.write(row_num, 7, error.participant.DORH,date_xf)
        ws.write(row_num, 8, error.participant.excluded, font_style)
        ws.write(row_num, 9, error.participant.gross_wages, currency_format)
        ws.write(row_num, 10, error.participant.eligible_wages, currency_format)
        ws.write(row_num, 11, error.participant.hours_worked, number_format)
        ws.write(row_num, 12, error.participant.EE_pre_tax_amount, currency_format)
        ws.write(row_num, 13, error.participant.ER_pre_tax_amount, currency_format)
        ws.write(row_num, 14, error.participant.EE_roth_amount, currency_format)
        ws.write(row_num, 15, error.participant.ER_roth_amount, currency_format)
        ws.write(row_num, 16, error.participant.EE_catch_up, currency_format)
        ws.write(row_num, 17, error.participant.ER_catch_up, currency_format)
        ws.write(row_num, 18, error.participant.effective_deferral_percentage, percentage_format)
        ws.write(row_num, 19, error.error_message, font_style)

    wb.save(response)
    return response

class ParticipantAPI(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=serializer.ParticipantSerializer

    def get_queryset(self):
        user = self.request.user

        client=models.client.objects.get(slug=self.kwargs['slug'])
        if client in user.client_set.all():
            engagement=models.engagement.objects.get(slug=self.kwargs['Eslug'],client=client)
            participants=models.participant.objects.filter(engagement=engagement)
        
            return participants
        else:
            raise PermissionDenied({"message":"You do not have permission to access"})

class ClientAPI(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=serializer.ClientSerializer

    def get_queryset(self):
        clients=models.client.objects.filter(users=self.request.user) 
        return clients 

class EngagementAPI(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=serializer.EngagementSerializer

    def get_queryset(self):
        user = self.request.user
        client=models.client.objects.get(slug=self.kwargs['slug'])

        if client in user.client_set.all():
            engagements=models.engagement.objects.filter(client=client) 
            return engagements    
        else:
            raise PermissionDenied({"message":"You do not have permission to access"})






