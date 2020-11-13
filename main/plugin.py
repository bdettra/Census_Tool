from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from . import models
from django_random_queryset import RandomManager
import re

def location_dict(columns):

    #This is a dictionary of acceptable column headers that match that column to the data type that will be imported into our participant model
    column_dict={"First Name":["First Name", "First","FNAME","fname"],"Last Name":["Last Name", "Last","LNAME","lname"],"SSN":["Social","SSN"],
             "DOB":["Date of B","DOB","Birthdate","Birth Date"],"DOH":["Date of H", "DOH", "Hire Date","hire date","Original Hire Date"],"DOT":["Date of Te","DOT"],"DORH":["Date of Re","DORH"],
             "Excluded":["Excluded Em","Excluded"],"Hours Worked":["Hours Worked","Hours"],"Gross Wages":["Gross Wa", "Gross Wages", "Gross Comp","GROSS WAGES" "Gross Compensation"],
             "Eligible Wages":["Eligible Wages","eligible wages","Eligible wages","eligible Wages","Eligible Wage","eligible wage"],
            "EE pre-tax":["Employee Pre-Tax","EE Pre Tax","EE pre tax","employee pre-tax con","EE Pre-Tax","Deferrals","DEFERRALS","deferrals", "EE Pre"],
             "ER pre-tax":["Employer Pre-Tax","ER Pre-Tax","ER pre tax","employer pre-tax con","Match","match","MATCH","ER Pre"],
            "EE Roth":["Employee Roth","employee roth","Employee roth","EE Roth","EE Post","ROTH"],
            "ER Roth":["Employer Roth","employer roth","Employer roth","ER Roth","ER Post"],
            "EE Catch-up":["Employee Catch-Up","employee catch-up","EE Catch-up","EE Catch-Up","ee catch-up","EE catch-up"],
            "ER Catch-up":["Employer Catch-Up","employer catch-up","ER Catch-up","ER Catch-Up","er catch-up", "ER catch-up","ER Catch-UP"]}
    
    #Creating a location dictionary that knows where each of the participant attributes are in the uploaded excel file
    location_dict=dict()

    #Iterating through the column dictionary from above and using Python regular expressions in order to match one of the 
    #values with a header value in the uploaded excel file. Once found this alogrithm assigns the location of that specific attribute 
    #a value that corresponds with where it is at in the excel file.
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
    return location_dict


#Function that determines if a participant is excluded and then properly makes that participant not eligible.
def excluded_check(participant,prelim_rules):
    if participant.excluded==False:
        prelim_rules['Excluded_Employees']=True
    
    return prelim_rules

def hours_worked_check(participant,eligibility_rules,prelim_rules):
    if participant.hours_worked >= eligibility_rules.service_hours:
        prelim_rules['Service_Hours']=True
    
    return prelim_rules

def age_check(participant,eligiblity_rules,prelim_rules,engagement):
    year_end = engagement.date
    age = engagement.date - participant.DOB
    age=((age.days)/365) 

    if age>eligiblity_rules.age:
        prelim_rules['Age']=True
    
    return prelim_rules

def calculate_start_date(participant):
    #If the participant was terminated and rehired make the participants "Start Day" equal to the DORH attribute
    if participant.DORH !=None:
        start_day = participant.DORH

    if participant.DOT != None and participant.DORH != None:
        start_day = participant.DORH

    #If the participant was not terminated then make the participants "Start Day" equal to the DOH attribute
    if participant.DOT == None or (participant.DOT != None and participant.DORH == None) :
        start_day = participant.DOH
    
    return start_day


def calculate_entry_dates(participant,eligibility_rules,entry_dates,eligible_dates):
    #Iterating through the entry dates list and creating an entry dates list for  
    for i in range(len(entry_dates)):
        if eligibility_rules.entry_date == "First day of following Month":
            entry_dates[i] = eligible_dates[i] + relativedelta(months=1)
            entry_dates[i]= entry_dates[i].replace(day=1)

        elif eligibility_rules.entry_date == "Semi Annual (Jan 1 or July 1)":

                #Seting the Mid Year July entry date variable 
                    july_eligible_date=engagement.date.replace(month=7,day=1)

                    #If the eligible dates variable is greater than the mid year July entry date variable then the entry dates
                    #variable is set to Jan. 1 of the following year else the entry date variable is July 1st of the current year
                    if eligible_dates[i] > july_eligible_date:
                        entry_dates[i]=engagement.date + relativedelta(years=1)
                        entry_dates[i]=entry_dates[i].replace(month=1,day=1)
                    else:
                        entry_dates[i]=july_eligible_date
                
                #If the eligiblity rules entry date is "Annual (Jan1)" and the eligible date variable is greater than Jan.1 of the engagement year
                #then the entry date is Jan.1 of the year following the engagement year, else the entry date is the date of the eligible dates.
        elif eligibility_rules.entry_date == "Annual (Jan 1)":
            if eligible_dates[i] > engagement.date.replace(month=1,day=1):
                entry_dates[i]=engagement.date + relativedelta(year=1)
                entry_dates[i]=entry_dates[i].replace(month=1,day=1)
                
            else:
                entry_dates[i]=eligible_dates[i]

    return entry_dates

            
