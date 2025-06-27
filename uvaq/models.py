import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

import pycountry
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, Count


# Validators
def validate_alpha_2_code(value):
    try:
        country = pycountry.countries.get(alpha_2=value)
        if country is None:
            msg = f"{value} is not a valid alpha-2 country code."
            raise ValidationError(msg)
    except KeyError:
        msg = f"{value} is not a valid alpha-2 country code."
        raise ValidationError(msg)


# Enums and Choices
class Role(models.TextChoices):
    STUDENT = "student", "Student"
    SERVICES = "services", "Services"
    PROFESSOR = "professor", "Professor"
    TESTER = "tester", "Tester"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


class PreferredContactMethod(models.TextChoices):
    WHATSAPP = "whatsapp", "WhatsApp"
    PHONE = "phone", "Phone"
    CELLPHONE = "cellphone", "Cellphone"
    EMAIL = "email", "Email"
    OTHER = "other", "Other"


class AdmissionType(models.TextChoices):
    REGULAR = "regular", "Regular Admission"
    TRANSFER = "transfer", "Transfer"
    SPECIAL = "special", "Special Admission"
    INTERNATIONAL = "international", "International Student"


class StudyModality(models.TextChoices):
    SCHOOLING = "schooling", "Schooling"
    MIXED = "mixed", "Mixed"
    ONLINE = "online", "Online"
    INTENSIVE = "intensive", "Intensive"


class Shift(models.TextChoices):
    MORNING = "morning", "Morning"
    AFTERNOON = "afternoon", "Afternoon"
    EVENING = "evening", "Evening"
    NIGHT = "night", "Night"


class SubjectStatus(models.TextChoices):
    APPROVED = "approved", "Approved"
    FAILED = "failed", "Failed"
    IN_PROGRESS = "in_progress", "In Progress"
    WITHDRAWN = "withdrawn", "Withdrawn"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    PARTIAL = "partial", "Partial Payment"
    CANCELLED = "cancelled", "Cancelled"
    WAIVED = "waived", "Waived"
    REFUNDED = "refunded", "Refunded"


class GraduationModality(models.TextChoices):
    THESIS = "thesis", "Thesis"
    EXAM = "exam", "Comprehensive Exam"
    WORK_EXPERIENCE = "work_exp", "Work Experience"
    SPECIAL_STUDY = "special_study", "Special Study"


class AcademicStatusType(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    GRADUATED = "graduated", "Graduated"
    SUSPENDED = "suspended", "Suspended"
    DROPPED_OUT = "dropped_out", "Dropped Out"


class EducationLevel(models.TextChoices):
    UNDERGRADUATE = "undergraduate", "Undergraduate"
    GRADUATE = "graduate", "Graduate"
    POSTGRADUATE = "postgraduate", "Postgraduate"


class SubjectTypes(models.TextChoices):
    CORE = "core", "Core"
    ELECTIVE = "elective", "Elective"


class PeriodType(models.TextChoices):
    SEMESTER = "semester", "Semester"
    SUMMER = "summer", "Summer"
    QUARTER = "quarter", "Quarter"
    INTENSIVE = "intensive", "Intensive"


class PersonalInformation(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    second_last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    photo = models.URLField(max_length=254)
    digital_signature = models.URLField(blank=True, max_length=254)
    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.second_last_name or ''}".strip()

    def clean(self):
        if self.birth_date > datetime.date.today():
            msg = "The date of birth cannot be in the future."
            raise ValidationError(msg)

    def has_content(self):
        role_attributes = {
            Role.STUDENT: [
                "contact_info",
                "identification",
                "academic_profile",
                "financial_info",
            ],
            Role.PROFESSOR: ["contact_info", "identification", "professor"],
            Role.SERVICES: ["contact_info", "identification", "staff_profile"],
            Role.TESTER: ["contact_info"],
        }

        role = Role(self.role) if isinstance(self.role, str) else self.role

        required_attributes = role_attributes.get(role, [])
        for attr in required_attributes:
            if getattr(self, attr, None) is None:
                return False
        return True


class ContactInformation(models.Model):
    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="contact_info",
    )
    phone = models.CharField(max_length=20, blank=True)
    cell_phone = models.CharField(max_length=20, blank=True)
    personal_email = models.EmailField()
    institutional_email = models.EmailField(unique=True, blank=True, null=True)
    preferred_contact_method = models.CharField(
        max_length=50,
        choices=PreferredContactMethod.choices,
        blank=True,
    )

    def __str__(self):
        return self.personal_email

    def clean(self):
        if (
            ContactInformation.objects.exclude(pk=self.pk)
            .filter(personal_email=self.personal_email)
            .exists()
        ):
            msg = "Personal Email must be unique."
            raise ValidationError(msg)
        if (
            ContactInformation.objects.exclude(pk=self.pk)
            .filter(institutional_email=self.institutional_email)
            .exists()
        ):
            msg = "Institutional Email must be unique."
            raise ValidationError(msg)


