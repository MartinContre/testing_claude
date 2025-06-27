from typing import ClassVar

import django_filters
from django.db import transaction
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from evoti.serializers import (
    CompleteProfessorSerializer,
    CompleteStaffSerializer,
    CompleteStudentSerializer,
    ProfessorCreateUpdateSerializer,
    StaffCreateUpdateSerializer,
    StudentCreateUpdateSerializer,
)
from uvaq.models import Professor, StaffProfile, Student


# Custom Pagination Classes
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "pagination": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "page_size": self.page_size,
                    "total_pages": self.page.paginator.num_pages,
                    "current_page": self.page.number,
                },
                "results": data,
            },
        )


# Custom Filter Classes
class StudentFilter(django_filters.FilterSet):
    # Basic filters
    student_id = django_filters.CharFilter(lookup_expr="icontains")
    first_name = django_filters.CharFilter(
        field_name="personal_info__first_name",
        lookup_expr="icontains",
    )
    last_name = django_filters.CharFilter(
        field_name="personal_info__last_name",
        lookup_expr="icontains",
    )
    email = django_filters.CharFilter(
        field_name="personal_info__contact_info__institutional_email",
        lookup_expr="icontains",
    )

    # Academic filters
    career = django_filters.CharFilter(field_name="career__code", lookup_expr="iexact")
    career_name = django_filters.CharFilter(field_name="career__name", lookup_expr="icontains")
    academic_status = django_filters.ChoiceFilter(
        choices=Student._meta.get_field("academic_status").choices,
    )
    admission_type = django_filters.ChoiceFilter(
        choices=Student._meta.get_field("admission_type").choices,
    )
    study_modality = django_filters.ChoiceFilter(
        choices=Student._meta.get_field("study_modality").choices,
    )
    shift = django_filters.ChoiceFilter(choices=Student._meta.get_field("shift").choices)
    education_level = django_filters.ChoiceFilter(
        choices=Student._meta.get_field("education_level").choices,
    )
    campus = django_filters.CharFilter(lookup_expr="icontains")

    # Date filters
    enrollment_date_from = django_filters.DateFilter(
        field_name="enrollment_date",
        lookup_expr="gte",
    )
    enrollment_date_to = django_filters.DateFilter(field_name="enrollment_date", lookup_expr="lte")
    expected_graduation_from = django_filters.DateFilter(
        field_name="expected_graduation_date",
        lookup_expr="gte",
    )
    expected_graduation_to = django_filters.DateFilter(
        field_name="expected_graduation_date",
        lookup_expr="lte",
    )

    # Numeric filters
    credits_approved_min = django_filters.NumberFilter(
        field_name="credits_approved",
        lookup_expr="gte",
    )
    credits_approved_max = django_filters.NumberFilter(
        field_name="credits_approved",
        lookup_expr="lte",
    )
    periods_completed_min = django_filters.NumberFilter(
        field_name="periods_completed",
        lookup_expr="gte",
    )
    periods_completed_max = django_filters.NumberFilter(
        field_name="periods_completed",
        lookup_expr="lte",
    )

    # Boolean filters
    is_active = django_filters.BooleanFilter()
    has_graduation = django_filters.BooleanFilter(
        field_name="graduation__isnull",
        lookup_expr=False,
    )
    has_financial_debt = django_filters.BooleanFilter(method="filter_has_debt")

    # Period filters
    admission_period = django_filters.CharFilter(field_name="admission_period__term_code")
    current_period = django_filters.CharFilter(field_name="current_period__term_code")

    class Meta:
        model = Student
        fields: ClassVar[list] = []

    def filter_has_debt(self, queryset, name, value):
        if value:
            return queryset.filter(personal_info__financial_info__total_debt__gt=0)
        return queryset.filter(personal_info__financial_info__total_debt=0)


class StaffFilter(django_filters.FilterSet):
    # Basic filters
    staff_id = django_filters.CharFilter(lookup_expr="icontains")
    first_name = django_filters.CharFilter(field_name="user__first_name", lookup_expr="icontains")
    last_name = django_filters.CharFilter(field_name="user__last_name", lookup_expr="icontains")
    email = django_filters.CharFilter(
        field_name="user__contact_info__institutional_email",
        lookup_expr="icontains",
    )

    # Employment filters
    department = django_filters.CharFilter(lookup_expr="icontains")
    job_title = django_filters.CharFilter(lookup_expr="icontains")
    staff_type = django_filters.ChoiceFilter(choices=StaffProfile.STAFF_TYPES)
    office_location = django_filters.CharFilter(lookup_expr="icontains")

    # Date filters
    hire_date_from = django_filters.DateFilter(field_name="hire_date", lookup_expr="gte")
    hire_date_to = django_filters.DateFilter(field_name="hire_date", lookup_expr="lte")

    # Boolean filters
    is_active = django_filters.BooleanFilter()
    has_supervisor = django_filters.BooleanFilter(
        field_name="supervisor__isnull",
        lookup_expr=False,
    )

    class Meta:
        model = StaffProfile
        fields: ClassVar[list] = []