def eligibility(participant, eligibility_rules, engagement):
    '''A function that determines if an employee is eligible or not for a specific eligibility rule'''

    eligibility=True
    prelim_rules = {"Age":False,"Service_Hours":False,"Excluded_Employees":False}
    #Check to see if the participant is excluded
    prelim_rules=excluded_check(participant,prelim_rules)    

    #If the participant's age is over the eligiblity rules age go through additional checks
    prelim_rules=age_check(participant,eligibility_rules,prelim_rules,engagement)


    #If the participant's hours worked is greater than the eligiblity rules service hours then proceed with additional checks   
    prelim_rules=hours_worked_check(participant,eligibility_rules,prelim_rules)

    #Performing a preliminary check of participant age, hours worked and excluded classifcation and return eligibility as False if any of those dictionary
    #items are false.
    for key, value in prelim_rules.items():
        if value == False:
            eligibility=False
            return eligibility
            


    #Calculating the participant's start day
    start_day=calculate_start_date(participant)

    #Creating datetime objects for the service days, service years and service months eligiblity rules
    service_days=relativedelta(days=eligibility_rules.service_days)
    service_years=relativedelta(years=eligibility_rules.service_years)
    service_months=relativedelta(months=eligibility_rules.service_months)

    #Creating datetime variables for when the participant becomes eligible for each of the eligiblity requirements (Eligible Days, Eligible Months, Eligible Years)
    #and appending it to a list
    eligible_dates=[]
    eligible_days = start_day + service_days
    eligible_dates.append(eligible_days)
    eligible_years = start_day + service_years
    eligible_dates.append(eligible_years)
    eligible_months = start_day + service_months
    eligible_dates.append(eligible_months)

    #Creating entry date, entry month and entry year variables and appending them to a list named "Entry Dates"
    entry_date=None
    entry_month=None
    entry_year=None
    entry_dates=[entry_date, entry_month, entry_year]
            
    entry_dates=calculate_entry_dates(participant,eligibility_rules,entry_dates,eligible_dates)


    #Iterating through the entry dates list and for each variable in the list if that variable is greater than the engagement date year end then 
    #the eligible variable is set to false
    for i in entry_dates:
        if i > engagement.date:
            eligibility=False
            
     #Making each participant's eligible attribute as False to start with.
    if eligibility_rules.match_type=="Deferral" and eligibility==True:
        participant.deferral_eligible=True
    elif eligibility_rules.match_type=="Match" and eligibility==True:
        participant.match_eligible=True
    elif eligibility_rules.match_type=="Profit Sharing" and eligibility==True:
        participant.profit_share_eligible=True

    participant.save()

    return eligibility

def participating(participant):

    #Initializing participant contribution variables
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

    #For loop that lists through participant contribution vairalbes and if any of them equal true then the participants participating variable is set to true and the contributing variable is set to true
    for i in participating:
        if i == True:
            participant.participating=True
            participant.contributing=True
    
    return participating

            
def effective_deferral(participant):
    '''A function that determines the participants effective deferral percentage'''

    total_deferral = participant.EE_pre_tax_amount + participant.EE_roth_amount + participant.EE_catch_up

    if total_deferral == 0:
        participant.effective_deferral_percentage = 0
    
    else:
        percentage = (total_deferral / participant.gross_wages) * 100

        participant.effective_deferral_percentage = percentage


def generate_selections(engagement):
    '''A function that makes selections for an engagemenet'''
    
    #Getting the participants related to the specific engagement and makeing there selection attribute false
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

    #Defining the date range of engagement to lookback on for making selections
    engagements=models.engagement.objects.filter(date__range=[(engagement.date-relativedelta(years=3)), engagement.date-relativedelta(years=1)])
    
    #A series of for loops that finds employees in the current census that were selections
    #in the past 3 years and then excludes them from the current year population.
    py_selections=[]
    for engagement in engagements:
        for participant in sample:
            try:
                #Using the SSN as the ultimate identifier
                py_selection = engagement.participant_set.get(SSN=participant.SSN,selection=True)
                py_selections.append(py_selection)
            except ObjectDoesNotExist:
                print("This participant was not a previous year selections")

    #Excluding PY selections for our CY sample            
    for selection in py_selections:
        sample=sample.exclude(SSN=selection.SSN)

    #Creating seperate samples of contributing and non-contributing employees.
    sample_of_contributing =sample.filter(contributing=True)
    sample_of_non_contributing = sample.filter(contributing=False)

    selections_dict=dict()
    contributing_selections = sample_of_contributing.random(number_of_cont_selections)
    non_contributing_selections = sample_of_non_contributing.random(number_of_non_cont_selections)
    selections_dict['Contributing']=contributing_selections
    selections_dict['Non-Contributing'] = non_contributing_selections

    for participant in contributing_selections:
        participant.selection=True
        #selections_dict=participant.SSN
        participant.save()

    for participant in non_contributing_selections:
        participant.selection=True
        participant.save()

    

    return sample


