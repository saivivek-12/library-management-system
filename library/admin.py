from django.contrib import admin
from .models import Author, Book, Student, Issue, BookSummary, BookDemand

admin.site.register(Author)
admin.site.register(Book)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_no', 'name', 'department', 'role', 'login_method', 'last_id_card_login', 'is_active')
    list_filter = ('department', 'role', 'login_method', 'is_active')
    search_fields = ('roll_no', 'name', 'email')
    readonly_fields = ('last_id_card_login',)
admin.site.register(Issue)
admin.site.register(BookSummary)
admin.site.register(BookDemand)