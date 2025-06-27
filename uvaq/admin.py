from typing import ClassVar

from django.contrib import admin

from .models import (
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
    InsuranceInformation,
    Notification,
    Payment,
    PersonalInformation,
    Professor,
    ProfessorSubject,
    Responsibility,
    StaffProfile,
    Student,
    StudyPlan,
    StudyPlanSubject,
    Subject,
    UniversityInfo,
    UserUniversity,
    Vehicle,
)


# Inline Admin Classes
class ContactInformationInline(admin.StackedInline):
    model = ContactInformation
    can_delete = False
    verbose_name_plural = "Contact Information"


class IdentificationInline(admin.StackedInline):
    model = Identification
    can_delete = False
    verbose_name_plural = "Identification"


class AcademicProfileInline(admin.StackedInline):
    model = AcademicProfile
    can_delete = False
    verbose_name_plural = "Academic Profile"


class AdmissionDataInline(admin.StackedInline):
    model = AdmissionData
    can_delete = False
    verbose_name_plural = "Admission Data"


class FinancialInformationInline(admin.StackedInline):
    model = FinancialInformation
    can_delete = False
    verbose_name_plural = "Financial Information"


class EmergencyInformationInline(admin.StackedInline):
    model = EmergencyInformation
    can_delete = False
    verbose_name_plural = "Emergency Information"


class UserUniversityInline(admin.StackedInline):
    model = UserUniversity
    can_delete = False
    verbose_name_plural = "University Information"


class AccessControlInline(admin.StackedInline):
    model = AccessControl
    can_delete = False
    verbose_name_plural = "Access Control"


class ProfessorSubjectInline(admin.TabularInline):
    model = ProfessorSubject
    extra = 1


class StudyPlanSubjectInline(admin.TabularInline):
    model = StudyPlanSubject
    extra = 1


class ResponsibilityInline(admin.TabularInline):
    model = Responsibility
    extra = 1


class InsuranceInformationInline(admin.StackedInline):
    model = InsuranceInformation
    extra = 0
    max_num = 1


#  Main Admin Classes
@admin.register(PersonalInformation)
class PersonalInformationAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "second_last_name", "birth_date", "gender", "role")
    list_filter = ("gender", "role")
    search_fields = ("first_name", "last_name", "second_last_name")
    inlines: ClassVar[list] = [
        ContactInformationInline,
        IdentificationInline,
        AcademicProfileInline,
        AdmissionDataInline,
        FinancialInformationInline,
        EmergencyInformationInline,
    ]


@admin.register(ContactInformation)
class ContactInformationAdmin(admin.ModelAdmin):
    list_display = ("user", "personal_email", "institutional_email", "preferred_contact_method")
    search_fields = ("personal_email", "institutional_email", "user__first_name")


@admin.register(Identification)
class IdentificationAdmin(admin.ModelAdmin):
    list_display = ("user", "curp", "identity_number", "nationality")
    search_fields = ("curp", "identity_number")
    list_filter = ("nationality",)


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "cohort", "start_date", "end_date", "is_active")
    list_filter = ("is_active", "cohort")
    search_fields = ("name", "term_code")
    date_hierarchy = "start_date"


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "credits", "is_active")
    list_filter = ("is_active", "core_requirement")
    search_fields = ("code", "name")
    filter_horizontal = ("prerequisites",)


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "start_date", "is_active")
    list_filter = ("is_active", "version")
    search_fields = ("name",)
    inlines: ClassVar[list] = [StudyPlanSubjectInline]


@admin.register(StudyPlanSubject)
class StudyPlanSubjectAdmin(admin.ModelAdmin):
    list_display = ("study_plan", "subject", "semester", "is_required")
    list_filter = ("study_plan", "semester", "is_required")
    search_fields = ("study_plan__name", "subject__name")


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ("user", "professor_id", "department", "hire_date", "is_active")
    search_fields = ("user__first_name", "professor_id")
    list_filter = ("department", "is_active")
    inlines: ClassVar[list] = [ProfessorSubjectInline]