class ProfessorFilter(django_filters.FilterSet):
    # Basic filters
    professor_id = django_filters.CharFilter(lookup_expr="icontains")
    first_name = django_filters.CharFilter(field_name="user__first_name", lookup_expr="icontains")
    last_name = django_filters.CharFilter(field_name="user__last_name", lookup_expr="icontains")
    email = django_filters.CharFilter(
        field_name="user__contact_info__institutional_email",
        lookup_expr="icontains",
    )

    # Academic filters
    department = django_filters.CharFilter(lookup_expr="icontains")
    academic_degree = django_filters.CharFilter(lookup_expr="icontains")
    specialization = django_filters.CharFilter(lookup_expr="icontains")

    # Teaching filters
    subject_code = django_filters.CharFilter(
        field_name="courses_taught__code",
        lookup_expr="iexact",
    )
    subject_name = django_filters.CharFilter(
        field_name="courses_taught__name",
        lookup_expr="icontains",
    )

    # Date filters
    hire_date_from = django_filters.DateFilter(field_name="hire_date", lookup_expr="gte")
    hire_date_to = django_filters.DateFilter(field_name="hire_date", lookup_expr="lte")

    # Numeric filters
    max_hours_min = django_filters.NumberFilter(field_name="max_hours_per_week", lookup_expr="gte")
    max_hours_max = django_filters.NumberFilter(field_name="max_hours_per_week", lookup_expr="lte")

    # Boolean filters
    is_active = django_filters.BooleanFilter()
    currently_teaching = django_filters.BooleanFilter(method="filter_currently_teaching")
    has_graduated_students = django_filters.BooleanFilter(
        field_name="graduation_set__isnull",
        lookup_expr=False,
    )

    class Meta:
        model = Professor
        fields: ClassVar[list] = []

    def filter_currently_teaching(self, queryset, name, value):
        if value:
            return queryset.filter(professorsubject__period__is_active=True).distinct()
        return queryset.exclude(professorsubject__period__is_active=True).distinct()


# Base queryset methods for optimization
def get_student_queryset():
    return Student.objects.select_related(
        "personal_info",
        "personal_info__contact_info",
        "personal_info__identification",
        "personal_info__financial_info",
        "personal_info__academic_profile",
        "personal_info__admission_data",
        "personal_info__emergency_info",
        "personal_info__user_university",
        "personal_info__user_university__university",
        "career",
        "study_plan",
        "admission_period",
        "current_period",
        "graduation",
    ).prefetch_related(
        "personal_info__vehicles",
        "personal_info__vehicles__insurance_info",
        "personal_info__access_control",
        "personal_info__access_control__vehicle",
        "enrollment_set__subject",
        "enrollment_set__period",
        "enrollment_set__professor",
        "academicrecord_set__period",
        "payments",
        "career__study_plans",
        "career__study_plans__subjects",
    )


def get_staff_queryset():
    return StaffProfile.objects.select_related(
        "user",
        "user__contact_info",
        "user__identification",
        "user__emergency_info",
        "user__user_university",
        "user__user_university__university",
        "supervisor",
        "supervisor__user",
    ).prefetch_related(
        "user__vehicles",
        "user__vehicles__insurance_info",
        "user__access_control",
        "user__access_control__vehicle",
        "responsibilities",
    )


def get_professor_queryset():
    return Professor.objects.select_related(
        "user",
        "user__contact_info",
        "user__identification",
        "user__emergency_info",
        "user__user_university",
        "user__user_university__university",
    ).prefetch_related(
        "user__vehicles",
        "user__vehicles__insurance_info",
        "user__access_control",
        "user__access_control__vehicle",
        "courses_taught",
        "professorsubject_set__subject",
        "professorsubject_set__period",
        "graduation_set__student",
        "graduation_set__graduation_period",
    )


