from django.urls import path

from . import views


urlpatterns = [

    path(
        "coe/",
        views.hall_ticket_examinations,
        name="hall_ticket_examinations",
    ),

    path(
        "coe/<int:examination_id>/",
        views.hall_ticket_schedule,
        name="hall_ticket_schedule",
    ),
    
    path(
        "coe/<int:examination_id>/publish/",
        views.hall_ticket_publish,
        name="hall_ticket_publish",
    ),

]