class Identification(models.Model):
    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="identification",
    )
    curp = models.CharField(
        max_length=18,
        db_index=True,
        unique=True,
        blank=True,
        null=True,
    )
    identity_number = models.CharField(max_length=50)
    nationality = models.CharField(max_length=2, validators=[validate_alpha_2_code])

    def __str__(self):
        return self.curp

    def clean(self):
        if Identification.objects.exclude(pk=self.pk).filter(curp=self.curp).exists():
            msg = "CURP must be unique."
            raise ValidationError(msg)
        if (
            Identification.objects.exclude(pk=self.pk)
            .filter(identity_number=self.identity_number)
            .exists()
        ):
            msg = "Identity Number 'CURP' must be unique."
            raise ValidationError(msg)


class AcademicPeriod(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    parent_period = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    cohort = models.CharField(max_length=50)
    registration_start = models.DateField()
    registration_end = models.DateField()
    term_code = models.CharField(max_length=20, unique=True)
    academic_year = models.PositiveSmallIntegerField()
    period_number = models.PositiveSmallIntegerField()
    period_type = models.CharField(max_length=20, choices=PeriodType.choices)
    is_regular_period = models.BooleanField(default=True)
    # These are virtual (derived) or linked via FK
    next_period = models.OneToOneField(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="previous_period"
    )

    def __str__(self):
        return f"{self.name} ({self.cohort})"

    def clean(self):
        if self.start_date >= self.end_date:
            msg = "End date must be after start date."
            raise ValidationError(msg)
        if self.registration_start >= self.registration_end:
            msg = "Registration end must be after registration start."
            raise ValidationError(msg)
        if self.registration_end > self.start_date:
            msg = "Registration should end before period starts."
            raise ValidationError(msg)


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=125)
    description = models.CharField(max_length=255)
    credits = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    prerequisites = models.ManyToManyField("self", symmetrical=False, blank=True)
    core_requirement = models.BooleanField(default=False)
    hours_per_week = models.PositiveSmallIntegerField()
    total_hours = models.PositiveSmallIntegerField()
    department = models.CharField(max_length=100)
    duration_weeks = models.PositiveSmallIntegerField(default=16)
    type = models.CharField(choices=SubjectTypes.choices, max_length=20)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_typical_enrollment(self):
        return (
            Enrollment.objects.filter(subject=self)
            .values("period")
            .annotate(count=Count("id"))
            .aggregate(avg=Avg("count"))["avg"]
        )


class StudyPlan(models.Model):
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_credits = models.PositiveSmallIntegerField()
    required_credits = models.PositiveSmallIntegerField()
    elective_credits = models.PositiveSmallIntegerField()
    subjects = models.ManyToManyField(Subject, through="StudyPlanSubject")
    duration_in_periods = models.PositiveSmallIntegerField(default=8)

    def __str__(self):
        return f"{self.name} v{self.version}"


class StudyPlanSubject(models.Model):
    study_plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.PositiveSmallIntegerField()
    is_required = models.BooleanField(default=True)
    min_grade = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("6.00"))

    class Meta:
        unique_together = ("study_plan", "subject")

    def __str__(self):
        return f"{self.study_plan} - {self.subject} (Sem {self.semester})"


class Professor(models.Model):
    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="professor",
    )
    professor_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    courses_taught = models.ManyToManyField(
        Subject,
        through="ProfessorSubject",
        related_name="professors",
    )
    work_hours = models.CharField(max_length=100)
    hire_date = models.DateField()
    academic_degree = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    max_hours_per_week = models.PositiveSmallIntegerField(default=40)

    def __str__(self):
        return f"Prof. {self.user.first_name} {self.user.last_name}"


class ProfessorSubject(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE)
    group = models.CharField(max_length=10)
    classroom = models.CharField(max_length=20)
    schedule = models.CharField(max_length=100)

    class Meta:
        unique_together = ("professor", "subject", "period", "group")

    def __str__(self):
        return f"{self.professor} - {self.subject} ({self.period})"


