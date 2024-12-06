import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ParentUserCreationForm
from .models import ParentUser
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView as DefaultLoginView
from .models import ParentUser, TeacherUser, BursorUser, SecretaryUser, AcademicUser, CustomUser
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ParentUserCreationForm
from .models import ParentUser
from apps.students.models import Student
from sms.models import SentSMS
from sms.beem_service import send_sms
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.utils import timezone
from geopy.distance import geodesic
from location.models import SchoolLocation

"""
logger = logging.getLogger(__name__)

class CustomLoginView(DefaultLoginView):
    form_class = AuthenticationForm
    template_name = "registration/login.html"

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        user = form.get_user()
        logger.debug(f'User {user.username} logged in')

        if user.is_superuser:
            logger.debug('Redirecting to admin:index')
            return redirect('home')
        elif hasattr(user, 'parentuser'):
            logger.debug('Redirecting to parent_dashboard')
            return redirect('parent_dashboard')
        elif hasattr(user, 'teacheruser'):
            logger.debug('Redirecting to teacher_dashboard')
            return redirect('teacher_dashboard')
        elif hasattr(user, 'bursoruser'):
            logger.debug('Redirecting to bursor_dashboard')
            return redirect('bursor_dashboard')
        elif hasattr(user, 'secretaryuser'):
            logger.debug('Redirecting to secretary_dashboard')
            return redirect('secretary_dashboard')
        elif hasattr(user, 'academicuser'):
            logger.debug('Redirecting to academic_dashboard')
            return redirect('academic_dashboard')
        else:
            logger.debug('Redirecting to home')
            return redirect('home')
"""
"""
from django.utils import timezone
from geopy.distance import geodesic

logger = logging.getLogger(__name__)
"""
"""
class CustomLoginView(DefaultLoginView):
    form_class = AuthenticationForm
    template_name = "registration/login.html"

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)
        logger.debug(f'User {user.username} logged in')

        # Check if the user is a staff member
        if hasattr(user, 'teacheruser') or hasattr(user, 'bursoruser') or hasattr(user, 'secretaryuser') or hasattr(user, 'academicuser'):
            school_location = SchoolLocation.objects.filter(is_active=True).first()  # Fetch the active school location

            if not school_location:
                # If no school location is configured, allow login without restrictions
                logger.debug('No school location configured, allowing unrestricted login.')
                return self.redirect_user(user)

            # Get the current day and time
            current_day = timezone.now().strftime('%A')
            current_time = timezone.now().time()

            # Get the latitude and longitude from the user's input or browser
            try:
                current_latitude = float(self.request.POST.get('latitude', 0))
                current_longitude = float(self.request.POST.get('longitude', 0))
            except ValueError:
                messages.error(self.request, "Unable to retrieve your current location.")
                return redirect('login')

            # Calculate the distance between the current location and the school location
            distance = geodesic(
                (school_location.latitude, school_location.longitude),
                (current_latitude, current_longitude)
            ).meters

            # Check if the user is within the allowed radius
            if distance > float(school_location.distance):  # Use the stored distance
                messages.error(self.request, f"You are not within the allowed school location radius of {school_location.distance} meters.")
                return redirect('login')

            # Adjust the day logic to account for wraparound (e.g., Friday to Monday)
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            start_day_index = days_of_week.index(school_location.start_day)
            end_day_index = days_of_week.index(school_location.end_day)
            current_day_index = days_of_week.index(current_day)

            # Check if the current day is within the allowed range
            if start_day_index <= end_day_index:
                valid_day = start_day_index <= current_day_index <= end_day_index
            else:
                valid_day = current_day_index >= start_day_index or current_day_index <= end_day_index

            # Check if the current time is within the allowed range
            valid_time = school_location.start_time <= current_time <= school_location.end_time

            if not (valid_day and valid_time):
                messages.error(self.request, "You are not allowed to access the system at this time.")
                return redirect('login')

        return self.redirect_user(user)

    def redirect_user(self, user):
        # Redirect to the appropriate dashboard
        if user.is_superuser:
            logger.debug('Redirecting to admin:index')
            return redirect('home')
        elif hasattr(user, 'parentuser'):
            logger.debug('Redirecting to parent_dashboard')
            return redirect('parent_dashboard')
        elif hasattr(user, 'teacheruser'):
            logger.debug('Redirecting to teacher_dashboard')
            return redirect('teacher_dashboard')
        elif hasattr(user, 'bursoruser'):
            logger.debug('Redirecting to bursor_dashboard')
            return redirect('bursor_dashboard')
        elif hasattr(user, 'secretaryuser'):
            logger.debug('Redirecting to secretary_dashboard')
            return redirect('secretary_dashboard')
        elif hasattr(user, 'academicuser'):
            logger.debug('Redirecting to academic_dashboard')
            return redirect('academic_dashboard')
        else:
            logger.debug('Redirecting to home')
            return redirect('home')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid login details.")
        return self.render_to_response(self.get_context_data(form=form))
"""

