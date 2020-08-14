from . import models, forms
from django.core.mail import send_mail
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.generic.edit import FormView, DeleteView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.utils.text import slugify
import re
import pandas as pd
from . import plugin
from dateutil.relativedelta import relativedelta
from django.forms import modelformset_factory
from django.forms import formset_factory
from django.db.models import Avg, StdDev
import xlwt


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
    '''Renders the sign up page.'''

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
        return response


@login_required
def client_dashboard(request):
    '''Renders the client dashboard page'''

    clients=models.client.objects.filter(users=request.user)

    context={"clients":clients}

    return render(request,"client_dashboard.html",context)

class createClientView(TemplateView):
    '''Renders the create client modal'''

    template_name="new_client.html"

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
            slug=slugify(name)
            instance=models.client.objects.create(name=name,number=number,slug=slug)
            instance.users.set(users)
            data['form_is_valid']=True

        user=request.user

        clients=models.client.objects.filter(users=user)
        context={"clients":clients,"form":form}
        

        data['clients']=render_to_string('client_list.html',{'clients':context['clients'],},request=request)
        data['html_form']=render_to_string('new_client.html',context,request=request)
        
        return JsonResponse(data)


class ClientDeleteView(DeleteView):
    model=models.client
    success_url=reverse_lazy('client_dashboard')
    template_name="client_dashboard.html"



class CreateEngagement(TemplateView):
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
            instance=models.engagement.objects.create(name=name,date=date,slug=slug_name, client=client_object)
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

        data['engagements']=render_to_string('engagement_list.html',{'engagements':context['engagements'], 'client': context['client']},request=request)
        
        data['html_form']=render_to_string('new_engagement.html',context,request=request)
        print(data['form_is_valid'])

        return JsonResponse(data)    


@login_required
def client_page(request,slug):
    client=models.client.objects.get(slug=slug)
    engagements=models.engagement.objects.filter(client=client)
    context={"client":client,"engagements":engagements}

    return render(request,"client_page.html",context)

class EngagementView(TemplateView):

    template_name="engagement_page.html"

    def get(self,request, slug, Eslug, *args,**kwargs):

        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        participants = models.participant.objects.filter(engagement=engagement)
        census_form=forms.CensusFileForm()

        context={'census_form':census_form,'client':client,'engagement':engagement,"eligibility_rules":eligibility_rules,"participants":participants}

        return render(request,"engagement_page.html",context=context)


class EditEligibility(TemplateView):
    template_name="edit_eligibility.html"

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
        '''
        age=request.POST.get('age')
        service_hours=request.POST.get('service_hours')
        service_days=request.POST.get('service_days')
        service_months=request.POST.get('service_months')
        service_years=request.POST.get('service_years')
        excluded_employees=request.POST.get('excluded_employees')
        entry_date=request.POST.get('entry_date')
    
        
        '''
        client=models.client.objects.get(slug=slug)
        eligibility_rules=get_object_or_404(models.eligibility_rules,engagement=engagement)
        '''
        eligibility_rules.age=age
        eligibility_rules.service_hours=service_hours
        eligibility_rules.service_days=service_days
        eligibility_rules.service_months=service_months
        eligibility_rules.service_years=service_years
        eligibility_rules.excluded_employees=excluded_employees
        eligibility_rules.entry_date=entry_date
        eligibility_rules.save()
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        '''
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
        data['engagements1']=render_to_string('census_list.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client'],"eligibility_rules":context["eligibility_rules"]},request=request)

        
        data['form_is_valid']=True
        data['html_form']=render_to_string('edit_eligibility.html',context,request=request)
        print("Posting Correctly")
        return JsonResponse(data)


        
class KeyEmployee(TemplateView):
    template_name="key_employee.html"

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

        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants,}

        data['engagements']=render_to_string('census_list.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client']},request=request)
        
        data['form_is_valid']=True
        data['html_form']=render_to_string('key_employee.html',context,request=request)

        return JsonResponse(data) 

