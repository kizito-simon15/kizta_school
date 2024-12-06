from django.urls import path
from .views import (
    bursor_dashboard, bursor_profile, bursor_logout, bursor_details, bursor_salary_invoices, bursor_class_list, bursor_class_results, bursor_all_class_list, bursor_all_class_results, BursorInvoiceCreateView, BursorInvoiceDeleteView, BursorInvoiceDetailView, BursorInvoiceListView, BursorInvoiceUpdateView, BursorReceiptCreateView, BursorReceiptUpdateView, bursor_bulk_invoice, BursorSearchStudents, BursorEventListView, BursorStudentDetailView, BursorStudentListView, BursorInactiveStudentsView, BursorCompletedStudentsView, BursorCompletedStudentDetailView, BursorCategoryListView, BursorCategoryDetailView, BursorCategoryCreateView, BursorCategoryUpdateView, BursorCategoryDeleteView, BursorExpenditureCreateView, BursorExpenditureEditView, BursorExpenditureListView, BursorExpenditureDetailView, BursorExpenditureDeleteView, BursorExpenditureInvoiceListView, BursorExpenditureInvoiceCreateView, BursorExpenditureInvoiceDetailView, BursorExpenditureInvoiceUpdateView, BursorExpenditureInvoiceDeleteView, BursorViewAvailableBooksView, BursorBookDetailView, BursorStationeryListView, BursorStationeryDetailView, BursorSendSMSFormView, BursorCheckBalanceView, BursorSMSHistoryView, BursorDeleteSMSView, BursorStaffListView, bursor_uniform_list, bursor_uniform_create, bursor_uniform_update, bursor_uniform_delete, bursor_student_uniform_list, bursor_student_uniform_create, bursor_student_uniform_update, bursor_student_uniform_delete, bursor_uniform_detail, BursorCommentsListView, bursor_parent_user_list, bursor_create_parent_user, bursor_update_parent_user, bursor_delete_parent_user, BursorUniformTypeListView, BursorUniformTypeCreateView, BursorUniformTypeUpdateView, BursorUniformTypeDeleteView, bursor_get_uniform_price, mark_attendance, bursor_get_student_class, mark_comment_as_satisfied, BursorReceiptDetailView, bursor_staff_management_home
)

from . import views