from django.utils import timezone
from geopy.distance import geodesic

logger = logging.getLogger(__name__)

class CustomLoginView(DefaultLoginView):
    form_class = AuthenticationForm
    template_name = "registration/login.html"

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)
        logger.debug(f'User {user.username} logged in')

        # Check if the user is a staff member
        if hasattr(user, 'teacheruser') or hasattr(user, 'bursoruser') or hasattr(user, 'secretaryuser') or hasattr(user, 'academicuser'):
            school_location = SchoolLocation.objects.filter(is_active=True).first()  # Fetch the active school location

            if not school_location:
                # If no school location is configured, allow login without restrictions
                logger.debug('No school location configured, allowing unrestricted login.')
                return self.redirect_user(user)

            # Get the current day and time
            current_day = timezone.now().strftime('%A')
            current_time = timezone.now().time()

            # Get the latitude and longitude from the user's input or browser
            try:
                current_latitude = float(self.request.POST.get('latitude', 0))
                current_longitude = float(self.request.POST.get('longitude', 0))
            except ValueError:
                messages.error(self.request, "Unable to retrieve your current location.")
                return redirect('login')

            # Calculate the distance between the current location and the school location
            user_distance = geodesic(
                (school_location.latitude, school_location.longitude),
                (current_latitude, current_longitude)
            ).meters

            # Check if the user is within the allowed radius
            required_radius = float(school_location.distance)
            if user_distance > required_radius:
                # Calculate how far the user is from the required radius
                distance_away = user_distance - required_radius
                messages.error(
                    self.request, 
                    f"You are {distance_away:.2f} meters away from the allowed school location radius of {required_radius} meters."
                )
                return redirect('login')

            # Adjust the day logic to account for wraparound (e.g., Friday to Monday)
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            start_day_index = days_of_week.index(school_location.start_day)
            end_day_index = days_of_week.index(school_location.end_day)
            current_day_index = days_of_week.index(current_day)

            # Check if the current day is within the allowed range
            if start_day_index <= end_day_index:
                valid_day = start_day_index <= current_day_index <= end_day_index
            else:
                valid_day = current_day_index >= start_day_index or current_day_index <= end_day_index

            # Check if the current time is within the allowed range
            valid_time = school_location.start_time <= current_time <= school_location.end_time

            if not (valid_day and valid_time):
                messages.error(self.request, "You are not allowed to access the system at this time.")
                return redirect('login')

        return self.redirect_user(user)

    def redirect_user(self, user):
        # Redirect to the appropriate dashboard
        if user.is_superuser:
            logger.debug('Redirecting to admin:index')
            return redirect('home')
        elif hasattr(user, 'parentuser'):
            logger.debug('Redirecting to parent_dashboard')
            return redirect('parent_dashboard')
        elif hasattr(user, 'teacheruser'):
            logger.debug('Redirecting to teacher_dashboard')
            return redirect('teacher_dashboard')
        elif hasattr(user, 'bursoruser'):
            logger.debug('Redirecting to bursor_dashboard')
            return redirect('bursor_dashboard')
        elif hasattr(user, 'secretaryuser'):
            logger.debug('Redirecting to secretary_dashboard')
            return redirect('secretary_dashboard')
        elif hasattr(user, 'academicuser'):
            logger.debug('Redirecting to academic_dashboard')
            return redirect('academic_dashboard')
        else:
            logger.debug('Redirecting to home')
            return redirect('home')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid login details.")
        return self.render_to_response(self.get_context_data(form=form))


