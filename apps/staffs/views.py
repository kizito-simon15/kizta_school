from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from django.forms import widgets
from .models import Staff

class StaffListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Staff
    template_name = 'staffs/staff_list.html'
    context_object_name = 'staff_list'
    permission_required = 'staffs.view_staff_list'
    permission_denied_message = "Access Denied"

    def get_queryset(self):
        return Staff.objects.filter(current_status='active')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_male'] = Staff.objects.filter(gender='male').count()
        context['total_female'] = Staff.objects.filter(gender='female').count()
        context['overall_total'] = Staff.objects.count()
        return context

class InactiveStaffListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Staff
    template_name = 'staffs/inactive_staff_list.html'
    context_object_name = 'staff_list'
    permission_required = 'staffs.view_staff_list'
    permission_denied_message = "Access Denied"

    def get_queryset(self):
        return Staff.objects.filter(current_status='inactive')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_male'] = Staff.objects.filter(gender='male').count()
        context['total_female'] = Staff.objects.filter(gender='female').count()
        context['overall_total'] = Staff.objects.count()
        return context

class StaffDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Staff
    template_name = 'staffs/staff_detail.html'
    permission_required = 'staffs.view_staff_detail'  # Permission to view staff details
    permission_denied_message = "Access Denied"

class StaffCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Staff
    fields = '__all__'
    template_name = 'staffs/staff_form.html'
    success_message = 'New staff successfully added'
    permission_required = 'staffs.add_staff'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_of_birth'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['date_of_admission'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['contract_start_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['contract_end_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['address'].widget = forms.widgets.Textarea(attrs={'rows': 1})
        form.fields['others'].widget = forms.widgets.Textarea(attrs={'rows': 1})
        
        # Set initial value for mobile number
        if not form.instance.mobile_number:
            form.fields['mobile_number'].initial = '+255'

        return form

    def form_valid(self, form):
        staff = form.save(commit=False)
        staff.user = self.request.user
        if 'passport_photo' in self.request.FILES:
            staff.passport_photo = self.request.FILES['passport_photo']
        staff.save()

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('staff-list')

class StaffUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Staff
    fields = '__all__'
    template_name = 'staffs/staff_form.html'
    success_message = 'Record successfully updated.'
    permission_required = 'staffs.change_staff'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_of_birth'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['date_of_admission'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['contract_start_date'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['contract_end_date'].widget = widgets.DateInput(attrs={'type': 'date'})
        form.fields['address'].widget = widgets.Textarea(attrs={'rows': 1})
        form.fields['others'].widget = widgets.Textarea(attrs={'rows': 1})
        return form

    def form_valid(self, form):
        staff = form.save(commit=False)
        if 'passport_photo' in self.request.FILES:
            staff.passport_photo = self.request.FILES['passport_photo']
        staff.save()

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('staff-list')

class StaffDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Staff
    success_url = reverse_lazy('staff-list')
    template_name = 'staffs/staff_confirm_delete.html'
    permission_required = 'staffs.delete_staff'  # Permission to delete staff
    permission_denied_message = "Access Denied"

from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from .models import Staff

class SimpleStaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['passport_photo']

from django.shortcuts import render, get_object_or_404, redirect

def test_upload(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    
    if request.method == 'POST':
        if 'passport_photo' in request.FILES:
            staff.passport_photo = request.FILES['passport_photo']
            staff.save()
            return redirect('staff-detail', pk=staff.pk)
    
    return render(request, 'staffs/test_upload.html', {'staff': staff})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.staffs.models import StaffAttendance
from django.utils import timezone
from collections import defaultdict
from django.shortcuts import render
from apps.staffs.models import StaffAttendance
from django.shortcuts import render
from apps.staffs.models import StaffAttendance
from django.shortcuts import render
from apps.staffs.models import StaffAttendance
from datetime import time

def staff_attendance_report(request):
    # Retrieve all attendance records, ordered by date and time of arrival
    attendance_records = StaffAttendance.objects.select_related('user__teacheruser__staff', 'user__bursoruser__staff', 'user__secretaryuser__staff', 'user__academicuser__staff').all().order_by('-date', 'time_of_arrival')

    # Group attendance records by date
    grouped_attendance = {}
    for record in attendance_records:
        date_key = record.date  # Using the date field directly
        if date_key not in grouped_attendance:
            grouped_attendance[date_key] = []
        
        # Determine tick color based on time of arrival
        if record.time_of_arrival:
            if time(0, 0) <= record.time_of_arrival < time(7, 30):
                record.tick_color = "blue-ticks"
            else:
                record.tick_color = "red-ticks"
        else:
            record.tick_color = None
        
        grouped_attendance[date_key].append(record)

    context = {
        'grouped_attendance': grouped_attendance
    }

    return render(request, 'staffs/staff_attendance_report.html', context)