class Career(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    duration_semesters = models.PositiveSmallIntegerField()
    total_credits = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    study_plans = models.ManyToManyField(StudyPlan, related_name="careers")
    faculty = models.CharField(max_length=100)
    accreditation = models.CharField(max_length=100, blank=True)
    accreditation_valid_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    personal_info = models.OneToOneField(PersonalInformation, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=50, unique=True)
    career = models.ForeignKey(Career, on_delete=models.PROTECT)
    current_grade = models.CharField(max_length=100)
    admission_type = models.CharField(max_length=20, choices=AdmissionType.choices)
    admission_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.PROTECT,
        related_name="admitted_students",
    )
    study_modality = models.CharField(max_length=20, choices=StudyModality.choices)
    shift = models.CharField(max_length=20, choices=Shift.choices, blank=True)
    campus = models.CharField(max_length=100)
    credits_approved = models.PositiveSmallIntegerField(default=0)
    periods_completed = models.PositiveSmallIntegerField(default=0)
    current_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_students",
    )
    study_plan = models.ForeignKey(StudyPlan, on_delete=models.PROTECT)
    enrollment_date = models.DateField()
    expected_graduation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    admission_period_term_code = models.CharField(
        max_length=20,
        blank=True,
    )
    subjects = models.ManyToManyField(Subject, through="Enrollment", related_name="students")
    academic_history = models.ManyToManyField(
        AcademicPeriod,
        through="AcademicRecord",
        related_name="students_history",
    )
    academic_status = models.CharField(
        max_length=20,
        choices=AcademicStatusType.choices,
        default=AcademicStatusType.ACTIVE,
    )
    education_level = models.CharField(max_length=20, choices=EducationLevel.choices)
    generation = models.CharField(max_length=20, blank=True)
    generation_year = models.PositiveSmallIntegerField(null=True, blank=True)
    cohort_identifier = models.CharField(max_length=50, blank=True)
    status_change_date = models.DateField(null=True, blank=True)
    withdrawal_date = models.DateField(null=True, blank=True)
    withdrawal_reason = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.personal_info.first_name} {self.personal_info.last_name} ({self.student_id})"

    def get_subjects_list(self):
        return [{"code": subject.code, "name": subject.name} for subject in self.subjects.all()]


class AcademicProfile(models.Model):
    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="academic_profile",
    )
    previous_school = models.CharField(max_length=100, blank=True)
    study_interest = models.CharField(max_length=200, blank=True)
    academic_offer = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.study_interest


class AdmissionData(models.Model):
    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="admission_data",
    )
    found_out_through = models.CharField(max_length=100, blank=True)
    educational_advisor = models.CharField(max_length=100, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return self.found_out_through


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE)
    enrollment_date = models.DateField()
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=SubjectStatus.choices,
        default=SubjectStatus.IN_PROGRESS,
    )
    attempt_number = models.PositiveSmallIntegerField(default=1)
    group = models.CharField(max_length=10)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ("student", "subject", "period")

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.period})"


class AcademicRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=AcademicStatusType.choices,
        default=AcademicStatusType.ACTIVE,
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    is_regular = models.BooleanField(default=True)
    scholarship = models.CharField(max_length=100, blank=True)
    average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    withdrawal_date = models.DateField(null=True, blank=True)
    withdrawal_reason = models.CharField(max_length=200, blank=True)
    re_enrollment_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "period")

    def __str__(self):
        return f"{self.student} - {self.period} ({self.status})"


class Payment(models.Model):
    PAYMENT_TYPES: ClassVar[list[tuple[str, str]]] = [
        ("enrollment", "Inscription"),
        ("monthly", "Monthly Payment"),
        ("degree", "Degree entitlement"),
        ("library", "Library"),
        ("lab", "Laboratory"),
        ("other", "Other"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payments")
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    period = models.ForeignKey(AcademicPeriod, on_delete=models.PROTECT)
    receipt_number = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.student} - {self.get_payment_type_display()} ({self.amount})"


class Graduation(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="graduation")
    graduation_date = models.DateField()
    modality = models.CharField(max_length=50, choices=GraduationModality.choices)
    title = models.CharField(max_length=200)
    thesis_title = models.CharField(max_length=200, blank=True)
    advisor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, blank=True)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2)
    honors = models.CharField(max_length=100, blank=True)
    ceremony_date = models.DateField(null=True, blank=True)
    diploma_number = models.CharField(max_length=50, unique=True)
    graduation_period = models.ForeignKey(AcademicPeriod, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.student} - {self.graduation_date}"


