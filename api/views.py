import json
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import Patient, Consultation
from .serializers import PatientSerializer, ConsultationSerializer
try:
    from django_q.tasks import async_task
except ImportError:
    # Для django-q2 используем другой импорт
    try:
        from django_q.pusher import async_task
    except ImportError:
        # Если не работает, используем заглушку (синхронный запуск)
        def async_task(func_path, *args, **kwargs):
            print(f"⚠️ Django-Q не настроен, запускаем синхронно: {func_path}")
            import importlib
            module_path, func_name = func_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            func(*args, **kwargs)

class PatientViewSet(viewsets.ModelViewSet):
    """
    API для управления пациентами.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class ConsultationViewSet(viewsets.ModelViewSet):
    """
    Главный API. Обрабатывает загрузку аудио и скачивание отчетов.
    """
    queryset = Consultation.objects.all().order_by('-created_at')
    serializer_class = ConsultationSerializer

    def perform_create(self, serializer):
        """
        Метод срабатывает при POST запросе (загрузка файла).
        """
        # 1. Сохраняем запись в базу данных MySQL
        instance = serializer.save()
        
        print(f"🚀 [API] Консультация {instance.id} создана. Передаю задачу в Django Q...")

        # 2. АСИНХРОННЫЙ ЗАПУСК:
        # Мы не ждем выполнения! Мы просто кидаем задачу в очередь.
        # 'api.tasks.process_audio' — это путь к функции, которую мы писали в tasks.py
        async_task('api.tasks.process_audio', instance.id)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """
        Генерация и скачивание PDF файла.
        """
        consultation = self.get_object()

        # 1. Подготовка данных (парсим JSON от ИИ)
        try:
            # Если в базе лежит текст JSON, превращаем его в словарь
            if consultation.final_report:
                report_data = json.loads(consultation.final_report)
            else:
                raise ValueError("Отчет пуст")
        except (json.JSONDecodeError, ValueError, TypeError):
            # Заглушка, если ИИ еще думает или произошла ошибка
            report_data = {
                "complaints": consultation.raw_transcription or "Транскрибация в процессе...",
                "anamnesis": "Данные обрабатываются...",
                "diagnosis": "Диагноз не сформирован",
                "recommendations": "Ожидайте завершения анализа."
            }

        # 2. Собираем контекст для шаблона HTML
        context = {
            'doctor': consultation.doctor.get_full_name() if consultation.doctor else "Дежурный врач",
            'patient': f"{consultation.patient.last_name} {consultation.patient.first_name}",
            'date': consultation.created_at.strftime("%d.%m.%Y"),
            'report': report_data,
            'report_id': consultation.id
        }

        # 3. Генерируем PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f"Medical_Report_{consultation.patient.last_name}_{pk}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        try:
            # Рендерим HTML из шаблона
            html_string = render_to_string('report.html', context)
            
            # Конвертируем HTML -> PDF
            pisa_status = pisa.CreatePDF(html_string, dest=response)

            if pisa_status.err:
                return Response({"error": "Ошибка конвертации в PDF"}, status=500)
                
            return response

        except Exception as e:
            return Response({"error": f"Ошибка шаблона: {str(e)}"}, status=500)