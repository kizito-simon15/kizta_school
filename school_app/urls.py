# school_app/urls.py
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
import debug_toolbar

def admin_redirect(request):
    return redirect(reverse('admin:index'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path("", include("apps.corecode.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include('accounts.urls')),
    path("student/", include("apps.students.urls")),
    path("staff/", include("apps.staffs.urls")),
    path("finance/", include("apps.finance.urls")),
    path("expenditures/", include("expenditures.urls")),
    path("event/", include("event.urls")),
    path("result/", include("apps.result.urls")),
    path("updations/", include("updations.urls")),
    path("school_properties/", include("school_properties.urls")),
    path('goto-admin/', admin_redirect, name='goto-admin'),
    path("library/", include("library.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("attendance/", include("attendace.urls")),  # Corrected "attendace" to "attendance"
    path('parents/', include('parents.urls')),
    path('bursor/', include('bursor.urls')),
    path('teachers/', include('teachers.urls')),
    path('academic/', include('academic.urls')),
    path('secretary/', include('secretary.urls')),
    path('sms/', include('sms.urls')),
    path('disprine/', include('apps.disprine.urls')),
    path('finance/', include('apps.finance.urls')),  # Ensure finance URLs are included correctly
    path('location/', include('location.urls')),  # Ensure finance URLs are included correctly
    path('analytics/', include('analytics.urls')),
    path('duty/', include('duty.urls')),
    path('meetings/', include('meetings.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