class CensusStatistics(TemplateView):

    template_name="census_statistics.html"

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

        context_object={"number_of_non_cont_selections":number_of_non_cont_selections,"number_of_cont_selections":number_of_cont_selections,"number_of_selections":number_selections,"lowest_earner":lowest_earner,"top_earner":top_earner,"standard_dev_wages":standard_dev_wages,"key_employees":key_employees,"employees_terminated":employees_terminated,"average_gross_wages":average_gross_wages,"ineligible":ineligible,"eligible":eligible,"non_contributing_employees":non_contributing_employees,"contributing_employees":contributing_employees,"number_of_employees":number_of_employees,"participants":participants, "client":client, "engagement":engagement,"eligibility_rules":eligibility_rules,}
        data['html_form']=render_to_string('census_statistics.html',context_object,request=request)
        return JsonResponse(data)


class MakeSelections(TemplateView):

    template_name="make_selections.html"

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
        participants=models.participant.objects.filter(engagement=engagement)

        context={"engagement":engagement,"client":client,"eligibility_rules":eligibility_rules,"participants":participants,}

        data['engagements']=render_to_string('census_list.html',{"participants":context["participants"],'engagement':context['engagement'], 'client': context['client']},request=request)
        
        data['form_is_valid']=True
        data['html_form']=render_to_string('make_selections.html',context,request=request)
    
        return JsonResponse(data) 

class EditClient(TemplateView):


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
        


class ViewSelections(TemplateView):
    template_name="view_selections.html"

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