@login_required
def superuser_dashboard(request):
    return render(request, 'accounts/superuser_dashboard.html')

@login_required
def parent_dashboard(request):
    return render(request, 'parent_dashboard.html')


@login_required
def create_parent_user(request):
    if request.method == 'POST':
        form = ParentUserCreationForm(request.POST)
        if form.is_valid():
            parent_user = form.save()
            # Send SMS
            student = parent_user.student
            message = (
                f"Habari ndugu mzazi wa {student.firstname} {student.middle_name} {student.surname}, "
                f"pokea taarifa hizi za kukuwezesha kuingia kwenye mfumo wa shule, "
                f"username: {parent_user.username}, password: {request.POST.get('password1')}, "
                "usifute meseji hii kwa msaada piga 0744394080."
            )
            recipients = []

            # Add father's mobile number if it exists
            if student.father_mobile_number:
                recipients.append({
                    "dest_addr": student.father_mobile_number,
                    "first_name": parent_user.parent_first_name,
                    "last_name": parent_user.parent_last_name
                })

            # Add mother's mobile number if it exists
            if student.mother_mobile_number:
                recipients.append({
                    "dest_addr": student.mother_mobile_number,
                    "first_name": parent_user.parent_first_name,
                    "last_name": parent_user.parent_last_name
                })

            try:
                send_sms(message, recipients)
                messages.success(request, 'Parent user created successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Parent user created, but SMS sending failed: {e}')
                
            return redirect('list_users')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ParentUserCreationForm()
    return render(request, 'accounts/create_parent_user.html', {'form': form})
    
    
"""
@login_required
def create_parent_user(request):
    if request.method == 'POST':
        form = ParentUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parent user created successfully.')
            return redirect('list_users')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ParentUserCreationForm()
    return render(request, 'accounts/create_parent_user.html', {'form': form})
"""

@login_required
def parent_user_list(request):
    parent_users = ParentUser.objects.all()
    return render(request, 'accounts/parent_user_list.html', {'parent_users': parent_users})

@login_required
def update_parent_user(request, pk):
    user = get_object_or_404(ParentUser, pk=pk)
    if request.method == 'POST':
        form = ParentUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parent user updated successfully.')
            return redirect('list_users')
    else:
        form = ParentUserCreationForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'user_type': 'Parent'})

@login_required
def delete_parent_user(request, pk):
    user = get_object_or_404(ParentUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Parent user deleted successfully.')
        return redirect('parent_user_list')
    return render(request, 'accounts/delete_parent_user.html', {'user': user})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ParentUserCreationForm, TeacherUserCreationForm, BursorUserCreationForm, SecretaryUserCreationForm, AcademicUserCreationForm
from itertools import chain


@login_required
def select_user_type(request):
    return render(request, 'accounts/select_user_type.html')

@login_required
def create_teacher_user(request):
    if request.method == 'POST':
        form = TeacherUserCreationForm(request.POST)
        if form.is_valid():
            teacher_user = form.save()
            # Send SMS
            staff = teacher_user.staff
            message = (
                f"Hello {staff.firstname} {staff.middle_name} {staff.surname}, "
                f"receive the informations to enter the school management system, "
                f"username: {teacher_user.username}, password: {request.POST.get('password1')}, "
                "don't delete this message, for help call 0744394080."
            )
            recipients = [{
                "dest_addr": staff.mobile_number,  # Assuming you have a mobile number field in the Staff model
                "first_name": staff.firstname,
                "last_name": staff.surname
            }]
            
            try:
                send_sms(message, recipients)
                messages.success(request, 'Teacher user created successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Teacher user created, but SMS sending failed: {e}')
                
            return redirect('select_user_type')
    else:
        form = TeacherUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form, 'user_type': 'Teacher'})


