from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from authentication.hybrid_authentication import HybridAuthentication
from authentication.mixins import AuthorizedUserRequiredMixin

from .models import (
    AccessControl,
    ContactInformation,
    EmergencyInformation,
    Enrollment,
    FinancialInformation,
    Identification,
    InsuranceInformation,
    PersonalInformation,
    Professor,
    Responsibility,
    StaffProfile,
    Student,
    Subject,
    UniversityInfo,
    UserUniversity,
    Vehicle,
)
from .serializers import (
    AccessControlSerializer,
    ContactInformationSerializer,
    EmergencyInformationSerializer,
    EnrollmentSerializer,
    FinancialInformationSerializer,
    IdentificationSerializer,
    InsuranceInformationSerializer,
    PersonalInformationSerializer,
    ProfessorSerializer,
    ResponsibilitySerializer,
    StaffProfileSerializer,
    StudentSerializer,
    SubjectSerializer,
    UniversityInfoSerializer,
    UserUniversitySerializer,
    VehicleSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PersonalInformationViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = PersonalInformation.objects.all()
    serializer_class = PersonalInformationSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class ContactInformationViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = ContactInformation.objects.all()
    serializer_class = ContactInformationSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class IdentificationViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = Identification.objects.all()
    serializer_class = IdentificationSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class AccessControlViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = AccessControl.objects.all()
    serializer_class = AccessControlSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class EmergencyInformationViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = EmergencyInformation.objects.all()
    serializer_class = EmergencyInformationSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class EnrollmentViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class FinancialInformationViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = FinancialInformation.objects.all()
    serializer_class = FinancialInformationSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class InsuranceInformationViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = InsuranceInformation.objects.all()
    serializer_class = InsuranceInformationSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class ProfessorViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class ResponsibilityViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = Responsibility.objects.all()
    serializer_class = ResponsibilitySerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class StaffProfileViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class StudentViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class SubjectViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class UniversityInfoViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = UniversityInfo.objects.all()
    serializer_class = UniversityInfoSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class UserUniversityViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = UserUniversity.objects.all()
    serializer_class = UserUniversitySerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]


class VehicleViewSet(AuthorizedUserRequiredMixin, viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]