# API Views
class StudentListAPIView(generics.ListAPIView):
    """
    GET /api/students/

    List all students with complete information including:
    - Personal information and contact details
    - Financial information and payment history
    - Academic records and progress
    - Career and study plan information
    - Graduation details (if applicable)

    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search in name, student_id, email
    - student_id: Filter by student ID (partial match)
    - career: Filter by career code
    - academic_status: Filter by academic status
    - campus: Filter by campus
    - is_active: Filter by active status (true/false)
    - has_graduation: Filter students with graduation (true/false)
    - has_financial_debt: Filter students with debt (true/false)
    """

    serializer_class = CompleteStudentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = StudentFilter
    search_fields: ClassVar[list] = [
        "student_id",
        "personal_info__first_name",
        "personal_info__last_name",
        "personal_info__contact_info__institutional_email",
        "personal_info__contact_info__personal_email",
    ]
    ordering_fields: ClassVar[list] = [
        "student_id",
        "enrollment_date",
        "credits_approved",
        "personal_info__first_name",
        "personal_info__last_name",
    ]
    ordering: ClassVar[list] = ["-enrollment_date"]

    def get_queryset(self):
        return Student.objects.select_related(
            "personal_info",
            "personal_info__contact_info",
            "personal_info__identification",
            "personal_info__financial_info",
            "personal_info__academic_profile",
            "personal_info__admission_data",
            "personal_info__emergency_info",
            "personal_info__user_university",
            "personal_info__user_university__university",
            "career",
            "study_plan",
            "admission_period",
            "current_period",
            "graduation",
        ).prefetch_related(
            "personal_info__vehicles",
            "personal_info__vehicles__insurance_info",
            "personal_info__access_control",
            "personal_info__access_control__vehicle",
            "enrollment_set__subject",
            "enrollment_set__period",
            "enrollment_set__professor",
            "academicrecord_set__period",
            "payments",
            "career__study_plans",
            "career__study_plans__subjects",
        )


class StudentListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/students/
    POST /api/students/

    List all students or create new students (bulk creation supported)
    """

    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = StudentFilter
    search_fields: ClassVar[list] = [
        "student_id",
        "personal_info__first_name",
        "personal_info__last_name",
        "personal_info__contact_info__institutional_email",
        "personal_info__contact_info__personal_email",
    ]
    ordering_fields: ClassVar[list] = [
        "student_id",
        "enrollment_date",
        "credits_approved",
        "personal_info__first_name",
        "personal_info__last_name",
    ]
    ordering: ClassVar[list] = ["-enrollment_date"]

    def get_queryset(self):
        return get_student_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StudentCreateUpdateSerializer
        return CompleteStudentSerializer

    def create(self, request, *args, **kwargs):
        """
        Create single or multiple students
        """
        # Check if data is a list (bulk creation)
        is_bulk = isinstance(request.data, list)

        if is_bulk:
            return self.bulk_create(request.data)
        else:
            return self.single_create(request.data)

    @transaction.atomic
    def single_create(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()

        # Return the created student with complete data
        complete_serializer = CompleteStudentSerializer(student)
        return Response(complete_serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def bulk_create(self, data_list):
        """
        Bulk create students
        """
        created_students = []
        errors = []

        for i, student_data in enumerate(data_list):
            try:
                serializer = StudentCreateUpdateSerializer(data=student_data)
                if serializer.is_valid():
                    student = serializer.save()
                    created_students.append(student)
                else:
                    errors.append({"index": i, "errors": serializer.errors})
            except Exception as e:
                errors.append({"index": i, "errors": str(e)})

        if errors:
            return Response(
                {
                    "created": len(created_students),
                    "errors": errors,
                    "created_students": [s.id for s in created_students],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return created students with complete data
        complete_serializer = CompleteStudentSerializer(created_students, many=True)
        return Response(
            {"created": len(created_students), "students": complete_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class StudentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/students/{id}/
    PATCH /api/students/{id}/
    DELETE /api/students/{id}/ (soft delete - inactivate)
    """

    lookup_field = "pk"

    def get_queryset(self):
        return get_student_queryset()

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return StudentCreateUpdateSerializer
        return CompleteStudentSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update student (PATCH only)
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()

        # Return updated student with complete data
        complete_serializer = CompleteStudentSerializer(student)
        return Response(complete_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - inactivate student
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])

        return Response(
            {
                "message": f"Student {instance.student_id} has been inactivated",
                "student_id": instance.student_id,
                "is_active": instance.is_active,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        """
        Disable PUT method, only allow PATCH
        """
        return Response(
            {"error": "PUT method not allowed. Use PATCH for partial updates."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class StaffListAPIView(generics.ListAPIView):
    """
    GET /api/staff/

    List all staff members with complete information including:
    - Personal information and contact details
    - Employment details and responsibilities
    - Supervisor information
    - Vehicle and access control information

    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search in name, staff_id, email
    - department: Filter by department
    - staff_type: Filter by staff type
    - job_title: Filter by job title
    - is_active: Filter by active status (true/false)
    """

    serializer_class = CompleteStaffSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = StaffFilter
    search_fields: ClassVar[list] = [
        "staff_id",
        "user__first_name",
        "user__last_name",
        "user__contact_info__institutional_email",
        "department",
        "job_title",
    ]
    ordering_fields: ClassVar[list] = [
        "staff_id",
        "hire_date",
        "department",
        "job_title",
        "user__first_name",
        "user__last_name",
    ]
    ordering: ClassVar[list] = ["-hire_date"]

    def get_queryset(self):
        return StaffProfile.objects.select_related(
            "user",
            "user__contact_info",
            "user__identification",
            "user__emergency_info",
            "user__user_university",
            "user__user_university__university",
            "supervisor",
            "supervisor__user",
        ).prefetch_related(
            "user__vehicles",
            "user__vehicles__insurance_info",
            "user__access_control",
            "user__access_control__vehicle",
            "responsibilities",
        )


class StaffListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/staff/
    POST /api/staff/
    """

    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = StaffFilter
    search_fields: ClassVar[list] = [
        "staff_id",
        "user__first_name",
        "user__last_name",
        "user__contact_info__institutional_email",
        "department",
        "job_title",
    ]
    ordering_fields: ClassVar[list] = [
        "staff_id",
        "hire_date",
        "department",
        "job_title",
        "user__first_name",
        "user__last_name",
    ]
    ordering: ClassVar[list] = ["-hire_date"]

    def get_queryset(self):
        return get_staff_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StaffCreateUpdateSerializer
        return CompleteStaffSerializer

    def create(self, request, *args, **kwargs):
        is_bulk = isinstance(request.data, list)

        if is_bulk:
            return self.bulk_create(request.data)
        else:
            return self.single_create(request.data)

    @transaction.atomic
    def single_create(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()

        complete_serializer = CompleteStaffSerializer(staff)
        return Response(complete_serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def bulk_create(self, data_list):
        created_staff = []
        errors = []

        for i, staff_data in enumerate(data_list):
            try:
                serializer = StaffCreateUpdateSerializer(data=staff_data)
                if serializer.is_valid():
                    staff = serializer.save()
                    created_staff.append(staff)
                else:
                    errors.append({"index": i, "errors": serializer.errors})
            except Exception as e:
                errors.append({"index": i, "errors": str(e)})

        if errors:
            return Response(
                {
                    "created": len(created_staff),
                    "errors": errors,
                    "created_staff": [s.id for s in created_staff],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        complete_serializer = CompleteStaffSerializer(created_staff, many=True)
        return Response(
            {"created": len(created_staff), "staff": complete_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class StaffDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/staff/{id}/
    PATCH /api/staff/{id}/
    DELETE /api/staff/{id}/ (soft delete)
    """

    lookup_field = "pk"

    def get_queryset(self):
        return get_staff_queryset()

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return StaffCreateUpdateSerializer
        return CompleteStaffSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()

        complete_serializer = CompleteStaffSerializer(staff)
        return Response(complete_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])

        return Response(
            {
                "message": f"Staff member {instance.staff_id} has been inactivated",
                "staff_id": instance.staff_id,
                "is_active": instance.is_active,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        return Response(
            {"error": "PUT method not allowed. Use PATCH for partial updates."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class ProfessorListAPIView(generics.ListAPIView):
    """
    GET /api/professors/

    List all professors with complete information including:
    - Personal information and contact details
    - Academic credentials and specialization
    - Current and historical course assignments
    - Advised graduations
    - Teaching load analysis

    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search in name, professor_id, email
    - department: Filter by department
    - specialization: Filter by specialization
    - academic_degree: Filter by academic degree
    - currently_teaching: Filter professors currently teaching (true/false)
    - is_active: Filter by active status (true/false)
    """

    serializer_class = CompleteProfessorSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProfessorFilter
    search_fields: ClassVar[list] = [
        "professor_id",
        "user__first_name",
        "user__last_name",
        "user__contact_info__institutional_email",
        "department",
        "specialization",
        "academic_degree",
    ]
    ordering_fields: ClassVar[list] = [
        "professor_id",
        "hire_date",
        "department",
        "academic_degree",
        "user__first_name",
        "user__last_name",
    ]
    ordering: ClassVar[list] = ["-hire_date"]

    def get_queryset(self):
        return Professor.objects.select_related(
            "user",
            "user__contact_info",
            "user__identification",
            "user__emergency_info",
            "user__user_university",
            "user__user_university__university",
        ).prefetch_related(
            "user__vehicles",
            "user__vehicles__insurance_info",
            "user__access_control",
            "user__access_control__vehicle",
            "courses_taught",
            "professorsubject_set__subject",
            "professorsubject_set__period",
            "graduation_set__student",
            "graduation_set__graduation_period",
        )


class ProfessorListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/professors/
    POST /api/professors/
    """

    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProfessorFilter
    search_fields: ClassVar[list] = [
        "professor_id",
        "user__first_name",
        "user__last_name",
        "user__contact_info__institutional_email",
        "department",
        "specialization",
        "academic_degree",
    ]
    ordering_fields: ClassVar[list] = [
        "professor_id",
        "hire_date",
        "department",
        "academic_degree",
        "user__first_name",
        "user__last_name",
    ]
    ordering: ClassVar[list] = ["-hire_date"]

    def get_queryset(self):
        return get_professor_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProfessorCreateUpdateSerializer
        return CompleteProfessorSerializer

    def create(self, request, *args, **kwargs):
        is_bulk = isinstance(request.data, list)

        if is_bulk:
            return self.bulk_create(request.data)
        else:
            return self.single_create(request.data)

    @transaction.atomic
    def single_create(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        professor = serializer.save()

        complete_serializer = CompleteProfessorSerializer(professor)
        return Response(complete_serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def bulk_create(self, data_list):
        created_professors = []
        errors = []

        for i, professor_data in enumerate(data_list):
            try:
                serializer = ProfessorCreateUpdateSerializer(data=professor_data)
                if serializer.is_valid():
                    professor = serializer.save()
                    created_professors.append(professor)
                else:
                    errors.append({"index": i, "errors": serializer.errors})
            except Exception as e:
                errors.append({"index": i, "errors": str(e)})

        if errors:
            return Response(
                {
                    "created": len(created_professors),
                    "errors": errors,
                    "created_professors": [p.id for p in created_professors],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        complete_serializer = CompleteProfessorSerializer(created_professors, many=True)
        return Response(
            {"created": len(created_professors), "professors": complete_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class ProfessorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/professors/{id}/
    PATCH /api/professors/{id}/
    DELETE /api/professors/{id}/ (soft delete)
    """

    lookup_field = "pk"

    def get_queryset(self):
        return get_professor_queryset()

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return ProfessorCreateUpdateSerializer
        return CompleteProfessorSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        professor = serializer.save()

        complete_serializer = CompleteProfessorSerializer(professor)
        return Response(complete_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])

        return Response(
            {
                "message": f"Professor {instance.professor_id} has been inactivated",
                "professor_id": instance.professor_id,
                "is_active": instance.is_active,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        return Response(
            {"error": "PUT method not allowed. Use PATCH for partial updates."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


# Additional utility views (keeping your existing ones)
@api_view(["GET"])
def student_by_student_id(request, student_id):
    """
    GET /api/students/by-student-id/{student_id}/
    """
    student = get_object_or_404(get_student_queryset(), student_id=student_id)
    serializer = CompleteStudentSerializer(student)
    return Response(serializer.data)


@api_view(["GET"])
def professor_by_professor_id(request, professor_id):
    """
    GET /api/professors/by-professor-id/{professor_id}/
    """
    professor = get_object_or_404(get_professor_queryset(), professor_id=professor_id)
    serializer = CompleteProfessorSerializer(professor)
    return Response(serializer.data)


@api_view(["GET"])
def staff_by_staff_id(request, staff_id):
    """
    GET /api/staff/by-staff-id/{staff_id}/

    Retrieve staff member by staff_id instead of primary key
    """
    staff = get_object_or_404(
        get_staff_queryset(),
        staff_id=staff_id,
    )
    serializer = CompleteStaffSerializer(staff)
    return Response(serializer.data)


@api_view(["PATCH"])
@transaction.atomic
def bulk_update_students(request):
    """
    PATCH /api/students/bulk-update/

    Bulk update multiple students
    Expected format:
    [
        {"id": 1, "data": {...}},
        {"id": 2, "data": {...}},
    ]
    """
    if not isinstance(request.data, list):
        return Response(
            {"error": "Expected list of objects with id and data fields"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    updated_students = []
    errors = []

    for item in request.data:
        try:
            student_id = item.get("id")
            data = item.get("data", {})

            student = Student.objects.get(pk=student_id)
            serializer = StudentCreateUpdateSerializer(student, data=data, partial=True)

            if serializer.is_valid():
                updated_student = serializer.save()
                updated_students.append(updated_student)
            else:
                errors.append({"id": student_id, "errors": serializer.errors})
        except Student.DoesNotExist:
            errors.append({"id": student_id, "errors": "Student not found"})
        except Exception as e:
            errors.append({"id": student_id, "errors": str(e)})

    complete_serializer = CompleteStudentSerializer(updated_students, many=True)

    return Response(
        {"updated": len(updated_students), "errors": errors, "students": complete_serializer.data},
    )


@api_view(["POST"])
@transaction.atomic
def bulk_inactivate_students(request):
    """
    POST /api/students/bulk-inactivate/

    Bulk inactivate students
    Expected format: {"ids": [1, 2, 3, ...]}
    """
    student_ids = request.data.get("ids", [])

    if not student_ids:
        return Response({"error": "No student IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

    updated_count = Student.objects.filter(id__in=student_ids).update(is_active=False)

    return Response(
        {"message": f"{updated_count} students inactivated", "inactivated_count": updated_count},
    )


@api_view(["POST"])
@transaction.atomic
def bulk_activate_students(request):
    """
    POST /api/students/bulk-activate/

    Bulk activate students
    Expected format: {"ids": [1, 2, 3, ...]}
    """
    student_ids = request.data.get("ids", [])

    if not student_ids:
        return Response({"error": "No student IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

    updated_count = Student.objects.filter(id__in=student_ids).update(is_active=True)

    return Response(
        {"message": f"{updated_count} students activated", "activated_count": updated_count},
    )


# Statistics views
@api_view(["GET"])
def students_statistics(request):
    """
    GET /api/students/statistics/

    Get general statistics about students
    """
    stats = {
        "total_students": Student.objects.count(),
        "active_students": Student.objects.filter(is_active=True).count(),
        "graduated_students": Student.objects.filter(graduation__isnull=False).count(),
        "by_academic_status": dict(
            Student.objects.values("academic_status")
            .annotate(count=Count("id"))
            .values_list("academic_status", "count"),
        ),
        "by_career": dict(
            Student.objects.values("career__name")
            .annotate(count=Count("id"))
            .values_list("career__name", "count"),
        ),
        "by_campus": dict(
            Student.objects.values("campus")
            .annotate(count=Count("id"))
            .values_list("campus", "count"),
        ),
        "average_credits": Student.objects.aggregate(avg_credits=Avg("credits_approved"))[
            "avg_credits"
        ],
        "total_debt": Student.objects.aggregate(
            total=Sum("personal_info__financial_info__total_debt"),
        )["total"]
        or 0,
    }

    return Response(stats)


@api_view(["GET"])
def staff_statistics(request):
    """
    GET /api/staff/statistics/

    Get general statistics about staff
    """
    stats = {
        "total_staff": StaffProfile.objects.count(),
        "active_staff": StaffProfile.objects.filter(is_active=True).count(),
        "by_department": dict(
            StaffProfile.objects.values("department")
            .annotate(count=Count("id"))
            .values_list("department", "count"),
        ),
        "by_staff_type": dict(
            StaffProfile.objects.values("staff_type")
            .annotate(count=Count("id"))
            .values_list("staff_type", "count"),
        ),
    }

    return Response(stats)


@api_view(["GET"])
def professors_statistics(request):
    """
    GET /api/professors/statistics/

    Get general statistics about professors
    """
    stats = {
        "total_professors": Professor.objects.count(),
        "active_professors": Professor.objects.filter(is_active=True).count(),
        "currently_teaching": Professor.objects.filter(professorsubject__period__is_active=True)
        .distinct()
        .count(),
        "by_department": dict(
            Professor.objects.values("department")
            .annotate(count=Count("id"))
            .values_list("department", "count"),
        ),
        "average_teaching_hours": Professor.objects.aggregate(avg_hours=Avg("max_hours_per_week"))[
            "avg_hours"
        ],
        "total_courses_taught": Professor.objects.aggregate(total=Count("courses_taught"))["total"],
    }

    return Response(stats)
