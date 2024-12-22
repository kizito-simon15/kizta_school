import sys
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import HttpResponseRedirect, get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from datetime import time

from .models import Staff, StaffAttendance
from .forms import StaffForm, StaffAttendanceForm
from accounts.models import CustomUser

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
    permission_required = 'staffs.view_staff_detail'
    permission_denied_message = "Access Denied"


class StaffCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'staffs/staff_form.html'
    success_message = 'New staff successfully added'
    permission_required = 'staffs.add_staff'

    def form_valid(self, form):
        staff = form.save(commit=False)
        if 'passport_photo' in self.request.FILES:
            staff.passport_photo = self.request.FILES['passport_photo']
        staff.save()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # Print form errors to the terminal
        print("Form Invalid:", file=sys.stderr)
        for field, errors in form.errors.items():
            print(f"Field: {field} - Errors: {errors}", file=sys.stderr)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('staff-list')


class StaffUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'staffs/staff_form.html'
    success_message = 'Record successfully updated.'
    permission_required = 'staffs.change_staff'

    def form_valid(self, form):
        staff = form.save(commit=False)
        if 'passport_photo' in self.request.FILES:
            staff.passport_photo = self.request.FILES['passport_photo']
        staff.save()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # Print form errors to the terminal
        print("Form Invalid (Update):", file=sys.stderr)
        for field, errors in form.errors.items():
            print(f"Field: {field} - Errors: {errors}", file=sys.stderr)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('staff-list')


class StaffDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Staff
    success_url = reverse_lazy('staff-list')
    template_name = 'staffs/staff_confirm_delete.html'
    permission_required = 'staffs.delete_staff'
    permission_denied_message = "Access Denied"


def staff_attendance_report(request):
    attendance_records = StaffAttendance.objects.select_related('user').all().order_by('-date', 'time_of_arrival')
    grouped_attendance = {}

    for record in attendance_records:
        date_key = record.date
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