@admin.register(ProfessorSubject)
class ProfessorSubjectAdmin(admin.ModelAdmin):
    list_display = ("professor", "subject", "period", "group")
    list_filter = ("period", "subject")
    search_fields = ("professor__user__first_name", "subject__name")


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "duration_semesters", "is_active")
    search_fields = ("name", "code")
    list_filter = ("faculty", "is_active")
    filter_horizontal = ("study_plans",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("personal_info", "student_id", "career", "current_period", "academic_status")
    search_fields = ("student_id", "personal_info__first_name")
    list_filter = ("career", "admission_type", "academic_status", "study_modality")
    raw_id_fields = ("personal_info", "study_plan", "current_period")


@admin.register(AcademicProfile)
class AcademicProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "study_interest")
    search_fields = ("user__first_name", "study_interest")


@admin.register(AdmissionData)
class AdmissionDataAdmin(admin.ModelAdmin):
    list_display = ("user", "found_out_through")
    search_fields = ("user__first_name", "found_out_through")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "period", "status", "final_grade")
    list_filter = ("status", "period")
    search_fields = ("student__student_id", "subject__name")
    raw_id_fields = ("professor",)


@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "period", "status", "average")
    list_filter = ("status", "period", "is_regular")
    search_fields = ("student__student_id", "reason")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "payment_type", "amount", "payment_date", "status")
    list_filter = ("payment_type", "status", "period")
    search_fields = ("student__student_id", "receipt_number")
    date_hierarchy = "payment_date"


@admin.register(Graduation)
class GraduationAdmin(admin.ModelAdmin):
    list_display = ("student", "graduation_date", "modality", "final_grade")
    search_fields = ("student__student_id", "thesis_title")
    raw_id_fields = ("advisor",)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "staff_id", "department", "job_title", "staff_type")
    search_fields = ("user__first_name", "staff_id")
    list_filter = ("staff_type", "department")
    inlines: ClassVar[list] = [ResponsibilityInline]


@admin.register(Responsibility)
class ResponsibilityAdmin(admin.ModelAdmin):
    list_display = ("staff_profile", "description", "start_date", "is_current")
    list_filter = ("is_current", "area")
    search_fields = ("description", "staff_profile__user__first_name")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("owner", "plate_number", "make", "model", "year")
    search_fields = ("plate_number", "owner__first_name")
    inlines: ClassVar[list] = [InsuranceInformationInline]


@admin.register(InsuranceInformation)
class InsuranceInformationAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "policy_number", "provider")
    search_fields = ("policy_number", "vehicle__plate_number")


@admin.register(AccessControl)
class AccessControlAdmin(admin.ModelAdmin):
    list_display = ("user", "access_level", "valid_from", "valid_until", "is_active")
    list_filter = ("is_active", "access_level")
    search_fields = ("user__first_name", "device_id")
    filter_horizontal = ("vehicle",)


@admin.register(FinancialInformation)
class FinancialInformationAdmin(admin.ModelAdmin):
    list_display = ("user", "total_debt", "overdue_balance")
    search_fields = ("user__first_name",)


@admin.register(UniversityInfo)
class UniversityInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "identifier", "foundation_date")
    search_fields = ("name", "identifier")


@admin.register(UserUniversity)
class UserUniversityAdmin(admin.ModelAdmin):
    list_display = ("user", "university", "user_roles", "is_active")
    list_filter = ("user_roles", "is_active", "type")
    search_fields = ("user__first_name", "university_identifier")
    filter_horizontal = ("optional_notifications",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("name", "notification_type", "target_roles", "is_active")
    list_filter = ("notification_type", "target_roles", "is_active")
    search_fields = ("name", "description")


@admin.register(EmergencyInformation)
class EmergencyInformationAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "relationship", "phone")
    search_fields = ("user__first_name", "name")
