from django.urls import path

from .views import (
    DownloadCSVViewdownloadcsv,
    StudentBulkUploadView,
    StudentCreateView,
    StudentDeleteView,
    StudentDetailView,
    StudentListView,
    StudentUpdateView,
    InactiveStudentsView,
    SelectAlluiClassView,
    CompletedStudentsView,
    CompletedStudentDetailView,
)

from . import views

urlpatterns = [
    path("list", StudentListView.as_view(), name="student-list"),
    path("<int:pk>/", StudentDetailView.as_view(), name="student-detail"),
    path("create/", StudentCreateView.as_view(), name="student-create"),
    path("<int:pk>/update/", StudentUpdateView.as_view(), name="student-update"),
    path("delete/<int:pk>/", StudentDeleteView.as_view(), name="student-delete"),
    path("upload/", StudentBulkUploadView.as_view(), name="student-upload"),
    path("download-csv/", DownloadCSVViewdownloadcsv.as_view(), name="download-csv"),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student-delete'),
    path('inactive-students/', InactiveStudentsView.as_view(), name='inactive-student-list'),
    path('select-allui-class/', SelectAlluiClassView.as_view(), name='select-allui-class'),
    path('completed-students/', CompletedStudentsView.as_view(), name='completed-students'),
    path('completed-student/<int:pk>/', CompletedStudentDetailView.as_view(), name='completed-student-detail'),
]
