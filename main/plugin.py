from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from . import models
from django_random_queryset import RandomManager

def eligibility(participant, eligibility_rules, engagement):
    year_end = engagement.date
    age = engagement.date - participant.DOB
    age=((age.days)/365) 
    participant.eligible=False
    if participant.excluded == True:
        participant.eligible=False
    if age > eligibility_rules.age:
        if participant.hours_worked >= eligibility_rules.service_hours:
            if participant.DOT != None and participant.DORH != None:
                start_day = participant.DORH
            elif participant.DOT == None:
                start_day = participant.DOH
            elif participant.DOT != None and participant.DORH == None:
                participant.eligiblity=False

            
            if participant.DORH == None:
                start_day = participant.DOH
            else:
                start_day = participant.DORH

            service_days=relativedelta(days=eligibility_rules.service_days)
            service_years=relativedelta(years=eligibility_rules.service_years)
            service_months=relativedelta(months=eligibility_rules.service_months)

            eligible_dates=[]
            eligible_days = start_day + service_days
            eligible_dates.append(eligible_days)
            eligible_years = start_day + service_years
            eligible_dates.append(eligible_years)
            eligible_months = start_day + service_months
            eligible_dates.append(eligible_months)


            entry_date=None
            entry_month=None
            entry_year=None

            entry_dates=[entry_date,entry_month,entry_year]
            
            for i in range(len(entry_dates)):
                if eligibility_rules.entry_date == "First day of following Month":
                    entry_dates[i] = eligible_dates[i] + relativedelta(months=1)
                    entry_dates[i]= entry_dates[i].replace(day=1)
                    
                
            eligible=True
            for i in entry_dates:
                if i > year_end:
                    eligible=False
            
            if eligible == True:
                participant.eligible=True
            else:
                participant.eligible=False
                

    return participant.eligible

def participating(participant):
    employee_pre_tax=None
    employer_pre_tax=None
    employee_roth=None
    employer_roth=None
    employee_catch_up=None
    employer_catch_up=None
    participating=[]
    participant.participating=False
    participant.contributing=False

    if participant.EE_pre_tax_amount == 0 or participant.EE_pre_tax_amount == None:
        employee_pre_tax=False
    else:
        employee_pre_tax=True
    participating.append(employee_pre_tax)

    if participant.ER_pre_tax_amount == 0 or participant.ER_pre_tax_amount == None:
        employer_pre_tax=False
    else:
        employer_pre_tax=True
    participating.append(employer_pre_tax)

    if participant.EE_roth_amount == 0 or participant.EE_roth_amount == None:
        employee_roth=False
    else:
        employee_roth=True
    participating.append(employee_roth)
                
    if participant.ER_roth_amount == 0 or participant.ER_roth_amount == None:
        employer_roth=False
    else:
        employer_roth=True
    participating.append(employer_roth)
                    
    if participant.EE_catch_up == 0 or participant.EE_catch_up == None:
        employee_catch_up=False
    else:
        employee_catch_up=True
    participating.append(employee_catch_up)
                        
    if participant.ER_catch_up == 0 or participant.ER_catch_up == None:
        employer_catch_up=False
    else:
        employer_catch_up=True
    participating.append(employer_catch_up)

    for i in participating:
        if i == True:
            participant.participating=True
            participant.contributing=True
    
    return participating

            
def effective_deferral(participant):
    total_deferral = participant.EE_pre_tax_amount + participant.EE_roth_amount + participant.EE_catch_up

    percentage = (total_deferral / participant.gross_wages) * 100

    participant.effective_deferral_percentage = percentage


