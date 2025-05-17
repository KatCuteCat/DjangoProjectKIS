from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse
from openpyxl import Workbook
import os

from .models import Student, StipendType, StipendApplication, ApplicationHistory
from .serializers import (
    StudentSerializer,
    StipendTypeSerializer,
    StipendApplicationSerializer,
    ApplicationHistorySerializer
)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StipendTypeViewSet(viewsets.ModelViewSet):
    queryset = StipendType.objects.all()
    serializer_class = StipendTypeSerializer


class StipendApplicationViewSet(viewsets.ModelViewSet):
    queryset = StipendApplication.objects.all()
    serializer_class = StipendApplicationSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, *args, **kwargs):
        application = self.get_object()
        application.status = 'approved'
        application.reviewed_at = timezone.now()
        if hasattr(request.user, 'admin'):
            application.reviewer = request.user.admin
        application.save()

        ApplicationHistory.objects.create(
            application=application,
            action='approved',
            changed_by=request.user
        )
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, *args, **kwargs):
        application = self.get_object()
        application.status = 'rejected'
        application.reviewed_at = timezone.now()
        if hasattr(request.user, 'admin'):
            application.reviewer = request.user.admin
        application.save()

        ApplicationHistory.objects.create(
            application=application,
            action='rejected',
            changed_by=request.user
        )
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def upload_file(self, request, *args, **kwargs):
        application = self.get_object()
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({'error': 'Файл не предоставлен'}, status=400)

        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'stipend_docs'))
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        if 'files' not in application.files:
            application.files = {'files': []}

        application.files['files'].append({
            'name': uploaded_file.name,
            'url': file_url,
            'uploaded_at': str(timezone.now())
        })
        application.save()

        return Response({'file_url': file_url})

    @action(detail=False, methods=['get'])
    def export_to_excel(self, request):
        applications = self.get_queryset()

        wb = Workbook()
        ws = wb.active
        ws.title = "Заявки на стипендию"

        # Заголовки
        headers = [
            'ID', 'ФИО студента', 'Факультет', 'Группа',
            'Тип стипендии', 'Категория', 'Статус',
            'Дата подачи', 'Дата рассмотрения', 'Комментарий'
        ]
        ws.append(headers)

        # Данные
        for app in applications:
            ws.append([
                app.id,
                app.student.full_name,
                app.student.faculty,
                app.student.group,
                app.stipend.name,
                app.stipend.get_category_display(),
                app.get_status_display(),
                app.created_at.strftime('%Y-%m-%d %H:%M'),
                app.reviewed_at.strftime('%Y-%m-%d %H:%M') if app.reviewed_at else '',
                app.comment or ''
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="stipend_applications.xlsx"'},
        )
        wb.save(response)

        return response


class ApplicationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApplicationHistorySerializer

    def get_queryset(self):
        application_id = self.request.query_params.get('application_id')
        if application_id:
            return ApplicationHistory.objects.filter(application_id=application_id)
        return ApplicationHistory.objects.all()