@login_required
def create_bursor_user(request):
    if request.method == 'POST':
        form = BursorUserCreationForm(request.POST)
        if form.is_valid():
            bursor_user = form.save()
            # Send SMS
            staff = bursor_user.staff
            message = (
                f"Hello bursor,{staff.firstname} {staff.middle_name} {staff.surname}, "
                f"receive the informations to enter the school management system, "
                f"username: {bursor_user.username}, password: {request.POST.get('password1')}, "
                "don't delete this message, for help call 0744394080."
            )
            recipients = [{
                "dest_addr": staff.mobile_number,
                "first_name": staff.firstname,
                "last_name": staff.surname
            }]
            
            try:
                send_sms(message, recipients)
                messages.success(request, 'Bursor user created successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Bursor user created, but SMS sending failed: {e}')
                
            return redirect('select_user_type')
    else:
        form = BursorUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form, 'user_type': 'Bursor'})


"""
@login_required
def create_bursor_user(request):
    if request.method == 'POST':
        form = BursorUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bursor user created successfully.')
            return redirect('select_user_type')
    else:
        form = BursorUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form, 'user_type': 'Bursor'})
"""

@login_required
def create_secretary_user(request):
    if request.method == 'POST':
        form = SecretaryUserCreationForm(request.POST)
        if form.is_valid():
            secretary_user = form.save()
            # Send SMS
            staff = secretary_user.staff
            message = (
                f"Hello secretary, {staff.firstname} {staff.middle_name} {staff.surname}, "
                f"receive the informations to enter the school management system, "
                f"username: {secretary_user.username}, password: {request.POST.get('password1')}, "
                "dont delete this message, for help call 0744394080."
            )
            recipients = [{
                "dest_addr": staff.mobile_number,
                "first_name": staff.firstname,
                "last_name": staff.surname
            }]
            
            try:
                send_sms(message, recipients)
                messages.success(request, 'Secretary user created successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Secretary user created, but SMS sending failed: {e}')
                
            return redirect('select_user_type')
    else:
        form = SecretaryUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form, 'user_type': 'Secretary'})
"""

@login_required
def create_secretary_user(request):
    if request.method == 'POST':
        form = SecretaryUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Secretary user created successfully.')
            return redirect('select_user_type')
    else:
        form = SecretaryUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form, 'user_type': 'Secretary'})

"""

@login_required
def create_academic_user(request):
    if request.method == 'POST':
        form = AcademicUserCreationForm(request.POST)
        if form.is_valid():
            academic_user = form.save()
            # Send SMS
            staff = academic_user.staff
            message = (
                f"Hello academic, {staff.firstname} {staff.middle_name} {staff.surname}, "
                f"receive the informations to enter the school management system, "
                f"username: {academic_user.username}, password: {request.POST.get('password1')}, "
                "don't delete this message, for help call 0744394080."
            )
            recipients = [{
                "dest_addr": staff.mobile_number,
                "first_name": staff.firstname,
                "last_name": staff.surname
            }]
            
            try:
                send_sms(message, recipients)
                messages.success(request, 'Academic user created successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Academic user created, but SMS sending failed: {e}')
                
            return redirect('select_user_type')
    else:
        form = AcademicUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form, 'user_type': 'Academic'})


"""
@login_required
def create_academic_user(request):
    if request.method == 'POST':
        form = AcademicUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic user created successfully.')
            return redirect('select_user_type')
    else:
        form = AcademicUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form, 'user_type': 'Academic'})
"""

from itertools import chain

@login_required
def list_users(request):
    account_type = request.GET.get('account_type', 'all')  # Retrieve the account type from query parameters

    parent_users = ParentUser.objects.all()
    teacher_users = TeacherUser.objects.all()
    bursor_users = BursorUser.objects.all()
    secretary_users = SecretaryUser.objects.all()
    academic_users = AcademicUser.objects.all()

    if account_type == 'parent':
        users = parent_users
    elif account_type == 'teacher':
        users = teacher_users
    elif account_type == 'bursor':
        users = bursor_users
    elif account_type == 'secretary':
        users = secretary_users
    elif account_type == 'academic':
        users = academic_users
    else:
        users = chain(parent_users, teacher_users, bursor_users, secretary_users, academic_users)

    context = {
        'parent_users': parent_users,
        'teacher_users': teacher_users,
        'bursor_users': bursor_users,
        'secretary_users': secretary_users,
        'academic_users': academic_users,
        'users': users,
        'account_type': account_type
    }
    return render(request, 'accounts/list_users.html', context)


