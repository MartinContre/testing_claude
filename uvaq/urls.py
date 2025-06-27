from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccessControlViewSet,
    ContactInformationViewSet,
    EmergencyInformationViewSet,
    EnrollmentViewSet,
    FinancialInformationViewSet,
    IdentificationViewSet,
    InsuranceInformationViewSet,
    PersonalInformationViewSet,
    ProfessorViewSet,
    ResponsibilityViewSet,
    StaffProfileViewSet,
    StudentViewSet,
    SubjectViewSet,
    UniversityInfoViewSet,
    UserUniversityViewSet,
    VehicleViewSet,
)

router = DefaultRouter()
router.register(r"personal", PersonalInformationViewSet)
router.register(r"contact-info", ContactInformationViewSet)
router.register(r"identification", IdentificationViewSet)
router.register(r"access-control", AccessControlViewSet)
router.register(r"emergency-info", EmergencyInformationViewSet)
router.register(r"enrollment", EnrollmentViewSet)
router.register(r"financial-info", FinancialInformationViewSet)
router.register(r"insurance-info", InsuranceInformationViewSet)
router.register(r"professor", ProfessorViewSet)
router.register(r"responsibility", ResponsibilityViewSet)
router.register(r"staff-profile", StaffProfileViewSet)
router.register(r"student", StudentViewSet)
router.register(r"subject", SubjectViewSet)
router.register(r"university-info", UniversityInfoViewSet)
router.register(r"user-university", UserUniversityViewSet)
router.register(r"vehicle", VehicleViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