def generate_selections(engagement):
    
    participants=models.participant.objects.filter(engagement=engagement)
    for i in participants:
        i.selection=False
        i.save()

    #Seperating our population of non-contributing and contributing employees
    number_of_contributing=participants.filter(contributing=True).count()
    number_of_non_contributing=participants.filter(contributing=False).count()

    #Defining the total population of the census
    population=participants.count()

    #Determining the number of selections to make depending on SOC 1 reliance.
    if engagement.soc_1_reliance == False:
        if population < 250:
            number_of_selections=round(population*.10)
        elif population > 250 and population < 2500:
            number_of_selections=25
        elif population > 2500 and population < 5000:
            number_of_selections=45
        elif population > 5000:
            number_of_selections=60
    else:
        if population < 250:
            number_of_selections=round(population*.05)
        elif population > 250 and population < 2500:
            number_of_selections=12
        elif population > 2500 and population < 5000:
            number_of_selections=23
        elif population > 5000:
            number_of_selections=30

    #Defining the number of non-contributing employee and contributing employees
    #depending on startification of the census.
    if number_of_non_contributing > number_of_contributing:
        number_of_cont_selections=min(round(number_of_contributing*.10),10)
    else:
        number_of_cont_selections=round((number_of_contributing/population)*number_of_selections)

    number_of_non_cont_selections=number_of_selections-number_of_cont_selections

    key_employees = participants.filter(key_employee=True)

    #Making every Key Employee a selection
    for participant in key_employees:
        participant.selection=True
        participant.save()
        if participant.contributing==True:
            number_of_cont_selections -= 1
        else:
            number_of_non_cont_selections -= 1

    #Defining the remaining population after excluding our selected Key Employees    
    sample=participants.filter(key_employee=False)
    print(sample)
    print(participants)

    #Defining the date range of engagement to lookback on for making selections
    engagements=models.engagement.objects.filter(date__range=[(engagement.date-relativedelta(years=3)), engagement.date-relativedelta(years=1)])
    
    #A series of for loops that finds employees in the current census that were selections
    #in the past 3 years and then excludes them from the current year population.
    py_selections=[]
    for engagement in engagements:
        for participant in sample:
            try:
                py_selection = engagement.participant_set.get(SSN=participant.SSN,selection=True)
                py_selections.append(py_selection)
            except ObjectDoesNotExist:
                print("This participant was not a previous year selections")
    for selection in py_selections:
        sample=sample.exclude(SSN=selection.SSN)

    sample_of_contributing =sample.filter(contributing=True)
    sample_of_non_contributing = sample.filter(contributing=False)

    selections_dict=dict()
    contributing_selections = sample_of_contributing.random(number_of_cont_selections)
    non_contributing_selections = sample_of_non_contributing.random(number_of_non_cont_selections)
    selections_dict['Contributing']=contributing_selections
    selections_dict['Non-Contributing'] = non_contributing_selections

    for participant in contributing_selections:
        participant.selection=True
        selections_dict=participant.SSN
        participant.save()

    for participant in non_contributing_selections:
        participant.selection=True
        participant.save()

    

    return sample


def previous_year_check(participant,py_engagement):

    py_participants=models.participant.objects.filter(engagement=py_engagement)
    error_dict={"First Name":False,"Last Name":False,"SSN":False,"DOB":False,
    "DOH":False,"DOT":False,"DORH":False}
    try:
        py_data=py_participants.get(SSN__exact=participant.SSN)
    except:
        print("didnt work")
        return error_dict

    if py_data.first_name != participant.first_name:
        error_dict["First Name"]=(participant.first_name + ' ' +  participant.last_name +"'s" + ' first name changed from the previous year census. You should investigate further.')
        models.error.objects.create(participant=participant,error_message="First name data does not match previous year census")
    if py_data.last_name != participant.last_name:
        error_dict["Last Name"]=(participant.first_name + ' ' +  participant.last_name +"'s" + ' last name changed from the previous year census. You should investigate further.')
        models.error.objects.create(participant=participant,error_message="Last name data does not match previous year census")
    if py_data.DOB != participant.DOB:
        error_dict["DOB"]=(participant.first_name + ' ' + participant.last_name +"'s" + ' date of birth changed from the previous year census. You should investigate further.')
        models.error.objects.create(participant=participant,error_message="DOB data does not match previous year census")
    
    if py_data.DOH != participant.DOH:
        error_dict["DOH"]=(participant.first_name + ' ' + participant.last_name +"'s" + ' date of hire changed from the previous year census. You should investigate further.')
        models.error.objects.create(participant=participant,error_message="DOH data does not match previous year census")
    if py_data.DOT != participant.DOT:
        error_dict["DOT"]=(participant.first_name + ' ' + participant.last_name +"'s" + ' date of termination changed from the previous year census. You should investigate further.')
        models.error.objects.create(participant=participant,error_message="DOT data does not match previous year census")
    if py_data.DORH != participant.DORH:
        error_dict["DORH"]=(participant.first_name + ' ' + participant.last_name +"'s" + ' date of rehire changed from the previous year census. You should investigate further.')
        models.error.objects.create(participant=participant,error_message="DORH data does not match previous year census")

    return error_dict

def contribution_check(participant,engagement):
    if participant.EE_pre_tax_amount + participant.EE_roth_amount > int(19500):
        error=models.error.objects.create(error_message="Employee contributions are greater than IRS limit",participant=participant)
        error.save()
        #messages.error(self.request,participant.first_name + " " + participant.last_name + " controbitons are greater than the IRS limit")

    age = engagement.date - participant.DOB
    age=((age.days)/365) 

    if participant.EE_catch_up > int(6000):
        error=models.error.objects.create("Catch-up contributions amount is over IRS limit",participant=participant)
        error.save()
        #messages.error(self.request,participant.first_name + " " + participant.last_name + " catch-up controbitons are greater than the IRS limit")

    if age < 50 and (participant.EE_catch_up + participant.ER_catch_up) > 0:
        error=models.error.objects.create(error_message="Employee is not eligible for catch-up contributions",participant=participant)
        error.save()
        #messages.error(self.request,participant.first_name + " " + participant.last_name + " is not eligible for catch-up contributions")

def eligible_wages_check(participant,engagement):
    if participant.eligible_wages > int(280000):
        error=models.error.objects.create(error_message="Eligible wages are greater than IRS limit",participant=participant)
        error.save()
       #messages.error(self.request,participant.first_name + " " + participant.last_name + " eligible wages are over IRS limit")





    

    
    




        
                

            



            

        
