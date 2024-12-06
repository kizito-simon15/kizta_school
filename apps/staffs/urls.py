from django.urls import path

from .views import (
    StaffCreateView,
    StaffDeleteView,
    StaffDetailView,
    StaffListView,
    StaffUpdateView,
    InactiveStaffListView,
    test_upload,
    staff_attendance_report
)

urlpatterns = [
    path("list/", StaffListView.as_view(), name="staff-list"),
    path("<int:pk>/", StaffDetailView.as_view(), name="staff-detail"),
    path("create/", StaffCreateView.as_view(), name="staff-create"),
    path("<int:pk>/update/", StaffUpdateView.as_view(), name="staff-update"),
    path("<int:pk>/delete/", StaffDeleteView.as_view(), name="staff-delete"),
    path('inactive-staff/', InactiveStaffListView.as_view(), name='inactive-staff-list'),
    path('staff/<int:pk>/upload/', test_upload, name='test_upload'),
    path('staff-attendace-report/', staff_attendance_report, name='staff_attendance_report'),
]
