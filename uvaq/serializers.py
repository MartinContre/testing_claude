from rest_framework import serializers

from .models import (
    AccessControl,
    ContactInformation,
    EmergencyInformation,
    Enrollment,
    FinancialInformation,
    Identification,
    InsuranceInformation,
    Notification,
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


def validate_user_role(profile, user, expected_role):
    if user.role != expected_role:
        raise serializers.ValidationError(
            f"The {profile} can only be assigned to users with the role of '{expected_role}'."
        )


class PersonalInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for personal information of a user.

    This serializer handles the CRUD operations for the `PersonalInformation` model,
    which contains sensitive details about the user, such as name, date of birth, etc.
    """

    class Meta:
        model = PersonalInformation
        fields = "__all__"


class ContactInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for the contact information associated with a user.

    Attributes:
        user (PrimaryKeyRelatedField): Foreign key to the `PersonalInformation` model.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = ContactInformation
        fields = "__all__"


class IdentificationSerializer(serializers.ModelSerializer):
    """
    Serializer for identification details linked to a user.

    Attributes:
        user (PrimaryKeyRelatedField): Links to the `PersonalInformation` model.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = Identification
        fields = "__all__"


class AccessControlSerializer(serializers.ModelSerializer):
    """
    Serializer for managing access control systems related to users.

    Attributes:
        user (PrimaryKeyRelatedField): Links to the `PersonalInformation` model.
        vehicle (PrimaryKeyRelatedField): Links to the `Vehicle` model (optional).
    """

    user = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = AccessControl
        fields = "__all__"


class FinancialInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling financial information related to a user.

    Attributes:
        user (PrimaryKeyRelatedField): Links to the `PersonalInformation` model.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = FinancialInformation
        fields = "__all__"


class UserUniversitySerializer(serializers.ModelSerializer):
    """
    Serializer for the relationship between a user and the university.

    Attributes:
        user (PrimaryKeyRelatedField): Links to the `PersonalInformation` model.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = UserUniversity
        fields = "__all__"


class EmergencyInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for emergency contact information of a user.

    Attributes:
        user (PrimaryKeyRelatedField): Links to `PersonalInformation`.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = EmergencyInformation
        fields = "__all__"


class InsuranceInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for insurance details of a vehicle.

    Attributes:
        vehicle (PrimaryKeyRelatedField): Links to the `Vehicle` model.
        policy_number (CharField): Unique policy number for the insurance.
        provider (CharField): Insurance provider's name.
    """

    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())

    class Meta:
        model = InsuranceInformation
        fields = "__all__"


class ProfessorSerializer(serializers.ModelSerializer):
    """
    Serializer for the professor profile.

    This serializer handles the creation and update of professor profiles, ensuring
    that only users with the role of 'professor' can have a professor profile.

    Attributes:
        user (PrimaryKeyRelatedField): Links to `PersonalInformation`, validating that the user role is 'professor'.

    Raises:
        ValidationError: If the user's role is not 'professor'.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = Professor
        fields = "__all__"

    def validate(self, data):
        validate_user_role("Professor profile", data["user"], "professor")
        return data


class StaffProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for managing staff profile information.

    Attributes:
        user (PrimaryKeyRelatedField): Links to the `PersonalInformation` model.

    Validation:
        Ensures that only users with the 'staff' role can have a staff profile.

    Raises:
        ValidationError: If the user's role is not 'staff'.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = StaffProfile
        fields = "__all__"

    def validate(self, data):
        validate_user_role("Staff profile", data["user"], "staff")
        return data


class ResponsibilitySerializer(serializers.ModelSerializer):
    staff_profile = serializers.PrimaryKeyRelatedField(queryset=StaffProfile.objects.all())

    class Meta:
        model = Responsibility
        fields = "__all__"


class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = Vehicle
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class UniversityInfoSerializer(serializers.ModelSerializer):
    user_university = serializers.PrimaryKeyRelatedField(queryset=UserUniversity.objects.all())

    class Meta:
        model = UniversityInfo
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the enrollment of students in subjects.

    This serializer manages the linking of students to subjects through the `Enrollment` model,
    which keeps track of the student's status and grade in the subject.

    Attributes:
        student (PrimaryKeyRelatedField): Foreign key to `Student`.
        subject (PrimaryKeyRelatedField): Foreign key to `Subject`.

    Meta:
        unique_together: Ensures that a student can only enroll in a subject once.
    """

    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    class Meta:
        model = Enrollment
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    personal_info = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all())

    class Meta:
        model = Student
        fields = "__all__"
