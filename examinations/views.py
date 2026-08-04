from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from .forms import (
    ExaminationTypeForm,
    ExaminationForm,
    ExaminationSemesterForm,
    AssessmentWindowForm,
)
from .models import (
    ExaminationType,
    Examination,
    ExaminationSemester,
    AssessmentWindow,
)

@login_required
def examination_type_list(request):

    examination_types = ExaminationType.objects.all()

    return render(
        request,
        "examinations/examination_type_list.html",
        {
            "examination_types": examination_types,
        },
    )

@login_required
def examination_type_create(request):

    if request.method == "POST":

        form = ExaminationTypeForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "examination_type_list"
            )

    else:

        form = ExaminationTypeForm()

    return render(
        request,
        "examinations/examination_type_form.html",
        {
            "form": form,
        },
    )

@login_required
def examination_create(request):

    if request.method == "POST":

        form = ExaminationForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("examination_list")

    else:

        form = ExaminationForm()

    return render(
        request,
        "examinations/examination_form.html",
        {
            "form": form,
        },
    )

@login_required
def examination_update(request, pk):

    examination = Examination.objects.get(pk=pk)

    if request.method == "POST":

        form = ExaminationForm(
            request.POST,
            instance=examination,
        )

        if form.is_valid():

            form.save()

            return redirect("examination_list")

    else:

        form = ExaminationForm(
            instance=examination,
        )

    return render(
        request,
        "examinations/examination_form.html",
        {
            "form": form,
        },
    )

@login_required
def examination_list(request):

    examinations = Examination.objects.all()

    return render(
        request,
        "examinations/examination_list.html",
        {
            "examinations": examinations,
        },
    )


def examination_semester_list(request):

    mappings = (
        ExaminationSemester.objects
        .select_related("examination")
        .order_by(
            "examination",
            "semester",
        )
    )

    return render(
        request,
        "examinations/examination_semester_list.html",
        {
            "mappings": mappings,
        },
    )


def examination_semester_create(request):

    if request.method == "POST":

        form = ExaminationSemesterForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "examination_semester_list"
            )

    else:

        form = ExaminationSemesterForm()

    return render(
        request,
        "examinations/examination_semester_form.html",
        {
            "form": form,
        },
    )

@login_required
def assessment_window_list(request):

    windows = (
        AssessmentWindow.objects
        .select_related("examination")
        .order_by(
            "examination",
            "start_date",
        )
    )

    return render(
        request,
        "examinations/assessment_window_list.html",
        {
            "windows": windows,
        },
    )

@login_required
def assessment_window_create(request):

    if request.method == "POST":

        form = AssessmentWindowForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "assessment_window_list"
            )

    else:

        form = AssessmentWindowForm()

    return render(
        request,
        "examinations/assessment_window_form.html",
        {
            "form": form,
        },
    )

@login_required
def assessment_window_update(request, pk):

    window = AssessmentWindow.objects.get(pk=pk)

    if request.method == "POST":

        form = AssessmentWindowForm(
            request.POST,
            instance=window,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "assessment_window_list"
            )

    else:

        form = AssessmentWindowForm(
            instance=window,
        )

    return render(
        request,
        "examinations/assessment_window_form.html",
        {
            "form": form,
        },
    )

@login_required
def assessment_window_delete(request, pk):

    window = AssessmentWindow.objects.get(pk=pk)

    if request.method == "POST":

        window.delete()

        return redirect(
            "assessment_window_list"
        )

    return render(
        request,
        "examinations/assessment_window_confirm_delete.html",
        {
            "window": window,
        },
    )
