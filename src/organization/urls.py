from django.urls import path, include
from rest_framework import routers
from organization.views import ResetPasswordView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView



from . import api
from . import views


router = routers.DefaultRouter()
router.register("EventMembership", api.EventMembershipViewSet)
router.register("Event", api.EventViewSet)
router.register("Team", api.TeamViewSet)
router.register("TeamMembership", api.TeamMembershipViewSet)
router.register("Volunteer", api.VolunteerViewSet)


urlpatterns = [
    path('', views.home, name="home"),
    path('login_user', views.login_user, name="login_user"),
    path('logout_user', views.logout_user, name='logout_user'),
    path('register_user', views.register_user, name='register_user'),
    path('password-reset', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='organization/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='organization/password_reset_complete.html'),
        name='password_reset_complete'),
    path("api/v1/", include(router.urls)),
    path("organization/EventMembership/", 
         views.EventMembershipListView.as_view(), 
         name="organization_EventMembership_list"),
    path("organization/EventMembership/create/", 
         views.EventMembershipCreateView.as_view(), 
         name="organization_EventMembership_create"),
    path("organization/EventMembership/detail/<int:pk>/", 
         views.EventMembershipDetailView.as_view(), 
         name="organization_EventMembership_detail"),
    path("organization/EventMembership/update/<int:pk>/", 
         views.EventMembershipUpdateView.as_view(), 
         name="organization_EventMembership_update"),
    path("organization/EventMembership/delete/<int:pk>/", 
         views.EventMembershipDeleteView.as_view(), 
         name="organization_EventMembership_delete"),
    path("organization/Event/", 
         views.EventListView.as_view(), 
         name="organization_Event_list"),
    path("organization/Event/create/", views.EventCreateView.as_view(), name="organization_Event_create"),
    path("organization/Event/detail/<int:pk>/", views.EventDetailView.as_view(), name="organization_Event_detail"),
    path("organization/Event/update/<int:pk>/", views.EventUpdateView.as_view(), name="organization_Event_update"),
    path("organization/Event/delete/<int:pk>/", views.EventDeleteView.as_view(), name="organization_Event_delete"),
    path("organization/Team/", views.TeamListView.as_view(), name="organization_Team_list"),
    path("organization/Team/create/", views.TeamCreateView.as_view(), name="organization_Team_create"),
    path("organization/Team/detail/<int:pk>/", views.TeamDetailView.as_view(), name="organization_Team_detail"),
    path("organization/Team/update/<int:pk>/", views.TeamUpdateView.as_view(), name="organization_Team_update"),
    path("organization/Team/delete/<int:pk>/", views.TeamDeleteView.as_view(), name="organization_Team_delete"),
    path("organization/TeamMembership/", views.TeamMembershipListView.as_view(), name="organization_TeamMembership_list"),
    path("organization/TeamMembership/create/", views.TeamMembershipCreateView.as_view(), name="organization_TeamMembership_create"),
    path("organization/TeamMembership/detail/<int:pk>/", views.TeamMembershipDetailView.as_view(), name="organization_TeamMembership_detail"),
    path("organization/TeamMembership/update/<int:pk>/", views.TeamMembershipUpdateView.as_view(), name="organization_TeamMembership_update"),
    path("organization/TeamMembership/delete/<int:pk>/", views.TeamMembershipDeleteView.as_view(), name="organization_TeamMembership_delete"),
    path("organization/Volunteer/", views.VolunteerListView.as_view(), name="organization_Volunteer_list"),
    path("organization/Volunteer/create/", views.VolunteerCreateView.as_view(), name="organization_Volunteer_create"),
    path("organization/Volunteer/detail/<int:pk>/", views.VolunteerDetailView.as_view(), name="organization_Volunteer_detail"),
    path("organization/Volunteer/update/<int:pk>/", views.VolunteerUpdateView.as_view(), name="organization_Volunteer_update"),
    path("organization/Volunteer/delete/<int:pk>/", views.VolunteerDeleteView.as_view(), name="organization_Volunteer_delete"),
]