class StaffProfile(models.Model):
    STAFF_TYPES: ClassVar[list[tuple[str, str]]] = [
        ("academic", "Academic"),
        ("administrative", "Administrative"),
        ("support", "Support"),
        ("technical", "Technical"),
    ]

    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    department = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    work_hours = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=50, unique=True)
    hire_date = models.DateField()
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)
    is_active = models.BooleanField(default=True)
    supervisor = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    office_location = models.CharField(max_length=100)
    extension = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"Staff {self.user.first_name} {self.user.last_name} ({self.job_title})"


class Responsibility(models.Model):
    staff_profile = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name="responsibilities",
    )
    description = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    area = models.CharField(max_length=100)

    def __str__(self):
        return self.description


class Vehicle(models.Model):
    owner = models.ForeignKey(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="vehicles",
    )
    plate_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    year = models.PositiveSmallIntegerField()
    make = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model} - {self.plate_number}"

    def clean(self):
        if Vehicle.objects.exclude(pk=self.pk).filter(plate_number=self.plate_number).exists():
            msg = "A vehicle with this plate number already exists."
            raise ValidationError(msg)


class InsuranceInformation(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="insurance_info")
    policy_number = models.CharField(max_length=50, unique=True)
    provider = models.CharField(max_length=100)

    def __str__(self):
        return f"Policy {self.policy_number} for {self.vehicle.plate_number}"


class AccessControl(models.Model):
    user = models.ForeignKey(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="access_control",
    )
    access_level = models.CharField(max_length=50, blank=True)
    access_hours = models.CharField(max_length=50, blank=True)
    vehicle = models.ManyToManyField(
        Vehicle,
        blank=True,
        related_name="access_control",
    )
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    areas_allowed = models.TextField()
    biometric_type = models.CharField(
        max_length=100,
    )  # Example: 'Fingerprint', 'Retina Scan'
    data = models.TextField()  # Store encoded data or reference to external storage
    device_type = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user} - Access Level: {self.access_level or 'N/A'}"

    def clean(self):
        if self.valid_from >= self.valid_until:
            msg = "Valid until date must be after valid from date."
            raise ValidationError(msg)


class FinancialInformation(models.Model):
    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="financial_info",
    )
    total_debt = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    overdue_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    last_payment_date = models.DateField(null=True, blank=True)
    last_payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    payment_plan = models.CharField(max_length=100, blank=True)
    scholarship = models.CharField(max_length=100, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"Debt: {self.total_debt}"


class UniversityInfo(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50)
    additional_info = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    website = models.URLField()
    rector = models.CharField(max_length=100)
    foundation_date = models.DateField()

    def __str__(self):
        return self.name


class UserUniversity(models.Model):
    TYPE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("secondary", "Secondary"),
        ("high_school", "High School"),
        ("degree", "Degree"),
        ("engineer", "Engineer"),
        ("specialty", "Specialty"),
        ("master", "Master"),
        ("doctorate", "Doctorate"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="user_university",
    )
    user_identifier = models.CharField(max_length=50)
    university_identifier = models.CharField(
        max_length=50,
        default="2b0020f3-9d2f-4a14-b5b2-dcbad34754b5",
    )
    university = models.ForeignKey(UniversityInfo, on_delete=models.CASCADE)
    user_roles = models.CharField(max_length=20, choices=Role.choices)
    mandatory_notification = models.CharField(max_length=20, choices=Role.choices)
    optional_notifications = models.ManyToManyField(
        "Notification",
        related_name="optional_for_users",
        blank=True,
    )
    enrollment_date = models.DateField()
    campus = models.CharField(max_length=100, blank=True)
    career = models.ForeignKey(Career, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)
    last_access = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.university_identifier

    def save(self, *args, **kwargs):
        if (self.mandatory_notification and self.user_roles) and (
            self.mandatory_notification != self.user_roles
        ):
            msg = f"Mandatory notification must match the user role '{self.user_roles}'."
            raise ValidationError(msg)

        super().save(*args, **kwargs)


class Notification(models.Model):
    NOTIFICATION_TYPES: ClassVar[list[tuple[str, str]]] = [
        ("academic", "Academic"),
        ("financial", "Financial"),
        ("administrative", "Administrative"),
        ("event", "Event"),
        ("security", "Security"),
    ]

    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    target_roles = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return self.name


class EmergencyInformation(models.Model):
    user = models.OneToOneField(
        PersonalInformation,
        on_delete=models.CASCADE,
        related_name="emergency_info",
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50)
    secondary_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=True)

    def __str__(self):
        return f"Emergency Contact for {self.user.first_name} {self.user.last_name}"
