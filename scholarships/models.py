from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    FORM_CHOICES = [
        ('full_time', 'Очная'),
        ('part_time', 'Заочная'),
        ('evening', 'Вечерняя'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    faculty = models.CharField(max_length=100, verbose_name="Факультет")
    group = models.CharField(max_length=50, verbose_name="Группа")
    form = models.CharField(max_length=50, choices=FORM_CHOICES, verbose_name="Форма обучения")
    birth_date = models.DateField(verbose_name="Дата рождения")
    documents = models.JSONField(default=list, verbose_name="Документы")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    email = models.EmailField(unique=True, verbose_name="Email")
    position = models.CharField(max_length=100, verbose_name="Должность", blank=True)

    class Meta:
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"

    def __str__(self):
        return f"{self.user.username} ({self.position or 'Администратор'})"


class StipendType(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Учебная'),
        ('research', 'Научно-исследовательская'),
        ('public', 'Общественная'),
        ('sport', 'Спортивная'),
        ('creative', 'Культурно-творческая'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Категория")
    description = models.TextField(verbose_name="Описание")
    max_recipients = models.PositiveIntegerField(verbose_name="Макс. получателей")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Тип стипендии"
        verbose_name_plural = "Типы стипендий"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class StipendApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="applications")
    stipend = models.ForeignKey(StipendType, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    files = models.JSONField(default=list, verbose_name="Прикреплённые файлы")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подачи")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата рассмотрения")
    reviewer = models.ForeignKey(
        AdminProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Кто рассмотрел"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Заявка на стипендию"
        verbose_name_plural = "Заявки на стипендию"
        ordering = ['-created_at']
        permissions = [
            ('can_review_application', 'Может рассматривать заявки'),
        ]

    def __str__(self):
        return f"Заявка {self.student} на {self.stipend} ({self.get_status_display()})"


class ApplicationHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Создано'),
        ('updated', 'Обновлено'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('file_uploaded', 'Файл загружен'),
    ]

    application = models.ForeignKey(StipendApplication, on_delete=models.CASCADE, related_name="history")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Действие")
    details = models.JSONField(default=dict, verbose_name="Детали")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время изменения")
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Кто изменил"
    )

    class Meta:
        verbose_name = "История заявки"
        verbose_name_plural = "История заявок"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} – {self.application} ({self.timestamp})"