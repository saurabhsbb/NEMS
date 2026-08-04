from django.urls import path

from . import views

urlpatterns = [

    path(
        "types/",
        views.examination_type_list,
        name="examination_type_list",
    ),

    path(
        "types/add/",
        views.examination_type_create,
        name="examination_type_create",
    ),
    path(
        "add/",
        views.examination_create,
        name="examination_create",
    ),
    
    path(
        "",
        views.examination_list,
        name="examination_list",
    ),
    path(
        "<int:pk>/edit/",
        views.examination_update,
        name="examination_update",
    ),
    path(
        "semester-mapping/",
        views.examination_semester_list,
        name="examination_semester_list",
    ),

    path(
        "semester-mapping/add/",
        views.examination_semester_create,
        name="examination_semester_create",
    ),

    path(
        "assessment-windows/",
        views.assessment_window_list,
        name="assessment_window_list",
    ),

    path(
        "assessment-windows/add/",
        views.assessment_window_create,
        name="assessment_window_create",
    ),

    path(
        "assessment-windows/<int:pk>/edit/",
        views.assessment_window_update,
        name="assessment_window_update",
    ),

    path(
        "assessment-windows/<int:pk>/delete/",
        views.assessment_window_delete,
        name="assessment_window_delete",
    ),
]
