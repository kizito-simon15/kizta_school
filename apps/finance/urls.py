from django.urls import path
from .views import (
    InvoiceCreateView,
    InvoiceDeleteView,
    InvoiceDetailView,
    InvoiceListView,
    InvoiceUpdateView,
    ReceiptCreateView,
    ReceiptUpdateView,
    bulk_invoice,
    SalaryInvoiceListView,
    SalaryInvoiceDetailView,
    SalaryInvoiceCreateView,
    SalaryInvoiceUpdateView,
    SalaryInvoiceDeleteView,
    print_pdf,
    save_pdf,
    salary_list,
    SearchStudents,
    receipt_view,
    generate_receipt,
    uniform_list, uniform_create, uniform_update, uniform_delete,
    student_uniform_list, student_uniform_create, student_uniform_update, student_uniform_delete,
    student_info_api, SelectLinkView, uniform_detail,
    UniformTypeListView, 
    UniformTypeCreateView, 
    UniformTypeUpdateView,
    UniformTypeDeleteView,
    get_uniform_price,
    get_student_class,
    initiate_payment, 
    mpesa_callback,
    student_search
)

urlpatterns = [
    # Student Invoice URLs
    path("list/", InvoiceListView.as_view(), name="invoice-list"),
    path("create/", InvoiceCreateView.as_view(), name="invoice-create"),
    path("<int:pk>/detail/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("<int:pk>/update/", InvoiceUpdateView.as_view(), name="invoice-update"),
    path("<int:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice-delete"),
    path("receipt/create", ReceiptCreateView.as_view(), name="receipt-create"),
    path('generate_receipt/<int:pk>/', generate_receipt, name='generate_receipt'),
    path("receipt/<int:pk>/update/", ReceiptUpdateView.as_view(), name="receipt-update"),
    path("bulk-invoice/", bulk_invoice, name="bulk-invoice"),

    # Salary Invoice URLs
    path('invoices/', SalaryInvoiceListView.as_view(), name='salary-invoice-list'),
    path('search-students/', SearchStudents.as_view(), name='search_students'),
    path('invoices/print/', print_pdf, name='print-pdf'),
    path('save-pdf/', save_pdf, name='save-pdf'),
    path('salary-list/', salary_list, name='salary_list'),
    path('invoices/<int:pk>/', SalaryInvoiceDetailView.as_view(), name='salary-invoice-detail'),
    path('invoices/create/', SalaryInvoiceCreateView.as_view(), name='salary-invoice-create'),
    path('invoices/<int:pk>/update/', SalaryInvoiceUpdateView.as_view(), name='salary-invoice-update'),
    path('invoices/<int:pk>/delete/', SalaryInvoiceDeleteView.as_view(), name='salary-invoice-delete'),
    path('receipt/', receipt_view, name='receipt'),
    
    # Uniforms
    path('uniforms/', uniform_list, name='uniform_list'),
    path('uniforms/create/', uniform_create, name='uniform_create'),
    path('uniforms/<int:pk>/update/', uniform_update, name='uniform_update'),
    path('uniforms/<int:pk>/delete/', uniform_delete, name='uniform_delete'),
    path('uniforms/<int:student_id>/detail/', uniform_detail, name='uniform_detail'),

    # Student Uniforms
    path('student_uniforms/', student_uniform_list, name='student_uniform_list'),
    path('student_uniforms/create/<int:student_id>/', student_uniform_create, name='student_uniform_create'),
    path('student_uniforms/<int:pk>/update/', student_uniform_update, name='student_uniform_update'),
    path('student_uniforms/<int:pk>/delete/', student_uniform_delete, name='student_uniform_delete'),

    path('api/student-info/<int:student_id>/', student_info_api, name='student_info_api'),
    path('select-link/', SelectLinkView.as_view(), name='select_link'),
    path('uniformtypes/', UniformTypeListView.as_view(), name='uniformtype_list'),
    path('uniformtypes/add/', UniformTypeCreateView.as_view(), name='uniformtype_add'),
    path('uniformtypes/<int:pk>/edit/', UniformTypeUpdateView.as_view(), name='uniformtype_edit'),
    path('uniformtypes/<int:pk>/delete/', UniformTypeDeleteView.as_view(), name='uniformtype_delete'),
    path('uniform/get_price/', get_uniform_price, name='get_uniform_price'),

    # AJAX endpoints for modernized invoice form
    path('student-search/', student_search, name='student-search'),
    path('get-student-class/', get_student_class, name='get-student-class'),

    # Payment
    path('initiate-payment/', initiate_payment, name='initiate_payment'),
    path('mpesa-callback/', mpesa_callback, name='mpesa_callback'),
]

