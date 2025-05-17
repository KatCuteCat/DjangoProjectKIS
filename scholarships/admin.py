from django.contrib import admin
from .models import Student, AdminProfile, StipendApplication  # Убрали неиспользуемый StipendType

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'faculty', 'group', 'form')
    search_fields = ('full_name', 'faculty', 'group')
    list_filter = ('faculty', 'form')

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position')
    search_fields = ('user__username', 'position')

@admin.register(StipendApplication)
class StipendApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'stipend', 'status', 'created_at')
    list_filter = ('status', 'stipend')
    search_fields = ('student__full_name',)
    actions = ['make_approved', 'make_rejected']

    def make_approved(self, queryset):  # Убрали неиспользуемый параметр request
        queryset.update(status='approved')
    make_approved.short_description = "Одобрить выбранные заявки"

    def make_rejected(self, queryset):  # Убрали неиспользуемый параметр request
        queryset.update(status='rejected')
    make_rejected.short_description = "Отклонить выбранные заявки"