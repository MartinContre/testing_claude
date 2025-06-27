from datetime import date
from typing import ClassVar

import pycountry
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from uvaq.models import (
    AcademicPeriod,
    AcademicProfile,
    AcademicRecord,
    AccessControl,
    AdmissionData,
    Career,
    ContactInformation,
    EmergencyInformation,
    Enrollment,
    FinancialInformation,
    Graduation,
    Identification,
    Payment,
    PersonalInformation,
    Professor,
    ProfessorSubject,
    Responsibility,
    StaffProfile,
    Student,
    StudyPlan,
    Subject,
    UniversityInfo,
    UserUniversity,
    Vehicle,
)


# Base Serializers for Common Models
class PersonalInformationSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = PersonalInformation
        fields: ClassVar[list[str]] = [
            "id",
            "first_name",
            "last_name",
            "second_last_name",
            "full_name",
            "birth_date",
            "age",
            "gender",
            "photo",
            "digital_signature",
            "role",
        ]

    def get_age(self, obj):
        today = date.today()
        return (
            today.year
            - obj.birth_date.year
            - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
        )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name} {obj.second_last_name or ''}".strip()


class ContactInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInformation
        fields: ClassVar[list[str]] = [
            "id",
            "phone",
            "cell_phone",
            "personal_email",
            "institutional_email",
            "preferred_contact_method",
        ]


class IdentificationSerializer(serializers.ModelSerializer):
    nationality_name = serializers.SerializerMethodField()

    class Meta:
        model = Identification
        fields: ClassVar[list[str]] = [
            "id",
            "curp",
            "identity_number",
            "nationality",
            "nationality_name",
        ]

    def get_nationality_name(self, obj):
        try:
            country = pycountry.countries.get(alpha_2=obj.nationality)
            return country.name if country else obj.nationality
        except:
            return obj.nationality


class EmergencyInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyInformation
        fields: ClassVar[list[str]] = [
            "id",
            "name",
            "phone",
            "relationship",
            "secondary_phone",
            "address",
            "is_primary",
        ]


class VehicleSerializer(serializers.ModelSerializer):
    insurance_info = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields: ClassVar[list[str]] = [
            "id",
            "plate_number",
            "model",
            "vehicle_type",
            "color",
            "year",
            "make",
            "is_active",
            "insurance_info",
        ]

    def get_insurance_info(self, obj):
        try:
            insurance = obj.insurance_info.first()
            if insurance:
                return {"policy_number": insurance.policy_number, "provider": insurance.provider}
        except:
            pass
        return None


class AccessControlSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True, read_only=True)

    class Meta:
        model = AccessControl
        fields: ClassVar[list[str]] = [
            "id",
            "access_level",
            "access_hours",
            "valid_from",
            "valid_until",
            "is_active",
            "areas_allowed",
            "biometric_type",
            "device_type",
            "device_id",
            "vehicles",
        ]


class UniversityInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityInfo
        fields: ClassVar[list[str]] = [
            "id",
            "name",
            "identifier",
            "address",
            "phone",
            "website",
            "rector",
            "foundation_date",
        ]


class UserUniversitySerializer(serializers.ModelSerializer):
    university = UniversityInfoSerializer(read_only=True)

    class Meta:
        model = UserUniversity
        fields: ClassVar[list[str]] = [
            "id",
            "user_identifier",
            "university_identifier",
            "university",
            "user_roles",
            "enrollment_date",
            "campus",
            "type",
            "is_active",
            "last_access",
        ]


# Student Related Serializers
class PaymentSerializer(serializers.ModelSerializer):
    payment_type_display = serializers.CharField(source="get_payment_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields: ClassVar[list[str]] = [
            "id",
            "payment_type",
            "payment_type_display",
            "amount",
            "payment_date",
            "status",
            "status_display",
            "receipt_number",
            "payment_method",
            "description",
            "due_date",
            "days_overdue",
        ]

    def get_days_overdue(self, obj):
        if obj.status == "pending":
            overdue_days = (date.today() - obj.due_date).days
            return max(0, overdue_days)
        return 0


class FinancialInformationSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source="user.student.payments")
    payment_summary = serializers.SerializerMethodField()

    class Meta:
        model = FinancialInformation
        fields: ClassVar[list[str]] = [
            "id",
            "total_debt",
            "overdue_balance",
            "last_payment_date",
            "last_payment_amount",
            "payment_plan",
            "scholarship",
            "discount",
            "payments",
            "payment_summary",
        ]

    def get_payment_summary(self, obj):
        try:
            student = obj.user.student
            payments = student.payments.all()
            return {
                "total_payments": payments.count(),
                "pending_payments": payments.filter(status="pending").count(),
                "completed_payments": payments.filter(status="completed").count(),
                "total_paid": sum(p.amount for p in payments.filter(status="completed")),
                "total_pending": sum(p.amount for p in payments.filter(status="pending")),
            }
        except:
            return {}


class AcademicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProfile
        fields: ClassVar[list[str]] = [
            "id",
            "previous_school",
            "study_interest",
            "academic_offer",
        ]


class AdmissionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionData
        fields: ClassVar[list[str]] = [
            "id",
            "found_out_through",
            "educational_advisor",
            "comments",
        ]


class SubjectSerializer(serializers.ModelSerializer):
    prerequisites = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Subject
        fields: ClassVar[list[str]] = [
            "id",
            "code",
            "name",
            "description",
            "credits",
            "is_active",
            "prerequisites",
            "core_requirement",
            "hours_per_week",
            "total_hours",
        ]


class StudyPlanSerializer(serializers.ModelSerializer):
    subjects_count = serializers.SerializerMethodField()

    class Meta:
        model = StudyPlan
        fields: ClassVar[list[str]] = [
            "id",
            "name",
            "version",
            "start_date",
            "end_date",
            "is_active",
            "total_credits",
            "required_credits",
            "elective_credits",
            "subjects_count",
        ]

    def get_subjects_count(self, obj):
        return obj.subjects.count()


class CareerSerializer(serializers.ModelSerializer):
    study_plans = StudyPlanSerializer(many=True, read_only=True)

    class Meta:
        model = Career
        fields: ClassVar[list[str]] = [
            "id",
            "name",
            "code",
            "description",
            "duration_semesters",
            "total_credits",
            "is_active",
            "faculty",
            "accreditation",
            "accreditation_valid_until",
            "study_plans",
        ]


class AcademicPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPeriod
        fields: ClassVar[list[str]] = [
            "id",
            "name",
            "start_date",
            "end_date",
            "is_active",
            "cohort",
            "registration_start",
            "registration_end",
            "term_code",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    period = AcademicPeriodSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Enrollment
        fields: ClassVar[list[str]] = [
            "id",
            "subject",
            "period",
            "enrollment_date",
            "final_grade",
            "status",
            "status_display",
            "attempt_number",
            "group",
        ]


class AcademicRecordSerializer(serializers.ModelSerializer):
    period = AcademicPeriodSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AcademicRecord
        fields: ClassVar[list[str]] = [
            "id",
            "period",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "reason",
            "comments",
            "is_regular",
            "scholarship",
            "average",
            "withdrawal_date",
            "withdrawal_reason",
            "re_enrollment_date",
        ]


class GraduationSerializer(serializers.ModelSerializer):
    modality_display = serializers.CharField(source="get_modality_display", read_only=True)
    advisor_name = serializers.CharField(source="advisor.user.first_name", read_only=True)
    graduation_period = AcademicPeriodSerializer(read_only=True)

    class Meta:
        model = Graduation
        fields: ClassVar[list[str]] = [
            "id",
            "graduation_date",
            "modality",
            "modality_display",
            "title",
            "thesis_title",
            "advisor_name",
            "final_grade",
            "honors",
            "ceremony_date",
            "diploma_number",
            "graduation_period",
        ]


# Staff Related Serializers
class ResponsibilitySerializer(serializers.ModelSerializer):
    duration_days = serializers.SerializerMethodField()

    class Meta:
        model = Responsibility
        fields: ClassVar[list[str]] = [
            "id",
            "description",
            "start_date",
            "end_date",
            "is_current",
            "area",
            "duration_days",
        ]

    def get_duration_days(self, obj):
        end_date = obj.end_date or timezone.now().date()
        return (end_date - obj.start_date).days


# Professor Related Serializers
class ProfessorSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    period = AcademicPeriodSerializer(read_only=True)

    class Meta:
        model = ProfessorSubject
        fields: ClassVar[list[str]] = ["id", "subject", "period", "group", "classroom", "schedule"]


# Main Complete Serializers
class CompleteStudentSerializer(serializers.ModelSerializer):
    personal_info = PersonalInformationSerializer(read_only=True)
    contact_info = ContactInformationSerializer(source="personal_info.contact_info", read_only=True)
    identification = IdentificationSerializer(source="personal_info.identification", read_only=True)
    financial_info = FinancialInformationSerializer(
        source="personal_info.financial_info",
        read_only=True,
    )
    academic_profile = AcademicProfileSerializer(
        source="personal_info.academic_profile",
        read_only=True,
    )
    admission_data = AdmissionDataSerializer(source="personal_info.admission_data", read_only=True)
    emergency_info = EmergencyInformationSerializer(
        source="personal_info.emergency_info",
        read_only=True,
    )
    user_university = UserUniversitySerializer(
        source="personal_info.user_university",
        read_only=True,
    )
    vehicles = VehicleSerializer(source="personal_info.vehicles", many=True, read_only=True)
    access_control = AccessControlSerializer(
        source="personal_info.access_control",
        many=True,
        read_only=True,
    )

    # Academic Information
    career = CareerSerializer(read_only=True)
    study_plan = StudyPlanSerializer(read_only=True)
    admission_period = AcademicPeriodSerializer(read_only=True)
    current_period = AcademicPeriodSerializer(read_only=True)

    # Academic Records
    enrollments = EnrollmentSerializer(source="enrollment_set", many=True, read_only=True)
    academic_records = AcademicRecordSerializer(
        source="academicrecord_set",
        many=True,
        read_only=True,
    )
    graduation = GraduationSerializer(read_only=True)

    # Computed Fields
    admission_type_display = serializers.CharField(
        source="get_admission_type_display",
        read_only=True,
    )
    study_modality_display = serializers.CharField(
        source="get_study_modality_display",
        read_only=True,
    )
    shift_display = serializers.CharField(source="get_shift_display", read_only=True)
    academic_status_display = serializers.CharField(
        source="get_academic_status_display",
        read_only=True,
    )
    education_level_display = serializers.CharField(
        source="get_education_level_display",
        read_only=True,
    )

    academic_progress = serializers.SerializerMethodField()
    current_semester = serializers.SerializerMethodField()
    gpa = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields: ClassVar[list[str]] = [
            "id",
            "student_id",
            "personal_info",
            "contact_info",
            "identification",
            "financial_info",
            "academic_profile",
            "admission_data",
            "emergency_info",
            "user_university",
            "vehicles",
            "access_control",
            # Academic Info
            "career",
            "study_plan",
            "current_grade",
            "admission_type",
            "admission_type_display",
            "admission_period",
            "study_modality",
            "study_modality_display",
            "shift",
            "shift_display",
            "campus",
            "credits_approved",
            "periods_completed",
            "current_period",
            "enrollment_date",
            "expected_graduation_date",
            "is_active",
            "academic_status",
            "academic_status_display",
            "education_level",
            "education_level_display",
            # Records
            "enrollments",
            "academic_records",
            "graduation",
            # Computed
            "academic_progress",
            "current_semester",
            "gpa",
        ]

    def get_academic_progress(self, obj):
        try:
            total_credits_needed = obj.study_plan.total_credits
            progress_percentage = (obj.credits_approved / total_credits_needed) * 100
            return {
                "credits_approved": obj.credits_approved,
                "total_credits_needed": total_credits_needed,
                "progress_percentage": round(progress_percentage, 2),
                "remaining_credits": total_credits_needed - obj.credits_approved,
            }
        except:
            return {}

    def get_current_semester(self, obj):
        return obj.periods_completed + 1 if obj.is_active else obj.periods_completed

    def get_gpa(self, obj):
        enrollments = obj.enrollment_set.filter(final_grade__isnull=False)
        if enrollments.exists():
            total_grades = sum(enrollment.final_grade for enrollment in enrollments)
            return round(total_grades / enrollments.count(), 2)
        return None


class CompleteStaffSerializer(serializers.ModelSerializer):
    user = PersonalInformationSerializer(read_only=True)
    contact_info = ContactInformationSerializer(source="user.contact_info", read_only=True)
    identification = IdentificationSerializer(source="user.identification", read_only=True)
    emergency_info = EmergencyInformationSerializer(source="user.emergency_info", read_only=True)
    user_university = UserUniversitySerializer(source="user.user_university", read_only=True)
    vehicles = VehicleSerializer(source="user.vehicles", many=True, read_only=True)
    access_control = AccessControlSerializer(
        source="user.access_control",
        many=True,
        read_only=True,
    )

    responsibilities = ResponsibilitySerializer(many=True, read_only=True)
    supervisor_info = serializers.SerializerMethodField()
    staff_type_display = serializers.CharField(source="get_staff_type_display", read_only=True)

    # Computed Fields
    years_of_service = serializers.SerializerMethodField()
    current_responsibilities = serializers.SerializerMethodField()

    class Meta:
        model = StaffProfile
        fields: ClassVar[list[str]] = [
            "id",
            "staff_id",
            "user",
            "contact_info",
            "identification",
            "emergency_info",
            "user_university",
            "vehicles",
            "access_control",
            # Staff Info
            "department",
            "job_title",
            "work_hours",
            "hire_date",
            "staff_type",
            "staff_type_display",
            "is_active",
            "supervisor_info",
            "office_location",
            "extension",
            # Responsibilities
            "responsibilities",
            "current_responsibilities",
            # Computed
            "years_of_service",
        ]

    def get_supervisor_info(self, obj):
        if obj.supervisor:
            return {
                "id": obj.supervisor.id,
                "name": f"{obj.supervisor.user.first_name} {obj.supervisor.user.last_name}",
                "job_title": obj.supervisor.job_title,
                "department": obj.supervisor.department,
            }
        return None

    def get_years_of_service(self, obj):
        today = date.today()
        return today.year - obj.hire_date.year

    def get_current_responsibilities(self, obj):
        current = obj.responsibilities.filter(is_current=True)
        return ResponsibilitySerializer(current, many=True).data


class CompleteProfessorSerializer(serializers.ModelSerializer):
    user = PersonalInformationSerializer(read_only=True)
    contact_info = ContactInformationSerializer(source="user.contact_info", read_only=True)
    identification = IdentificationSerializer(source="user.identification", read_only=True)
    emergency_info = EmergencyInformationSerializer(source="user.emergency_info", read_only=True)
    user_university = UserUniversitySerializer(source="user.user_university", read_only=True)
    vehicles = VehicleSerializer(source="user.vehicles", many=True, read_only=True)
    access_control = AccessControlSerializer(
        source="user.access_control",
        many=True,
        read_only=True,
    )

    # Professor specific
    courses_taught = SubjectSerializer(many=True, read_only=True)
    current_assignments = ProfessorSubjectSerializer(
        source="professorsubject_set",
        many=True,
        read_only=True,
    )
    advised_graduations = GraduationSerializer(source="graduation_set", many=True, read_only=True)

    # Computed Fields
    years_of_service = serializers.SerializerMethodField()
    teaching_load = serializers.SerializerMethodField()
    current_courses = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields: ClassVar[list[str]] = [
            "id",
            "professor_id",
            "user",
            "contact_info",
            "identification",
            "emergency_info",
            "user_university",
            "vehicles",
            "access_control",
            # Professor Info
            "department",
            "work_hours",
            "hire_date",
            "academic_degree",
            "specialization",
            "is_active",
            "max_hours_per_week",
            # Teaching
            "courses_taught",
            "current_assignments",
            "advised_graduations",
            # Computed
            "years_of_service",
            "teaching_load",
            "current_courses",
        ]

    def get_years_of_service(self, obj):
        today = date.today()
        return today.year - obj.hire_date.year

    def get_teaching_load(self, obj):
        current_assignments = obj.professorsubject_set.filter(period__is_active=True)
        total_hours = sum(assignment.subject.hours_per_week for assignment in current_assignments)
        return {
            "current_courses": current_assignments.count(),
            "total_weekly_hours": total_hours,
            "max_hours_per_week": obj.max_hours_per_week,
            "utilization_percentage": round((total_hours / obj.max_hours_per_week) * 100, 2)
            if obj.max_hours_per_week > 0
            else 0,
        }

    def get_current_courses(self, obj):
        current_assignments = obj.professorsubject_set.filter(
            period__is_active=True,
        ).select_related("subject", "period")

        return [
            {
                "subject_code": assignment.subject.code,
                "subject_name": assignment.subject.name,
                "group": assignment.group,
                "classroom": assignment.classroom,
                "schedule": assignment.schedule,
                "period": assignment.period.name,
                "credits": assignment.subject.credits,
            }
            for assignment in current_assignments
        ]


class PersonalInformationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating personal information"""

    class Meta:
        model = PersonalInformation
        fields = [
            "first_name",
            "last_name",
            "second_last_name",
            "birth_date",
            "gender",
            "photo",
            "digital_signature",
            "role",
        ]

    def validate_birth_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Birth date cannot be in the future")
        return value

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required")
        return value.strip().title()

    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required")
        return value.strip().title()


class ContactInformationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating contact information"""

    class Meta:
        model = ContactInformation
        fields = [
            "phone",
            "cell_phone",
            "personal_email",
            "institutional_email",
            "preferred_contact_method",
        ]

    def validate_personal_email(self, value):
        if value and "@" not in value:
            raise serializers.ValidationError("Invalid email format")
        return value

    def validate_institutional_email(self, value):
        if value and "@" not in value:
            raise serializers.ValidationError("Invalid email format")
        return value


class IdentificationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating identification information"""

    class Meta:
        model = Identification
        fields = ["curp", "identity_number", "nationality"]

    def validate_nationality(self, value):
        try:
            country = pycountry.countries.get(alpha_2=value)
            if not country:
                raise serializers.ValidationError("Invalid nationality code")
        except:
            raise serializers.ValidationError("Invalid nationality code")
        return value


class EmergencyInformationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating emergency contact information"""

    class Meta:
        model = EmergencyInformation
        fields = ["name", "phone", "relationship", "secondary_phone", "address", "is_primary"]

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Emergency contact name is required")
        return value.strip().title()


class VehicleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating vehicle information"""

    class Meta:
        model = Vehicle
        fields = ["plate_number", "model", "vehicle_type", "color", "year", "make", "is_active"]

    def validate_year(self, value):
        current_year = date.today().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError(f"Year must be between 1900 and {current_year + 1}")
        return value


class AccessControlCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating access control information"""

    class Meta:
        model = AccessControl
        fields = [
            "access_level",
            "access_hours",
            "valid_from",
            "valid_until",
            "is_active",
            "areas_allowed",
            "biometric_type",
            "device_type",
            "device_id",
        ]

    def validate(self, data):
        if data.get("valid_from") and data.get("valid_until"):
            if data["valid_from"] >= data["valid_until"]:
                raise serializers.ValidationError("Valid from date must be before valid until date")
        return data


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    """Complete serializer for creating and updating Student records"""

    # Nested serializers for related objects
    personal_info = PersonalInformationCreateUpdateSerializer()
    contact_info = ContactInformationCreateUpdateSerializer()
    identification = IdentificationCreateUpdateSerializer()
    emergency_info = EmergencyInformationCreateUpdateSerializer()
    vehicles = VehicleCreateUpdateSerializer(many=True, required=False)
    access_control = AccessControlCreateUpdateSerializer(many=True, required=False)

    # Foreign key fields using IDs/codes
    career_code = serializers.CharField(write_only=True)
    study_plan_id = serializers.IntegerField(write_only=True, required=False)
    admission_period_id = serializers.IntegerField(write_only=True)
    current_period_id = serializers.IntegerField(write_only=True, required=False)
    university_identifier = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = [
            "student_id",
            "personal_info",
            "contact_info",
            "identification",
            "emergency_info",
            "vehicles",
            "access_control",
            # Academic fields
            "career_code",
            "study_plan_id",
            "current_grade",
            "admission_type",
            "admission_period_id",
            "study_modality",
            "shift",
            "campus",
            "credits_approved",
            "periods_completed",
            "current_period_id",
            "enrollment_date",
            "expected_graduation_date",
            "is_active",
            "academic_status",
            "education_level",
            "university_identifier",
        ]

    def validate_credits_approved(self, value):
        if value < 0:
            raise serializers.ValidationError("Credits approved cannot be negative")
        return value

    def validate_periods_completed(self, value):
        if value < 0:
            raise serializers.ValidationError("Periods completed cannot be negative")
        return value

    def validate_career_code(self, value):
        try:
            Career.objects.get(code=value, is_active=True)
        except Career.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive career code")
        return value

    def validate_admission_period_id(self, value):
        try:
            AcademicPeriod.objects.get(id=value)
        except AcademicPeriod.DoesNotExist:
            raise serializers.ValidationError("Invalid admission period")
        return value

    def validate_university_identifier(self, value):
        try:
            UniversityInfo.objects.get(identifier=value)
        except UniversityInfo.DoesNotExist:
            raise serializers.ValidationError("Invalid university identifier")
        return value

    @transaction.atomic
    def create(self, validated_data):
        # Extract nested data
        personal_info_data = validated_data.pop("personal_info")
        contact_info_data = validated_data.pop("contact_info")
        identification_data = validated_data.pop("identification")
        emergency_info_data = validated_data.pop("emergency_info")
        vehicles_data = validated_data.pop("vehicles", [])
        access_control_data = validated_data.pop("access_control", [])

        # Extract foreign key data
        career_code = validated_data.pop("career_code")
        university_identifier = validated_data.pop("university_identifier")
        admission_period_id = validated_data.pop("admission_period_id")
        current_period_id = validated_data.pop("current_period_id", None)
        study_plan_id = validated_data.pop("study_plan_id", None)

        # Create PersonalInformation first
        personal_info = PersonalInformation.objects.create(**personal_info_data)

        # Create related objects
        ContactInformation.objects.create(user=personal_info, **contact_info_data)
        Identification.objects.create(user=personal_info, **identification_data)
        EmergencyInformation.objects.create(user=personal_info, **emergency_info_data)

        # Create vehicles
        for vehicle_data in vehicles_data:
            Vehicle.objects.create(owner=personal_info, **vehicle_data)

        # Create access control
        for access_data in access_control_data:
            AccessControl.objects.create(user=personal_info, **access_data)

        # Get foreign key objects
        career = Career.objects.get(code=career_code)
        admission_period = AcademicPeriod.objects.get(id=admission_period_id)
        current_period = (
            AcademicPeriod.objects.get(id=current_period_id) if current_period_id else None
        )
        study_plan = StudyPlan.objects.get(id=study_plan_id) if study_plan_id else None
        university = UniversityInfo.objects.get(identifier=university_identifier)

        # Create Student
        student = Student.objects.create(
            personal_info=personal_info,
            career=career,
            admission_period=admission_period,
            current_period=current_period,
            study_plan=study_plan,
            **validated_data,
        )

        # Create UserUniversity relationship
        UserUniversity.objects.create(
            user=personal_info,
            university=university,
            user_identifier=student.student_id,
            user_roles=["student"],
            enrollment_date=student.enrollment_date,
            campus=student.campus,
            type="student",
            is_active=student.is_active,
        )

        return student

    @transaction.atomic
    def update(self, instance, validated_data):
        # Extract nested data
        personal_info_data = validated_data.pop("personal_info", None)
        contact_info_data = validated_data.pop("contact_info", None)
        identification_data = validated_data.pop("identification", None)
        emergency_info_data = validated_data.pop("emergency_info", None)
        vehicles_data = validated_data.pop("vehicles", None)
        access_control_data = validated_data.pop("access_control", None)

        # Extract foreign key data
        career_code = validated_data.pop("career_code", None)
        admission_period_id = validated_data.pop("admission_period_id", None)
        current_period_id = validated_data.pop("current_period_id", None)
        study_plan_id = validated_data.pop("study_plan_id", None)

        # Update nested objects
        if personal_info_data:
            personal_serializer = PersonalInformationCreateUpdateSerializer(
                instance.personal_info, data=personal_info_data, partial=True
            )
            if personal_serializer.is_valid(raise_exception=True):
                personal_serializer.save()

        if contact_info_data:
            contact_serializer = ContactInformationCreateUpdateSerializer(
                instance.personal_info.contact_info, data=contact_info_data, partial=True
            )
            if contact_serializer.is_valid(raise_exception=True):
                contact_serializer.save()

        if identification_data:
            identification_serializer = IdentificationCreateUpdateSerializer(
                instance.personal_info.identification, data=identification_data, partial=True
            )
            if identification_serializer.is_valid(raise_exception=True):
                identification_serializer.save()

        if emergency_info_data:
            emergency_serializer = EmergencyInformationCreateUpdateSerializer(
                instance.personal_info.emergency_info, data=emergency_info_data, partial=True
            )
            if emergency_serializer.is_valid(raise_exception=True):
                emergency_serializer.save()

        # Update foreign key relationships
        if career_code:
            instance.career = Career.objects.get(code=career_code)
        if admission_period_id:
            instance.admission_period = AcademicPeriod.objects.get(id=admission_period_id)
        if current_period_id:
            instance.current_period = AcademicPeriod.objects.get(id=current_period_id)
        if study_plan_id:
            instance.study_plan = StudyPlan.objects.get(id=study_plan_id)

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class StaffCreateUpdateSerializer(serializers.ModelSerializer):
    """Complete serializer for creating and updating Staff records"""

    # Nested serializers for related objects
    user = PersonalInformationCreateUpdateSerializer()
    contact_info = ContactInformationCreateUpdateSerializer()
    identification = IdentificationCreateUpdateSerializer()
    emergency_info = EmergencyInformationCreateUpdateSerializer()
    vehicles = VehicleCreateUpdateSerializer(many=True, required=False)
    access_control = AccessControlCreateUpdateSerializer(many=True, required=False)

    # Foreign key fields
    supervisor_id = serializers.IntegerField(write_only=True, required=False)
    university_identifier = serializers.CharField(write_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            "staff_id",
            "user",
            "contact_info",
            "identification",
            "emergency_info",
            "vehicles",
            "access_control",
            # Staff specific fields
            "department",
            "job_title",
            "work_hours",
            "hire_date",
            "staff_type",
            "is_active",
            "supervisor_id",
            "office_location",
            "extension",
            "university_identifier",
        ]

    def validate_hire_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Hire date cannot be in the future")
        return value

    def validate_work_hours(self, value):
        if value <= 0 or value > 168:  # 168 hours in a week
            raise serializers.ValidationError("Work hours must be between 1 and 168")
        return value

    def validate_supervisor_id(self, value):
        try:
            StaffProfile.objects.get(id=value, is_active=True)
        except StaffProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive supervisor")
        return value

    def validate_university_identifier(self, value):
        try:
            UniversityInfo.objects.get(identifier=value)
        except UniversityInfo.DoesNotExist:
            raise serializers.ValidationError("Invalid university identifier")
        return value

    @transaction.atomic
    def create(self, validated_data):
        # Extract nested data
        user_data = validated_data.pop("user")
        contact_info_data = validated_data.pop("contact_info")
        identification_data = validated_data.pop("identification")
        emergency_info_data = validated_data.pop("emergency_info")
        vehicles_data = validated_data.pop("vehicles", [])
        access_control_data = validated_data.pop("access_control", [])

        # Extract foreign key data
        supervisor_id = validated_data.pop("supervisor_id", None)
        university_identifier = validated_data.pop("university_identifier")

        # Set role for staff
        user_data["role"] = "staff"

        # Create PersonalInformation first
        user = PersonalInformation.objects.create(**user_data)

        # Create related objects
        ContactInformation.objects.create(user=user, **contact_info_data)
        Identification.objects.create(user=user, **identification_data)
        EmergencyInformation.objects.create(user=user, **emergency_info_data)

        # Create vehicles
        for vehicle_data in vehicles_data:
            Vehicle.objects.create(owner=user, **vehicle_data)

        # Create access control
        for access_data in access_control_data:
            AccessControl.objects.create(user=user, **access_data)

        # Get foreign key objects
        supervisor = StaffProfile.objects.get(id=supervisor_id) if supervisor_id else None
        university = UniversityInfo.objects.get(identifier=university_identifier)

        # Create StaffProfile
        staff = StaffProfile.objects.create(user=user, supervisor=supervisor, **validated_data)

        # Create UserUniversity relationship
        UserUniversity.objects.create(
            user=user,
            university=university,
            user_identifier=staff.staff_id,
            user_roles=["staff"],
            enrollment_date=staff.hire_date,
            type="staff",
            is_active=staff.is_active,
        )

        return staff

    @transaction.atomic
    def update(self, instance, validated_data):
        # Extract nested data
        user_data = validated_data.pop("user", None)
        contact_info_data = validated_data.pop("contact_info", None)
        identification_data = validated_data.pop("identification", None)
        emergency_info_data = validated_data.pop("emergency_info", None)
        vehicles_data = validated_data.pop("vehicles", None)
        access_control_data = validated_data.pop("access_control", None)

        # Extract foreign key data
        supervisor_id = validated_data.pop("supervisor_id", None)

        # Update nested objects
        if user_data:
            user_serializer = PersonalInformationCreateUpdateSerializer(
                instance.user, data=user_data, partial=True
            )
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        if contact_info_data:
            contact_serializer = ContactInformationCreateUpdateSerializer(
                instance.user.contact_info, data=contact_info_data, partial=True
            )
            if contact_serializer.is_valid(raise_exception=True):
                contact_serializer.save()

        if identification_data:
            identification_serializer = IdentificationCreateUpdateSerializer(
                instance.user.identification, data=identification_data, partial=True
            )
            if identification_serializer.is_valid(raise_exception=True):
                identification_serializer.save()

        if emergency_info_data:
            emergency_serializer = EmergencyInformationCreateUpdateSerializer(
                instance.user.emergency_info, data=emergency_info_data, partial=True
            )
            if emergency_serializer.is_valid(raise_exception=True):
                emergency_serializer.save()

        # Update foreign key relationships
        if supervisor_id:
            instance.supervisor = StaffProfile.objects.get(id=supervisor_id)

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProfessorCreateUpdateSerializer(serializers.ModelSerializer):
    """Complete serializer for creating and updating Professor records"""

    # Nested serializers for related objects
    user = PersonalInformationCreateUpdateSerializer()
    contact_info = ContactInformationCreateUpdateSerializer()
    identification = IdentificationCreateUpdateSerializer()
    emergency_info = EmergencyInformationCreateUpdateSerializer()
    vehicles = VehicleCreateUpdateSerializer(many=True, required=False)
    access_control = AccessControlCreateUpdateSerializer(many=True, required=False)

    # Foreign key fields
    university_identifier = serializers.CharField(write_only=True)
    courses_taught_codes = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Professor
        fields = [
            "professor_id",
            "user",
            "contact_info",
            "identification",
            "emergency_info",
            "vehicles",
            "access_control",
            # Professor specific fields
            "department",
            "work_hours",
            "hire_date",
            "academic_degree",
            "specialization",
            "is_active",
            "max_hours_per_week",
            "university_identifier",
            "courses_taught_codes",
        ]

    def validate_hire_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Hire date cannot be in the future")
        return value

    def validate_work_hours(self, value):
        if value <= 0 or value > 168:  # 168 hours in a week
            raise serializers.ValidationError("Work hours must be between 1 and 168")
        return value

    def validate_max_hours_per_week(self, value):
        if value <= 0 or value > 168:
            raise serializers.ValidationError("Max hours per week must be between 1 and 168")
        return value

    def validate_university_identifier(self, value):
        try:
            UniversityInfo.objects.get(identifier=value)
        except UniversityInfo.DoesNotExist:
            raise serializers.ValidationError("Invalid university identifier")
        return value

    def validate_courses_taught_codes(self, value):
        for code in value:
            try:
                Subject.objects.get(code=code, is_active=True)
            except Subject.DoesNotExist:
                raise serializers.ValidationError(f"Invalid or inactive subject code: {code}")
        return value

    @transaction.atomic
    def create(self, validated_data):
        # Extract nested data
        user_data = validated_data.pop("user")
        contact_info_data = validated_data.pop("contact_info")
        identification_data = validated_data.pop("identification")
        emergency_info_data = validated_data.pop("emergency_info")
        vehicles_data = validated_data.pop("vehicles", [])
        access_control_data = validated_data.pop("access_control", [])

        # Extract foreign key data
        university_identifier = validated_data.pop("university_identifier")
        courses_taught_codes = validated_data.pop("courses_taught_codes", [])

        # Set role for professor
        user_data["role"] = "professor"

        # Create PersonalInformation first
        user = PersonalInformation.objects.create(**user_data)

        # Create related objects
        ContactInformation.objects.create(user=user, **contact_info_data)
        Identification.objects.create(user=user, **identification_data)
        EmergencyInformation.objects.create(user=user, **emergency_info_data)

        # Create vehicles
        for vehicle_data in vehicles_data:
            Vehicle.objects.create(owner=user, **vehicle_data)

        # Create access control
        for access_data in access_control_data:
            AccessControl.objects.create(user=user, **access_data)

        # Get foreign key objects
        university = UniversityInfo.objects.get(identifier=university_identifier)

        # Create Professor
        professor = Professor.objects.create(user=user, **validated_data)

        # Add courses taught
        for code in courses_taught_codes:
            subject = Subject.objects.get(code=code)
            professor.courses_taught.add(subject)

        # Create UserUniversity relationship
        UserUniversity.objects.create(
            user=user,
            university=university,
            user_identifier=professor.professor_id,
            user_roles=["professor"],
            enrollment_date=professor.hire_date,
            type="professor",
            is_active=professor.is_active,
        )

        return professor

    @transaction.atomic
    def update(self, instance, validated_data):
        # Extract nested data
        user_data = validated_data.pop("user", None)
        contact_info_data = validated_data.pop("contact_info", None)
        identification_data = validated_data.pop("identification", None)
        emergency_info_data = validated_data.pop("emergency_info", None)
        vehicles_data = validated_data.pop("vehicles", None)
        access_control_data = validated_data.pop("access_control", None)

        # Extract foreign key data
        courses_taught_codes = validated_data.pop("courses_taught_codes", None)

        # Update nested objects
        if user_data:
            user_serializer = PersonalInformationCreateUpdateSerializer(
                instance.user, data=user_data, partial=True
            )
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        if contact_info_data:
            contact_serializer = ContactInformationCreateUpdateSerializer(
                instance.user.contact_info, data=contact_info_data, partial=True
            )
            if contact_serializer.is_valid(raise_exception=True):
                contact_serializer.save()

        if identification_data:
            identification_serializer = IdentificationCreateUpdateSerializer(
                instance.user.identification, data=identification_data, partial=True
            )
            if identification_serializer.is_valid(raise_exception=True):
                identification_serializer.save()

        if emergency_info_data:
            emergency_serializer = EmergencyInformationCreateUpdateSerializer(
                instance.user.emergency_info, data=emergency_info_data, partial=True
            )
            if emergency_serializer.is_valid(raise_exception=True):
                emergency_serializer.save()

        # Update courses taught
        if courses_taught_codes is not None:
            instance.courses_taught.clear()
            for code in courses_taught_codes:
                subject = Subject.objects.get(code=code)
                instance.courses_taught.add(subject)

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# Additional serializers that might be needed


class ResponsibilityCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating staff responsibilities"""

    class Meta:
        model = Responsibility
        fields = ["description", "start_date", "end_date", "is_current", "area"]

    def validate(self, data):
        if data.get("start_date") and data.get("end_date"):
            if data["start_date"] >= data["end_date"]:
                raise serializers.ValidationError("Start date must be before end date")
        return data


class EnrollmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating student enrollments"""

    subject_code = serializers.CharField(write_only=True)
    period_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "subject_code",
            "period_id",
            "enrollment_date",
            "final_grade",
            "status",
            "attempt_number",
            "group",
        ]

    def validate_subject_code(self, value):
        try:
            Subject.objects.get(code=value, is_active=True)
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive subject code")
        return value

    def validate_period_id(self, value):
        try:
            AcademicPeriod.objects.get(id=value)
        except AcademicPeriod.DoesNotExist:
            raise serializers.ValidationError("Invalid academic period")
        return value

    def validate_final_grade(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Final grade must be between 0 and 100")
        return value


class PaymentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating payments"""

    class Meta:
        model = Payment
        fields = [
            "payment_type",
            "amount",
            "payment_date",
            "status",
            "receipt_number",
            "payment_method",
            "description",
            "due_date",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def validate(self, data):
        if data.get("payment_date") and data.get("due_date"):
            if data["payment_date"] < data["due_date"] and data.get("status") == "completed":
                # Payment is made before due date, which is fine
                pass
        return data
