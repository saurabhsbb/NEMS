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

    path(
        "student/",
        views.student_hall_tickets,
        name="student_hall_tickets",
    ),

    path(
        "student/<int:examination_id>/",
        views.student_hall_ticket,
        name="student_hall_ticket",
    ),
]