def generate_selections_version_2(engagement):

    
    '''Need to add handling for first year audits where population will be full census'''
    participants=models.participant.objects.filter(engagement=engagement)
    for i in participants:
        i.selection=False
        i.save()

    if engagement.first_year==True:
        population=models.participant.objects.filter(engagement=engagement)
    else:

        population = models.participant.objects.filter(engagement=engagement)

        new_hires= models.participant.objects.filter(DOH__range=[engagement.date-relativedelta(years=1), engagement.date],engagement=engagement)

        terminations = population.exclude(DOT=None)
    
        errors = models.participant.objects.filter(error__in=models.error.objects.filter(participant__in=population))


        population = new_hires | terminations | errors

    sample_of_contributing=population.filter(contributing=True)
    sample_of_non_contributing=population.filter(contributing=False)
    number_of_contributing = population.filter(contributing=True).count()
    number_of_non_contributing = population.filter(contributing=False).count()

    if engagement.soc_1_reliance == False:
        if len(population) < 250:
            number_of_selections=round(population.count()*.10)
        elif population.count() > 250 and population.count() < 2500:
            number_of_selections=25
        elif population.count() > 2500 and population.count() < 5000:
            number_of_selections=45
        elif population.count() > 5000:
            number_of_selections=60
    else:
        if population.count() < 250:
            number_of_selections=round(population*.05)
        elif population.count() > 250 and population.count() < 2500:
            number_of_selections=12
        elif population.count() > 2500 and population.count() < 5000:
            number_of_selections=23
        elif population.count() > 5000:
            number_of_selections=30

    if number_of_non_contributing > number_of_contributing:
        number_of_cont_selections=min(round(number_of_contributing*.10),10)
    else:
        number_of_cont_selections=round((number_of_contributing/len(population))*number_of_selections)

    number_of_non_cont_selections=number_of_selections-number_of_cont_selections

    contributing_selections = sample_of_contributing.random(number_of_cont_selections)
    non_contributing_selections = sample_of_non_contributing.random(number_of_non_cont_selections)

    for participant in contributing_selections:
        participant.selection=True
        participant.save()

    for participant in non_contributing_selections:
        participant.selection=True
        participant.save()

    return population

            


    


def previous_year_check(participant,py_engagement):

    py_participants=models.participant.objects.filter(engagement=py_engagement)
    error_dict={"First Name":False,"Last Name":False,"SSN":False,"DOB":False,
    "DOH":False,"DOT":False,"DORH":False}
    if len(py_participants.filter(SSN__exact=participant.SSN))>0:
        try:
            py_data=py_participants.get(SSN__exact=pariticpant.SSN,first_name=participant.first_name,last_name=pariticpant.last_name)
        except:
            py_data=py_participants.get(SSN__exact=participant.SSN)
            print(py_data)
    else:
        py_data=py_participants.get(SSN__exact=participant.SSN)




    if py_data.first_name != participant.first_name:
        print(str(py_data.first_name)+'---'+ str(participant.first_name))
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

    return error_dict

def contribution_check(participant,engagement,location_dict):
    max_contributions = int(19000)

    if location_dict["EE Catch-up"]==None:
        max_contributions = int(25000)
    
    
    if participant.EE_pre_tax_amount + participant.EE_roth_amount > max_contributions:
        error=models.error.objects.create(error_message="Employee contributions are greater than IRS limit",participant=participant)
        error.save()

    age = engagement.date - participant.DOB
    age=((age.days)/365) 

    if participant.EE_catch_up > int(6000):
        error=models.error.objects.create("Catch-up contributions amount is over IRS limit",participant=participant)
        error.save()
        
    if age < 50 and (participant.EE_catch_up + participant.ER_catch_up) > 0:
        error=models.error.objects.create(error_message="Employee is not eligible for catch-up contributions",participant=participant)
        error.save()
    
    elif location_dict["EE Catch-up"]==None and age < 50 and participant.EE_pre_tax_amount + participant.EE_roth_amount > int(19000):
        error=models.error.objects.create(error_message="Employee is not eligible for catch-up contributions (No catch-up column)",participant=participant)
        error.save()
    
        

def eligible_wages_check(participant,engagement):
    if participant.eligible_wages > int(280000):
        error=models.error.objects.create(error_message="Eligible wages are greater than IRS limit",participant=participant)
        error.save()
      





    

    
    




        
                

            



            

        