@login_required
def update_parent_user(request, pk):
    user = get_object_or_404(ParentUser, pk=pk)
    if request.method == 'POST':
        form = ParentUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Send SMS
            student = user.student
            message = (
                f"Habari ndugu mzazi wa {student.firstname} {student.surname}, "
                "pokea maboresho ya taarifa za kuingia kwenye mfumo wa shule, "
                f"username: {user.username}, password: {request.POST.get('password1')}, "
                "usifute meseji hii kwa msaada piga 0762023662."
            )
            recipients = []

            # Add father's mobile number if it exists
            if student.father_mobile_number:
                recipients.append({
                    "dest_addr": student.father_mobile_number,
                    "first_name": user.parent_first_name,
                    "last_name": user.parent_last_name
                })

            # Add mother's mobile number if it exists
            if student.mother_mobile_number:
                recipients.append({
                    "dest_addr": student.mother_mobile_number,
                    "first_name": user.parent_first_name,
                    "last_name": user.parent_last_name
                })

            try:
                send_sms(message, recipients)
                messages.success(request, 'Parent user updated successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Parent user updated, but SMS sending failed: {e}')
                
            return redirect('list_users')
    else:
        form = ParentUserCreationForm(instance=user)
    return render(request, 'accounts/update_user.html', {'form': form, 'user_type': 'Parent'})


@login_required
def update_teacher_user(request, pk):
    user = get_object_or_404(TeacherUser, pk=pk)
    if request.method == 'POST':
        form = TeacherUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Send SMS
            staff = user.staff
            message = (
                f"Hello {staff.firstname} {staff.middle_name} {staff.surname}, "
                "receive the updates of entering the school management system, "
                f"username: {user.username}, password: {request.POST.get('password1')}, "
                "dont delete this message, for help call 0744394080."
            )
            recipients = [{
                "dest_addr": staff.mobile_number,
                "first_name": staff.firstname,
                "last_name": staff.surname
            }]
            
            try:
                send_sms(message, recipients)
                messages.success(request, 'Teacher user updated successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Teacher user updated, but SMS sending failed: {e}')
                
            return redirect('list_users')
    else:
        form = TeacherUserCreationForm(instance=user)
    return render(request, 'accounts/update_user.html', {'form': form, 'user_type': 'Teacher'})

@login_required
def update_bursor_user(request, pk):
    user = get_object_or_404(BursorUser, pk=pk)
    if request.method == 'POST':
        form = BursorUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Send SMS
            staff = user.staff
            message = (
                f"Hello bursor, {staff.firstname} {staff.middle_name} {staff.surname}, "
                "receive the updates of entering the school management system, "
                f"username: {user.username}, password: {request.POST.get('password1')}, "
                "dont delete this message, for help call 0744394080."
            )
            recipients = [{
                "dest_addr": staff.mobile_number,
                "first_name": staff.firstname,
                "last_name": staff.surname
            }]
            
            try:
                send_sms(message, recipients)
                messages.success(request, 'Bursor user updated successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Bursor user updated, but SMS sending failed: {e}')
                
            return redirect('list_users')
    else:
        form = BursorUserCreationForm(instance=user)
    return render(request, 'accounts/update_user.html', {'form': form, 'user_type': 'Bursor'})

@login_required
def update_secretary_user(request, pk):
    user = get_object_or_404(SecretaryUser, pk=pk)
    if request.method == 'POST':
        form = SecretaryUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Send SMS
            staff = user.staff
            message = (
                f"Hello secretary, {staff.firstname} {staff.middle_name} {staff.surname}, "
                "receive the updates of entering the school management system, "
                f"username: {user.username}, password: {request.POST.get('password1')}, "
                "dont delete this message, for help call 0744394080."
            )
            recipients = [{
                "dest_addr": staff.mobile_number,
                "first_name": staff.firstname,
                "last_name": staff.surname
            }]
            
            try:
                send_sms(message, recipients)
                messages.success(request, 'Secretary user updated successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Secretary user updated, but SMS sending failed: {e}')
                
            return redirect('list_users')
    else:
        form = SecretaryUserCreationForm(instance=user)
    return render(request, 'accounts/update_user.html', {'form': form, 'user_type': 'Secretary'})