class UploadCensus(TemplateView):
    template_name="upload_census.html"

    def get(self,request,slug,Eslug):
        data=dict()
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        form=forms.CensusFileForm()

        context_object={"client":client,"form":form,"engagement":engagement}
        data['html_form']=render_to_string("upload_census.html",context_object,request=request)

        return JsonResponse(data)

    def post(self,request,slug,Eslug,*args,**kwargs):
        client=models.client.objects.get(slug=slug)
        engagement=models.engagement.objects.get(slug=Eslug,client=client)
        eligibility_rules=models.eligibility_rules.objects.get(engagement=engagement)
        form=forms.CensusFileForm(request.POST, request.FILES)
        participants=models.participant.objects.filter(engagement=engagement)
        for instance in participants:
            instance.delete()
        participants=models.participant.objects.filter(engagement=engagement)
        context={"client":client,"engagement":engagement,"eligibility_rules":eligibility_rules,"form":forms.CensusFileForm,"participants":participants}

        data=pd.read_excel(request.FILES['filename'])
        
        columns=data.columns

        column_dict={"First Name":["First Name", "First"],"Last Name":["Last Name", "Last"],"SSN":["Social","SSN"],
             "DOB":["Date of B","DOB"],"DOH":["Date of H", "DOH"],"DOT":["Date of Te","DOT"],"DORH":["Date of Re","DORH"],
             "Excluded":["Excluded Em","Excluded"],"Hours Worked":["Hours Worked"],"Gross Wages":["Gross Wa", "Gross Wages"],
             "Eligible Wages":["Eligible Wages","eligible wages","Eligible wages","eligible Wages","Eligible Wage","eligible wage"],
            "EE pre-tax":["Employee Pre-Tax","EE Pre Tax","EE pre tax","employee pre-tax con","EE Pre-Tax"],
             "ER pre-tax":["Employer Pre-Tax","ER Pre-Tax","ER pre tax","employer pre-tax con"],
            "EE Roth":["Employee Roth","employee roth","Employee roth","EE Roth"],
            "ER Roth":["Employer Roth","employer roth","Employer roth","ER Roth"],
            "EE Catch-up":["Employee Catch-Up","employee catch-up","EE Catch-up","EE Catch-Up","ee catch-up","EE catch-up"],
            "ER Catch-up":["Employer Catch-Up","employer catch-up","ER Catch-up","ER Catch-Up","er catch-up", "ER catch-up","ER Catch-UP"]}

        try:
            data['DOB']=pd.to_datetime(data['DOB'],format="%m/%d/%y")
            data['DOH']=pd.to_datetime(data['DOH'],format="%m/%d/%y")
            data['DORH']=pd.to_datetime(data['DORH'],format="%m/%d/%y")
        except Exception as e:
            print('There was an error:{0}'.format(e))
            return render(request,"engagement_page.html",context=context)

        location_dict=dict()
        for key, value in column_dict.items():
            found=False
            for v in value:
                counter=0
                location=0
                pattern=re.compile(v)
                for c in columns:
                    if pattern.match(c)!=None and found==False:
                        location=counter
                        location_dict[key]=location
                        counter+=1
                        found=True
                    elif found==False:
                        counter+=1

        for i,x in data.iterrows():
            if pd.isnull(data.iloc[i,location_dict['SSN']])==False:
                participant, created=models.participant.objects.update_or_create(SSN=data.iloc[i,location_dict['SSN']],engagement=engagement)
            else:
                messages.error(self.request,"One of the employees is missing a SSN value. Census stopped processing at that employee.")
                return render(request,"engagement_page.html",context=context)

            if pd.isnull(data.iloc[i,location_dict['First Name']])==False:
                participant.first_name=data.iloc[i,location_dict['First Name']]
                participant.save()
            else:
                messages.error(self.request,"One of the participants is missing a First Name Value")
                
            
            if pd.isnull(data.iloc[i,location_dict['Last Name']])==False:
                participant.last_name=data.iloc[i,location_dict['Last Name']]
                participant.save()
            else:
                messages.error(self.request,"One of the participants is missing a Last Name Value")

            if pd.isnull(data.iloc[i,location_dict['DOB']])==False:
                participant.DOB=data.iloc[i,location_dict['DOB']].date()
            else:
                messages.error(self.request,participant.first_name +" " + participant.last_name + "is missing a DOB value. Census stopped processing at that employee.")
                return render(request,"engagement_page.html",context=context)

            if pd.isnull(data.iloc[i,location_dict['DOH']])==False:
                participant.DOH=data.iloc[i,location_dict['DOH']].date()
            else:
                messages.error(self.request,participant.first_name +" " + participant.last_name + "is missing a DOH value. Census stopped processing at that employee.")
                return render(request,"engagement_page.html",context=context)

            if pd.isnull(data.iloc[i,location_dict['DOT']])==False:
                participant.DOT=data.iloc[i,location_dict['DOT']].date()
                participant.save()
                if participant.DOT < (engagement.date - relativedelta(years=1)):
                    messages.error(self.request,participant.first_name + " " + participant.last_name + " " + "has a date of termination that is before the engagement year. You should investigate further.")

            if pd.isnull(data.iloc[i,location_dict['DORH']])==False:
                participant.DORH=data.iloc[i,location_dict['DORH']].date()

            if pd.isnull(data.iloc[i,location_dict["Excluded"]])==False:
                excluded=data.iloc[i,location_dict['Excluded']]
                excluded_values=[None,"No",'no']
                
                if data.iloc[i,location_dict['Excluded']] in excluded_values:
                    participant.excluded=False
                else:
                    participant.excluded=True

            if pd.isnull(data.iloc[i,location_dict['Hours Worked']])==False:
                participant.hours_worked=data.iloc[i,location_dict['Hours Worked']]
            else:
                messages.error(self.request,"One of the participants is missing an 'Hours Worked' value")

            if pd.isnull(data.iloc[i,location_dict['Gross Wages']])==False:
                participant.gross_wages=data.iloc[i,location_dict['Gross Wages']]
            
            
            if pd.isnull(data.iloc[i,location_dict['Eligible Wages']])==False:
                participant.eligible_wages=data.iloc[i,location_dict['Eligible Wages']]

            if pd.isnull(data.iloc[i,location_dict['EE pre-tax']])==False:
                participant.EE_pre_tax_amount=data.iloc[i,location_dict['EE pre-tax']]


            if pd.isnull(data.iloc[i,location_dict['ER pre-tax']])==False:
                participant.ER_pre_tax_amount=data.iloc[i,location_dict['ER pre-tax']]

            if pd.isnull(data.iloc[i,location_dict['EE Roth']])==False:
                participant.EE_roth_amount=data.iloc[i,location_dict['EE Roth']]

            if pd.isnull(data.iloc[i,location_dict['ER Roth']])==False:
                participant.ER_roth_amount=data.iloc[i,location_dict['ER Roth']]
            
            if pd.isnull(data.iloc[i,location_dict['EE Catch-up']])==False:
                participant.EE_catch_up=data.iloc[i,location_dict['EE Catch-up']]
            
            if pd.isnull(data.iloc[i,location_dict['ER Catch-up']])==False:
                participant.ER_catch_up=data.iloc[i,location_dict['ER Catch-up']]

            participant.key_employee=False
            participant.save()

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


        return HttpResponseRedirect(reverse('engagement_page',args=(slug, Eslug)))

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

class PreviousSelections(TemplateView):
    template_name="py_selections.html"

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





