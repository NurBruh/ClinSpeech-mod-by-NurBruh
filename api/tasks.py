import json
import os
import shutil
import whisper  # Библиотека ИИ
from .models import Consultation


def process_audio(consultation_id):
    """
    Эта функция запускается в фоне через Django Q.
    """
    try:
        # 1. Находим консультацию в базе
        print(f"⚡ [Worker] Взял в работу задачу ID: {consultation_id}")
        consultation = Consultation.objects.get(id=consultation_id)

        # Ставим статус "В обработке"
        consultation.status = 'processing'
        consultation.save()

        # 2. Проверяем FFmpeg (без него Whisper не работает)
        if not shutil.which("ffmpeg"):
            # Если не нашли в системе, пробуем искать в корне проекта
            if os.path.exists('ffmpeg.exe'):
                os.environ["PATH"] += os.pathsep + os.getcwd()
            else:
                print("❌ ОШИБКА: FFmpeg не найден! Положите ffmpeg.exe рядом с manage.py")
                consultation.status = 'error'
                consultation.save()
                return

        # 3. Запускаем Whisper (Транскрибация)
        audio_path = consultation.audio_file.path
        print(f"🎙️ Загружаю модель Whisper и слушаю файл: {audio_path}...")

        # 'medium' — отличное качество распознавания для медицинских терминов
        # Альтернативы: 'small' (быстрее), 'large' (ещё точнее, но очень медленная)
        model = whisper.load_model("medium")
        result = model.transcribe(audio_path)  # Указываем русский язык для лучшего качества
        text = result["text"]

        print(f"✅ Распознано: {text[:50]}...")

        # Сохраняем сырой текст
        consultation.raw_transcription = text
        consultation.save()

        # 4. Анализ текста (Имитация ума врача)
        # Здесь мы формируем JSON для отчета
        print("🧠 Формирую медицинский отчет...")

        # Простая логика поиска ключевых слов
        diagnosis = "Диагноз не уточнен"
        recs = "Осмотр терапевта"
        text_lower = text.lower()

        if "голов" in text_lower or "мигрень" in text_lower:
            diagnosis = "Головная боль напряжения (G44.2)"
            recs = "Соблюдение режима сна, МРТ головного мозга."
        elif "кашел" in text_lower or "температур" in text_lower:
            diagnosis = "ОРВИ (J06.9)"
            recs = "Обильное питье, постельный режим, парацетамол."

        report_data = {
            "complaints": text,  # Жалобы = всё, что сказал пациент
            "anamnesis": "Записано со слов пациента автоматически.",
            "diagnosis": diagnosis,
            "recommendations": recs
        }

        # Превращаем словарь в текст JSON
        json_string = json.dumps(report_data, ensure_ascii=False)

        # 5. Финал: сохраняем всё в базу
        consultation.generated_report = json_string
        consultation.final_report = json_string  # Копируем в финал
        consultation.status = 'ready'
        consultation.save()

        print(f"🎉 Задача {consultation_id} полностью готова!")

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        # Если что-то сломалось, пишем статус Error
        try:
            c = Consultation.objects.get(id=consultation_id)
            c.status = 'error'
            c.save()
        except:
            pass