@login_required
def update_academic_user(request, pk):
    user = get_object_or_404(AcademicUser, pk=pk)
    if request.method == 'POST':
        form = AcademicUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Send SMS
            staff = user.staff
            message = (
                f"Hello academic, {staff.firstname} {staff.middle_name} {staff.surname}, "
                "receive the updates of entering the school management system, "
                f"username: {user.username}, password: {request.POST.get('password1')}, "
                "dont delete this message, for help call 0744394080."
            )
            recipients = [{
                "dest_addr": staff.mobile_number,
                "first_name": staff.firstname,
                "last_name": staff.surname
            }]
            
            try:
                send_sms(message, recipients)
                messages.success(request, 'Academic user updated successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Academic user updated, but SMS sending failed: {e}')
                
            return redirect('list_users')
    else:
        form = AcademicUserCreationForm(instance=user)
    return render(request, 'accounts/update_user.html', {'form': form, 'user_type': 'Academic'})

# Delete Views
@login_required
def delete_parent_user(request, pk):
    user = get_object_or_404(ParentUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Parent user deleted successfully.')
        return redirect('list_users')
    return render(request, 'accounts/delete_user.html', {'user': user, 'user_type': 'Parent'})

@login_required
def delete_teacher_user(request, pk):
    user = get_object_or_404(TeacherUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Teacher user deleted successfully.')
        return redirect('list_users')
    return render(request, 'accounts/delete_user.html', {'user': user, 'user_type': 'Teacher'})

@login_required
def delete_bursor_user(request, pk):
    user = get_object_or_404(BursorUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Bursor user deleted successfully.')
        return redirect('list_users')
    return render(request, 'accounts/delete_user.html', {'user': user, 'user_type': 'Bursor'})

@login_required
def delete_secretary_user(request, pk):
    user = get_object_or_404(SecretaryUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Secretary user deleted successfully.')
        return redirect('list_users')
    return render(request, 'accounts/delete_user.html', {'user': user, 'user_type': 'Secretary'})

@login_required
def delete_academic_user(request, pk):
    user = get_object_or_404(AcademicUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Academic user deleted successfully.')
        return redirect('list_users')
    return render(request, 'accounts/delete_user.html', {'user': user, 'user_type': 'Academic'})

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, ParentUser

@login_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('list_users')  # Adjust the redirect as necessary

@login_required
def toggle_all_parents_status(request):
    parents = ParentUser.objects.all()
    current_status = all([parent.is_active for parent in parents])
    for parent in parents:
        parent.is_active = not current_status
        parent.save()
    return redirect('list_users')  # Adjust the redirect as necessary

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ParentUser, TeacherUser, BursorUser, SecretaryUser, AcademicUser

@login_required
def toggle_parent_status(request, user_id):
    user = get_object_or_404(ParentUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('list_users')

@login_required
def toggle_teacher_status(request, user_id):
    user = get_object_or_404(TeacherUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('list_users')

@login_required
def toggle_bursor_status(request, user_id):
    user = get_object_or_404(BursorUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('list_users')

@login_required
def toggle_secretary_status(request, user_id):
    user = get_object_or_404(SecretaryUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('list_users')

@login_required
def toggle_academic_status(request, user_id):
    user = get_object_or_404(AcademicUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('list_users')

@login_required
def toggle_all_teachers_status(request):
    teachers = TeacherUser.objects.all()
    current_status = all([teacher.is_active for teacher in teachers])
    for teacher in teachers:
        teacher.is_active = not current_status
        teacher.save()
    return redirect('list_users')

@login_required
def toggle_all_bursors_status(request):
    bursors = BursorUser.objects.all()
    current_status = all([bursor.is_active for bursor in bursors])
    for bursor in bursors:
        bursor.is_active = not current_status
        bursor.save()
    return redirect('list_users')

@login_required
def toggle_all_secretaries_status(request):
    secretaries = SecretaryUser.objects.all()
    current_status = all([secretary.is_active for secretary in secretaries])
    for secretary in secretaries:
        secretary.is_active = not current_status
        secretary.save()
    return redirect('list_users')

@login_required
def toggle_all_academics_status(request):
    academics = AcademicUser.objects.all()
    current_status = all([academic.is_active for academic in academics])
    for academic in academics:
        academic.is_active = not current_status
        academic.save()
    return redirect('list_users')
