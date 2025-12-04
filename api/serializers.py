from rest_framework import serializers
from .models import User, Organization, Patient, Consultation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role', 'organization']

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class ConsultationSerializer(serializers.ModelSerializer):
    # Добавляем вложенную информацию о пациенте (чтобы видеть имя, а не просто ID)
    patient_info = PatientSerializer(source='patient', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = Consultation
        fields = [
            'id',
            'doctor', 'doctor_name',
            'patient', 'patient_info',
            'audio_file',
            'status',
            'generated_report',
            'final_report',
            'created_at'
        ]
        read_only_fields = ['generated_report', 'status'] # Эти поля меняет только AI, а не юзер