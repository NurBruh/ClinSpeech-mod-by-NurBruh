import os
import json
import threading
import whisper  # Библиотека локального ИИ
from .models import Consultation


def run_ai_processing(consultation_id):
    try:
        # 1. Получаем запись
        consultation = Consultation.objects.get(id=consultation_id)
        print(f"🏥 [FREE AI] Начинаю обработку ID: {consultation_id}")

        consultation.status = 'processing'
        consultation.save()

        file_path = consultation.audio_file.path

        # --- ЭТАП 1: Локальная транскрибация (Whisper) ---
        print("📥 Загружаю модель Whisper (это может занять время в первый раз)...")
        # 'base' - это легкая модель, работает быстро на CPU.
        # Есть еще 'tiny' (быстрее, но глупее) и 'small' (умнее, но медленнее)
        model = whisper.load_model("base")

        print("🎙️ Слушаю аудио и перевожу в текст...")
        result = model.transcribe(file_path)
        text = result["text"]

        # Сохраняем сырой текст
        consultation.raw_transcription = text
        consultation.save()
        print(f"✅ Текст получен: {text}")

        # --- ЭТАП 2: Генерация отчета (Пока имитация) ---
        print("🧠 Анализирую текст...")

        # Простая логика для теста (пока без LLM)
        # Мы ищем ключевые слова в тексте и подставляем диагноз
        text_lower = text.lower()

        diagnosis = "Не удалось определить (требуется осмотр)"
        rec = "Консультация специалиста"

        if "голов" in text_lower or "мигрень" in text_lower:
            diagnosis = "Головная боль напряжения / Мигрень"
            rec = "МРТ головного мозга, режим сна, Нурофен."
        elif "кашел" in text_lower or "горл" in text_lower or "температур" in text_lower:
            diagnosis = "ОРВИ / Острый бронхит"
            rec = "Обильное питье, Лазолван, парацетамол при t > 38.5."
        elif "живот" in text_lower or "болит" in text_lower:
            diagnosis = "Гастрит? Синдром раздраженного кишечника"
            rec = "Диета стол №1, Но-шпа, ФГДС."

        # Формируем JSON вручную
        ai_report = {
            "complaints": text,  # В жалобы пишем то, что распознали
            "anamnesis": "Со слов пациента, заболевание началось остро.",
            "diagnosis": diagnosis,
            "recommendations": rec
        }

        json_report = json.dumps(ai_report, ensure_ascii=False)

        # Сохраняем
        consultation.generated_report = json_report
        consultation.final_report = json_report
        consultation.status = 'ready'
        consultation.save()

        print(f"🎉 [DONE] Успешно завершено! ID: {consultation_id}")

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        consultation = Consultation.objects.get(id=consultation_id)
        consultation.status = 'error'
        consultation.save()


def start_ai_task(consultation_id):
    # Запускаем в фоне, чтобы сайт не вис
    thread = threading.Thread(target=run_ai_processing, args=(consultation_id,))
    thread.start()