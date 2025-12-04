from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class Organization(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название клиники")
    address = models.TextField(blank=True, verbose_name="Адрес")

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Кастомная модель пользователя"""
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('doctor', 'Врач'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='doctor')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")

    # Исправление конфликтов с системными правами
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Patient(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    birth_date = models.DateField(verbose_name="Дата рождения")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Consultation(models.Model):
    STATUS_CHOICES = (
        ('created', 'Создано'),
        ('processing', 'Обработка (Транскрибация)'),
        ('generating', 'Генерация отчета'),
        ('ready', 'Готово'),
        ('error', 'Ошибка'),

    )
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    audio_file = models.FileField(upload_to='consultations/audio/')

    # Результат Whisper
    raw_transcription = models.TextField(blank=True, verbose_name="Текст из аудио")

    # Результат AI (JSON)
    generated_report = models.TextField(blank=True, verbose_name="AI структура (JSON)")

    # Финальный текст после правок врача
    final_report = models.TextField(blank=True, verbose_name="Финальный отчет")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)

    audio_file = models.FileField(
        upload_to='consultations/audio/',
        # Разрешаем форматы: mp3, wav (обычные файлы), ogg, webm (запись с браузера), m4a (айфон)
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'webm', 'm4a'])]
    )

    def __str__(self):
        return f"Прием {self.patient} - {self.created_at.strftime('%Y-%m-%d')}"