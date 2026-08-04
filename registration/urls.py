from django.urls import path

from . import views


urlpatterns = [

    path(
        "student/semester-registration/",
        views.semester_registration,
        name="semester_registration",
    ),

    path(
        "student/examination-registration/",
        views.examination_registration,
        name="examination_registration",
    ),

    path(
        "coe/pending-exam-registrations/",
        views.coe_pending_exam_registrations,
        name="coe_pending_exam_registrations",
    ),

    path(
        "coe/review-exam-registration/<int:registration_id>/",
        views.coe_review_exam_registration,
        name="coe_review_exam_registration",
    ),

    path(
        "student/review-registration/",
        views.review_registration,
        name="review_registration",
    ),

    path(
        "student/submit-registration/",
        views.submit_registration,
        name="submit_registration",
    ),

    path(
        "depm/pending-registrations/",
        views.depm_pending_registrations,
        name="depm_pending_registrations",
    ),

    path(
        "depm/review-registration/<int:registration_id>/",
        views.depm_review_registration,
        name="depm_review_registration",
    ),
]
