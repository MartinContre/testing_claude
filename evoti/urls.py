from django.urls import path

from evoti.views import (
    ProfessorDetailAPIView,
    ProfessorListAPIView,
    StaffDetailAPIView,
    StaffListAPIView,
    StudentDetailAPIView,
    StudentListAPIView,
    professor_by_professor_id,
    professors_statistics,
    staff_by_staff_id,
    staff_statistics,
    student_by_student_id,
    students_statistics,
)

urlpatterns = [
    # Student endpoints
    path("students/", StudentListAPIView.as_view(), name="student-list"),
    path("students/<int:pk>/", StudentDetailAPIView.as_view(), name="student-detail"),
    path("students/by-student-id/<str:student_id>/", student_by_student_id, name="student-by-id"),
    path("students/statistics/", students_statistics, name="students-statistics"),
    # Staff endpoints
    path("staff/", StaffListAPIView.as_view(), name="staff-list"),
    path("staff/<int:pk>/", StaffDetailAPIView.as_view(), name="staff-detail"),
    path("staff/by-staff-id/<str:staff_id>/", staff_by_staff_id, name="staff-by-id"),
    path("staff/statistics/", staff_statistics, name="staff-statistics"),
    # Professor endpoints
    path("professors/", ProfessorListAPIView.as_view(), name="professor-list"),
    path("professors/<int:pk>/", ProfessorDetailAPIView.as_view(), name="professor-detail"),
    path(
        "professors/by-professor-id/<str:professor_id>/",
        professor_by_professor_id,
        name="professor-by-id",
    ),
    path("professors/statistics/", professors_statistics, name="professors-statistics"),
]
