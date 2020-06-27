from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.mail import send_mail
from . import models
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Avg, Count, Min, Sum, Value
from . import views

class StringRowAdmin(admin.ModelAdmin):
    model=models.StringRow
    list_display=("column","data")

class FloatRowAdmin(admin.ModelAdmin):
    model=models.FloatRow
    list_display=("column","data")

class IntegerRowAdmin(admin.ModelAdmin):
    model=models.IntegerRow
    list_display=("column","data")

class DateRowAdmin(admin.ModelAdmin):
    model=models.DateRow
    list_display=("column","data")

class ColumnAdmin(admin.ModelAdmin):
    model=models.column
    list_display=("name","d_type")

class SpreadsheetAdmin(admin.ModelAdmin):
    model=models.spreadsheet
    list_display=("name","date","template")

class TemplateSpreadsheetAdmin(admin.ModelAdmin):
    model=models.TemplateSpreadsheet
    list_display=("name","client")

class EngagementAdmin(admin.ModelAdmin):
    model=models.engagement
    list_display=("name","date","client")

class ClientAdmin(admin.ModelAdmin):
    model=models.client
    list_display=("name","number",)

class UserAdmin(DjangoUserAdmin):
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

main_admin=OwnersAdminSite()
main_admin.register(models.User,UserAdmin)
main_admin.register(models.client,ClientAdmin)
main_admin.register(models.engagement,EngagementAdmin)
main_admin.register(models.spreadsheet,SpreadsheetAdmin)
main_admin.register(models.column,ColumnAdmin)
main_admin.register(models.StringRow,StringRowAdmin)
main_admin.register(models.IntegerRow,IntegerRowAdmin)
main_admin.register(models.FloatRow,FloatRowAdmin)
main_admin.register(models.DateRow,DateRowAdmin)