urlpatterns = [
    path('bursor/dashboard/', bursor_dashboard, name='bursor_dashboard'),
    path('dashboard/bursor/mark-attendance/', mark_attendance, name='mark_attendance'),
    path('bursor/profile/', bursor_profile, name='bursor_profile'),
    path('bursor/logout/', bursor_logout, name='bursor_logout'),
    path('bursor/details/', bursor_details, name='bursor_details'),
    path('bursor/salary/invoices/', bursor_salary_invoices, name='bursor_salary_invoices'),
    path('bursor/classes/', bursor_class_list, name='bursor_class_list'),
    path('bursor/classes/<int:class_id>/results/', bursor_class_results, name='bursor_class_results'),
    path('all/bursors/classes/', bursor_all_class_list, name='bursor_all_class_list'),
    path('all/bursors/classes/<int:class_id>/results/', bursor_all_class_results, name='bursor_all_class_results'),
    
    path("bursor/finance/list/", BursorInvoiceListView.as_view(), name="bursor-invoice-list"),
    path("bursor/create/", BursorInvoiceCreateView.as_view(), name="bursor-invoice-create"),
    path("<int:pk>/bursor/detail/", BursorInvoiceDetailView.as_view(), name="bursor-invoice-detail"),
    path("<int:pk>/update/", BursorInvoiceUpdateView.as_view(), name="bursor-invoice-update"),
    path("<int:pk>/delete/", BursorInvoiceDeleteView.as_view(), name="bursor-invoice-delete"),
    
    path("receipt/create", BursorReceiptCreateView.as_view(), name="bursor-receipt-create"),
    path("receipt/<int:pk>/update/", BursorReceiptUpdateView.as_view(), name="bursor-receipt-update"),
    
    path("bulk-invoice/", bursor_bulk_invoice, name="bursor-bulk-invoice"),
    
    path('search-students/', BursorSearchStudents.as_view(), name='bursor_search_students'),
    path('bursor/event/list/', BursorEventListView.as_view(), name='bursor_event_list_view'),
    
    path("bursor/list/", BursorStudentListView.as_view(), name="bursor-student-list"),
    path("bursor/<int:pk>/", BursorStudentDetailView.as_view(), name="bursor-student-detail"),
    path('bursor/inactive-students/', BursorInactiveStudentsView.as_view(), name='bursor-inactive-student-list'),
    path('bursor-completed-students/', BursorCompletedStudentsView.as_view(), name='bursor-completed-students'),
    path('bursor-completed-student/<int:pk>/', BursorCompletedStudentDetailView.as_view(), name='bursor-completed-student-detail'),
    
    path('bursor/categories/', BursorCategoryListView.as_view(), name='bursor_category_list'),
    path('bursor/categories/create/', BursorCategoryCreateView.as_view(), name='bursor_category_create'),
    path('bursor/categories/<int:pk>/', BursorCategoryDetailView.as_view(), name='bursor_category_detail'),
    path('bursor/category/<int:pk>/update/', BursorCategoryUpdateView.as_view(), name='bursor_category_update'),
    path('bursor/category/<int:pk>/delete/', BursorCategoryDeleteView.as_view(), name='bursor_category_delete'),
    
    path('bursor/expenditures/', BursorExpenditureListView.as_view(), name='bursor_expenditure_list'),
    path('bursor/expenditures/create/', BursorExpenditureCreateView.as_view(), name='bursor_expenditure_create'),
    path('bursor/expenditures/create/<int:pk>/', BursorExpenditureCreateView.as_view(), name='bursor_expenditure_create'),
    path('bursor/expenditure/<int:pk>/edit/', BursorExpenditureEditView.as_view(), name='bursor_expenditure_edit'),
    path('bursor/expenditures/<int:pk>/', BursorExpenditureDetailView.as_view(), name='bursor_expenditure_detail'),
    path('bursor/expenditures/<int:pk>/delete/', BursorExpenditureDeleteView.as_view(), name='bursor_expenditure_delete'),
    
    path('bursor/invoices/', BursorExpenditureInvoiceListView.as_view(), name='bursor-expenditure-invoice-list'),
    path('bursor/invoices/create/', BursorExpenditureInvoiceCreateView.as_view(), name='bursor-expenditure-invoice-create'),
    path('bursor-expenditure-invoice/<int:pk>/edit/', BursorExpenditureInvoiceUpdateView.as_view(), name='bursor-expenditure-invoice-edit'),
    path('bursor/expenditures/invoices/<int:pk>/', BursorExpenditureInvoiceDetailView.as_view(), name='bursor-expenditure-invoice-detail'),
    path('bursor/expenditures/invoices/<int:pk>/delete/', BursorExpenditureInvoiceDeleteView.as_view(), name='bursor-expenditure-invoice-delete'),
    path('bursor_view_available_books/', BursorViewAvailableBooksView.as_view(), name='bursor_view_available_books'),
    path('bursor_book_detail/<int:book_id>/', BursorBookDetailView.as_view(), name='bursor_book_detail'),
    path('bursor_stationery_list/', BursorStationeryListView.as_view(), name='bursor_stationery_list'),
    path('bursor_stationery_detail/<int:stationery_id>/', BursorStationeryDetailView.as_view(), name='bursor_stationery_detail'),
    path('bursor/properties/', views.bursor_property_list, name='bursor_property_list'),
    path('bursor/properties/<int:pk>/', views.bursor_property_detail, name='bursor_property_detail'),
    path('bursor-send-sms-form/', BursorSendSMSFormView.as_view(), name='bursor_send_sms_form'),
    path('bursor-check-balance/', BursorCheckBalanceView.as_view(), name='bursor_check_balance'),
    path('bursor-sms-history/', BursorSMSHistoryView.as_view(), name='bursor_sms_history'),
    path('bursor-delete-sms/', BursorDeleteSMSView.as_view(), name='bursor_delete_sms'),
    path("bursor/staff/list/", BursorStaffListView.as_view(), name="bursor-staff-list"),
    # Other URL patterns
    path('bursor/uniforms/', bursor_uniform_list, name='bursor_uniform_list'),
    path('bursor/uniforms/create/', bursor_uniform_create, name='bursor_uniform_create'),
    path('bursor/uniforms/<int:pk>/update/', bursor_uniform_update, name='bursor_uniform_update'),
    path('bursor/uniforms/<int:pk>/delete/', bursor_uniform_delete, name='bursor_uniform_delete'),
    path('bursor/uniforms/<int:student_id>/detail/', bursor_uniform_detail, name='bursor_uniform_detail'),
    
    path('bursoruniformtypes/', BursorUniformTypeListView.as_view(), name='bursoruniformtype_list'),
    path('bursoruniformtypes/add/', BursorUniformTypeCreateView.as_view(), name='bursoruniformtype_add'),
    path('bursoruniformtypes/<int:pk>/edit/', BursorUniformTypeUpdateView.as_view(), name='bursoruniformtype_edit'),
    path('bursoruniformtypes/<int:pk>/delete/', BursorUniformTypeDeleteView.as_view(), name='bursoruniformtype_delete'),
    path('bursoruniform/get_price/', bursor_get_uniform_price, name='bursor_get_uniform_price'),
    path('bursoruniform/get_student_class/', bursor_get_student_class, name='bursor_get_student_class'),

    path('bursor_student_uniforms/', bursor_student_uniform_list, name='bursor_student_uniform_list'),
    path('bursor_student_uniforms/create/<int:student_id>/', bursor_student_uniform_create, name='bursor_student_uniform_create'),
    path('bursor_student_uniforms/<int:pk>/update/', bursor_student_uniform_update, name='bursor_student_uniform_update'),
    path('bursor_student_uniforms/<int:pk>/delete/', bursor_student_uniform_delete, name='bursor_student_uniform_delete'),

    path('bursor/comments/', BursorCommentsListView.as_view(), name='bursor_comments'),
    path('bursor_create_parent_user/', bursor_create_parent_user, name='bursor_create_parent_user'),
    path('bursor_update_parent_user/<int:pk>/', bursor_update_parent_user, name='bursor_update_parent_user'),
    path('bursor_list_parent_users/', bursor_parent_user_list, name='bursor_parent_user_list'),
    path('bursor_delete_parent_user/<int:pk>/', bursor_delete_parent_user, name='bursor_delete_parent_user'),
    path('save-bursor-answer/', views.save_bursor_answer, name='save_bursor_answer'),
    path('mark-comment-as-satisfied/<int:comment_id>/', mark_comment_as_satisfied, name='mark_comment_as_satisfied'),
    path('bursor/receipt/<int:pk>/', BursorReceiptDetailView.as_view(), name='bursor-receipt-detail'),
    path('bursor-staff-management-home/', bursor_staff_management_home, name='bursor_staff_management_home'),
    path('bursor-student-management-home/', views.bursor_student_management_home, name='bursor_student_management_home'),
]
