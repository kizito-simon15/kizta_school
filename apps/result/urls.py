from django.urls import path
from .views import create_result, edit_results, StudentResultsView, ClassListView, ClassResultsView, SingleClassResultsView, SingleClassListView, SingleStudentResultsView, FormStatusView, admin_profile
from . import views

urlpatterns = [
    path("create/", create_result, name="create-result"),
    path("edit-results/", edit_results, name="edit-results"),
    path("edit-now-results/", views.edit_now_results, name="edit-now-results"),
    path('delete-page-results/', views.delete_page_results, name='delete-page-results'),
    path('student/<int:student_id>/results/', StudentResultsView.as_view(), name='student-results'),
    path('form-status/<int:class_id>/', FormStatusView.as_view(), name='form_status'),
    path('class/', ClassListView.as_view(), name='class-list'),
    path('class/results/<int:class_id>/', ClassResultsView.as_view(), name='class-results'),
    path('single/class/list', SingleClassListView.as_view(), name='single-class'),
    path('single/class/result/<int:class_id>/', SingleClassResultsView.as_view(), name='single-results'),
    path('single/student/results/<int:student_id>/', SingleStudentResultsView.as_view(), name='single-student'),
    path('admin/profile/', admin_profile, name='admin_profile'),
]