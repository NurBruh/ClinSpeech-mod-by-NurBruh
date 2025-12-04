from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Organization, User, Patient, Consultation


# 1. Настройка для Организаций (Клиник)
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')  # Что показывать в списке
    search_fields = ('name',)  # Поиск по названию


# 2. Настройка для Пользователей (Врачей/Админов)
# Мы наследуемся от встроенного UserAdmin, чтобы работала смена пароля
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Поля, которые видны в общем списке
    list_display = ('username', 'first_name', 'last_name', 'role', 'organization', 'is_staff')

    # Фильтры справа (по роли и клинике)
    list_filter = ('role', 'organization', 'is_staff', 'is_superuser')

    # Добавляем наши кастомные поля в форму редактирования пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'organization', 'middle_name')}),
    )

    # Поля при создании нового пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'organization', 'middle_name')}),
    )


# 3. Настройка для Пациентов
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'birth_date', 'organization')
    list_filter = ('organization',)  # Фильтр по клинике
    search_fields = ('last_name', 'first_name', 'phone')  # Поиск по ФИО


# 4. Настройка для Консультаций (Приемов)
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'status', 'created_at')
    list_filter = ('status', 'doctor', 'created_at')

    # Делаем поля ИИ только для чтения, чтобы админ случайно не сломал JSON
    readonly_fields = ('created_at', 'raw_transcription', 'generated_report')

    search_fields = ('patient__last_name', 'doctor__last_name')