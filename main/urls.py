from django.urls import path
from . import views, admin, forms
from django.contrib.auth.views import LoginView, LogoutView
from datetime import datetime

urlpatterns=[
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='login.html',
             authentication_form=forms.AuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.main_admin.urls,name='admin'),
    path('signup/',views.SignUpView.as_view(),name='signup'),
    path('dashboard/',views.client_dashboard,name='client_dashboard'),
    path('dashboard/create_client',views.createClientView.as_view(),name='create_client'),
    path('dashboard/client_page/<slug:slug>',views.client_page,name="client_page"),
    path('dashboard/client_page/<slug:slug>/edit',views.EditClient.as_view(),name="edit_client"),    
    path('dashboard/client_page/<slug:slug>/new_engagement', views.CreateEngagement.as_view(),name="create_engagement"),
    path('dashboard/client_plage/<slug:slug>/delete',views.ClientDeleteView.as_view(),name="delete_client"),
    path('dashboard/client_page/<slug:slug>/engagement/<slug:Eslug>',views.EngagementView.as_view(),name="engagement_page"),
    path('dashboard/client_page/<slug:slug>/engagement/<slug:Eslug>/edit_eligiblity',views.EditEligibility.as_view(),name="edit_eligibility"),
    path('dashboard/client_page/<slug:slug>/engagement/<slug:Eslug>/key_employees',views.KeyEmployee.as_view(),name="key_employees"),
    path('dashboard/client_page/<slug:slug>/engagement/<slug:Eslug>/census_statistics',views.CensusStatistics.as_view(),name="census_statistics"),
    path('dashboard/client_page/<slug:slug>/engagement/<slug:Eslug>/selections',views.MakeSelections.as_view(),name="make_selections"),
    path('dashboard/client_page/<slug:slug>/engagement/<slug:Eslug>/view_selections',views.ViewSelections.as_view(),name="view_selections"),
    path('dashboard/client_page/<slug:slug>/engagement/<slug:Eslug>/upload_census',views.UploadCensus.as_view(),name="upload_census"), 
    path('dashboard/client_page/<slug:slug>/engagement/<slug:Eslug>/export_selections',views.export_selections,name="export_selections"),   
    
]