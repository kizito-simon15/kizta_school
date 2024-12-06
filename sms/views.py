from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.db import transaction
from .beem_service import send_sms, check_balance
from apps.students.models import Student
from apps.staffs.models import Staff
from .models import SentSMS

"""
class SendSMSFormView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'sms.send_sms'

    def get(self, request):
        students = Student.objects.filter(current_status="active", completed=False)
        staff = Staff.objects.filter(current_status="active")
        return render(request, 'send_sms.html', {'students': students, 'staff': staff})

    def post(self, request):
        message = request.POST.get('message')
        recipient_type = request.POST.get('recipient_type')
        recipients = []

        if recipient_type == 'students':
            student_recipients = request.POST.getlist('student_recipients')
            for student_id in student_recipients:
                student = Student.objects.get(id=student_id)
                if student.father_mobile_number:
                    recipients.append({
                        "dest_addr": student.father_mobile_number,
                        "first_name": student.firstname,
                        "last_name": student.surname
                    })
                if student.mother_mobile_number:
                    recipients.append({
                        "dest_addr": student.mother_mobile_number,
                        "first_name": student.firstname,
                        "last_name": student.surname
                    })
        elif recipient_type == 'staff':
            staff_recipients = request.POST.getlist('staff_recipients')
            recipients = [
                {
                    "dest_addr": staff_member.mobile_number,
                    "first_name": staff_member.firstname,
                    "last_name": staff_member.surname
                } for staff_member in Staff.objects.filter(mobile_number__in=staff_recipients)
            ]

        if not recipients:
            messages.error(request, 'No recipients selected.')
            # Ensure only active and non-completed students and active staff are reloaded in the form
            return render(request, 'send_sms.html', {
                'students': Student.objects.filter(current_status="active", completed=False),
                'staff': Staff.objects.filter(current_status="active")
            })

        try:
            response = send_sms(message, recipients)
            if response.get('error'):
                messages.error(request, 'Failed to send SMS: ' + response['error'])
            else:
                messages.success(request, 'SMS sent successfully!')
            return redirect('send_sms_form')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return redirect('send_sms_form')
"""

from apps.corecode.models import StudentClass

class SendSMSFormView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'sms.send_sms'

    def get(self, request):
        students = Student.objects.filter(current_status="active", completed=False)
        staff = Staff.objects.filter(current_status="active")
        classes = StudentClass.objects.all()  # Fetch all classes
        return render(request, 'send_sms.html', {
            'students': students,
            'staff': staff,
            'classes': classes
        })

    def post(self, request):
        message = request.POST.get('message')
        recipient_type = request.POST.get('recipient_type')
        recipients = []

        if recipient_type == 'students':
            student_recipients = request.POST.getlist('student_recipients')
            for student_id in student_recipients:
                student = Student.objects.get(id=student_id)
                if student.father_mobile_number:
                    recipients.append({
                        "dest_addr": student.father_mobile_number,
                        "first_name": student.firstname,
                        "last_name": student.surname
                    })
                if student.mother_mobile_number:
                    recipients.append({
                        "dest_addr": student.mother_mobile_number,
                        "first_name": student.firstname,
                        "last_name": student.surname
                    })
        elif recipient_type == 'staff':
            staff_recipients = request.POST.getlist('staff_recipients')
            recipients = [
                {
                    "dest_addr": staff_member.mobile_number,
                    "first_name": staff_member.firstname,
                    "last_name": staff_member.surname
                } for staff_member in Staff.objects.filter(mobile_number__in=staff_recipients)
            ]

        if not recipients:
            messages.error(request, 'No recipients selected.')
            # Ensure only active and non-completed students and active staff are reloaded in the form
            return render(request, 'send_sms.html', {
                'students': Student.objects.filter(current_status="active", completed=False),
                'staff': Staff.objects.filter(current_status="active"),
                'classes': StudentClass.objects.all()
            })

        try:
            response = send_sms(message, recipients)
            if response.get('error'):
                messages.error(request, 'Failed to send SMS: ' + response['error'])
            else:
                messages.success(request, 'SMS sent successfully!')
            return redirect('send_sms_form')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return redirect('send_sms_form')

class SMSHistoryView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'sms.view_sms_history'

    def get(self, request):
        # Filter to get only sent messages
        messages_query = SentSMS.objects.filter(status='Sent').order_by('-sent_date')

        # Use a set to track unique messages and filter out duplicates
        seen = set()
        unique_messages = []
        for message in messages_query:
            identifier = (
                message.status,
                message.sent_date,
                message.first_name,
                message.last_name,
                message.dest_addr,
                message.message
            )
            if identifier not in seen:
                seen.add(identifier)
                unique_messages.append(message)

        total_sms = len(unique_messages)

        context = {
            'messages': unique_messages,
            'total_sms': total_sms
        }
        return render(request, 'sms_history.html', context)

    def post(self, request):
        sms_ids = request.POST.getlist('sms_ids')
        if sms_ids:
            with transaction.atomic():
                deleted_count, _ = SentSMS.objects.filter(id__in=sms_ids).delete()
                messages.success(request, f'Successfully deleted {deleted_count} messages.')
        else:
            messages.error(request, 'No messages selected for deletion.')
        return redirect('sms_history')


class CheckBalanceView(View):
    def get(self, request):
        try:
            response = check_balance()
            if "error" in response:
                return render(request, 'check_balance.html', {'error': response['error']})
            return render(request, 'check_balance.html', {'balance': response.get('data', {}).get('credit_balance', 'N/A')})
        except Exception as e:
            return render(request, 'check_balance.html', {'error': str(e)})

@method_decorator(require_POST, name='dispatch')
class DeleteSMSView(View):
    def post(self, request):
        sms_ids = request.POST.getlist('sms_ids')
        if sms_ids:
            with transaction.atomic():
                deleted_count, _ = SentSMS.objects.filter(id__in=sms_ids).delete()
                messages.success(request, f'Successfully deleted {deleted_count} messages.')
        else:
            messages.error(request, 'No messages selected for deletion.')
        return redirect('sms_history')