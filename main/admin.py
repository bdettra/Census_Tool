from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.mail import send_mail
from . import models
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Avg, Count, Min, Sum, Value
from . import views


class EligibilityRules(admin.ModelAdmin):
    model=models.eligibility_rules
    list_display=("age","service_hours","service_days","service_months",
    "service_years","excluded_employees","entry_date","engagement",)

class EngagementAdmin(admin.ModelAdmin):
    model=models.engagement
    list_display=("name","date","client","soc_1_reliance",)

class ClientAdmin(admin.ModelAdmin):
    model=models.client
    list_display=("name","number",)

class ParticipantAdmin(admin.ModelAdmin):
    models=models.participant
    list_display=("first_name","last_name","SSN","DOB","DOH","DOT","DORH","excluded",
    "gross_wages","eligible_wages","hours_worked","EE_pre_tax_amount","ER_pre_tax_amount",
    "EE_roth_amount","ER_roth_amount","EE_catch_up","ER_catch_up",
    "effective_deferral_percentage","selection","key_employee","eligible",
    "participating","engagement","id",)

class ClientContactAdmin(admin.ModelAdmin):
    models=models.client_contact
    list_display=("first_name","last_name","position","email","engagement")

class ErrorAdmin(admin.ModelAdmin):
    model=models.error
    list_display=("error_message",'participant')


'''class UserAdmin(DjangoUserAdmin):
    fieldsets=(
        (None,{"fields":("email","password")}),
        (
            "Personal info",
            {"fields":("first_name","last_name")}
        ),
        (
            "Permissions",
            {"fields":("is_active","is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            )
            }
        ),
        (
            "Important dates",
            {"fields":("last_login","date_joined")},
        ),
    )
    add_fieldsets=(
        (
            None,
            {
                "classes":("wide",),
                "fields":("email","password1","password2"),
            },
        ),
    )

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )

    search_fields=(
        "email","first_name","last_name"
    )
    
    ordering=("email",)
'''
'''
class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self,request):
        context=super().each_context(request)
        context["site_header_color"]=getattr(self,"site_header_color",None)

        context["module_caption_color"]=getattr(
            self,"module_caption_color",None
        )

        return context

class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls=super().get_urls()
        my_urls=[]
        return my_urls + urls
    


class OwnersAdminSite(ReportingColoredAdminSite):
    site_header="EBP Portal Administration"
    site_header_color="#FF6357"
    module_caption_color="white"
    def has_permission(self,request):
        return (
            request.user.is_active and request.user.is_superuser
        )
'''

main_admin=admin.site
#main_admin.register(models.User,UserAdmin)
main_admin.register(models.client,ClientAdmin)
main_admin.register(models.engagement,EngagementAdmin)
main_admin.register(models.eligibility_rules,EligibilityRules)
main_admin.register(models.participant,ParticipantAdmin)
main_admin.register(models.client_contact,ClientContactAdmin)
main_admin.register(models.error,ErrorAdmin)
