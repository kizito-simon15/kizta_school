from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.corecode.models import AcademicSession, AcademicTerm, Installment, StudentClass
from apps.students.models import Student
from apps.staffs.models import Staff
# apps/finance/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass

class SalaryInvoice(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    month = models.DateField(default=timezone.now)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Net salary is calculated based on gross salary and deductions
    total_given_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    issued_date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True)
    session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True)  # Add optional session field

    def __str__(self):
        return f"Invoice for {self.staff.surname} {self.staff.firstname} - {self.month.strftime('%B %Y')}"

    def get_absolute_url(self):
        return reverse("salary-invoice-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # Calculate net salary and total given salary before saving
        self.net_salary = self.gross_salary + self.allowance
        self.total_given_salary = self.net_salary - self.deductions
        super().save(*args, **kwargs)

class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default=None)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, default=None)
    installment = models.ForeignKey(Installment, on_delete=models.CASCADE, default=None)
    class_for = models.ForeignKey(StudentClass, on_delete=models.CASCADE, default=None)
    balance_from_previous_install = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("closed", "Closed")],
        default="active",
    )


    class Meta:
        ordering = ["student", "installment"]

    def __str__(self):
        return f"{self.student}"

    def balance(self):
        payable = self.total_amount_payable()
        paid = self.total_amount_paid()
        return payable - paid

    def amount_payable(self):
        items = InvoiceItem.objects.filter(invoice=self)
        total = 0
        for item in items:
            total += item.amount
        return total

    def total_amount_payable(self):
        return self.amount_payable()

    def total_amount_paid(self):
        receipts = Receipt.objects.filter(invoice=self)
        amount = 0
        for receipt in receipts:
            amount += receipt.amount_paid
        return amount

    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"pk": self.pk})

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    amount = models.IntegerField()

class Receipt(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.IntegerField()
    date_paid = models.DateField(default=timezone.now)
    comment = models.CharField(max_length=200, blank=True)

    # Define the choices for payment methods
    PAYMENT_METHOD_CHOICES = [
        ('NMB_BANK', 'NMB BANK'),
        ('M_PESA', 'M-PESA'),
        ('CASH', 'CASH'),
    ]

    # Add the payment_method field
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
    )

    def __str__(self):
        return f"Receipt on {self.date_paid}"

    class Meta:
        get_latest_by = "date_paid"

@receiver(post_save, sender=Receipt)
def update_balance_from_previous_install(sender, instance, **kwargs):
    # Update balance from previous installments when a receipt is saved
    invoice = instance.invoice
    previous_invoices = Invoice.objects.filter(
        student=invoice.student,
        session=invoice.session,
        installment__lt=invoice.installment
    ).order_by('installment')

    for prev_invoice in previous_invoices:
        prev_invoice.balance_from_previous_install
        prev_invoice.save()

class UniformType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Uniform(models.Model):
    QUANTITY_CHOICES = [
        ("Jozi 1", "Jozi 1"),
        ("Jozi 2", "Jozi 2"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    uniform_type = models.ForeignKey(UniformType, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=20, choices=QUANTITY_CHOICES, default="Jozi 2")
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        quantity_multiplier = 2 if self.quantity == "Jozi 2" else 1
        self.price = self.uniform_type.price * quantity_multiplier
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.uniform_type.name} - {self.quantity}"


class StudentUniform(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    transaction_id = models.CharField(max_length=100, unique=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)  # Store additional data like payment type and student ID
    payment_date = models.DateField(default=timezone.now)


    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"
