from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Student, StipendType

class StipendAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            password='testpass123'
        )
        self.student_user = User.objects.create_user(
            username='student',
            password='studentpass'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            full_name="Иванов Иван",
            faculty="ИТ",
            group="ИТ-101",
            form="full_time",
            birth_date="2000-01-01"
        )
        self.stipend = StipendType.objects.create(
            name="Академическая",
            category="academic",
            description="Для отличников",
            max_recipients=10
        )

    def test_create_application(self):
        self.client.force_login(self.student_user)
        url = reverse('stipendapplication-list')
        data = {
            "student": self.student.id,
            "stipend": self.stipend.id,
            "files": []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)