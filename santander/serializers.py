import logging
import re

from rest_framework import serializers

from uvaq.models import (
    ContactInformation,
    Identification,
    PersonalInformation,
    Professor,
    Role,
    Student,
    UserUniversity,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

ROLE_TRANSLATIONS = {
    "student": "Estudiante",
    "professor": "Profesor",
    "services": "Servicio",
    "tester": "tester",
}


class PersonNameSerializer(serializers.ModelSerializer):
    givenName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    secondLastName = serializers.CharField(source="second_last_name")

    class Meta:
        model = PersonalInformation
        fields = ["givenName", "lastName", "secondLastName"]


class ContactPointSerializer(serializers.ModelSerializer):
    telephone = serializers.CharField(
        source="contact_info.phone",
        allow_null=True,
        default=None,
    )
    emailAddress = serializers.EmailField(
        source="contact_info.institutional_email",
        allow_null=True,
        default=None,
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        phone = representation.get("telephone")
        if phone:
            formatted_phone = self.format_phone(phone)
            representation["telephone"] = formatted_phone
        return representation

    def format_phone(self, phone):
        pattern = r"(\d{3})(\d{3})(\d{4})"
        match = re.match(pattern, phone)
        if match:
            return f"({match.group(1)}) {match.group(2)} {match.group(3)}"
        return phone

    class Meta:
        model = ContactInformation
        fields = ["telephone", "emailAddress"]


class DocumentSerializer(serializers.ModelSerializer):
    documentNumber = serializers.CharField(
        source="identification.curp",
        allow_null=True,
        default=None,
    )
    issuerEntityCountry = serializers.CharField(
        source="identification.nationality",
        allow_null=True,
        default=None,
    )

    class Meta:
        model = Identification
        fields = ["documentNumber", "issuerEntityCountry"]


class UniversitySerializer(serializers.Serializer):
    universityId = serializers.CharField(source="university_identifier")

    class Meta:
        model = UserUniversity
        fields = ["universityId"]


class RoleSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = UserUniversity
        fields = ["name"]

    def get_name(self, obj):
        return ROLE_TRANSLATIONS.get(obj.user.role, obj.user.role)


class UserImageSerializer(serializers.Serializer):
    url = serializers.URLField()


class UserUniversitySerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField()
    creationDate = serializers.DateField(source="enrollment_date")
    university = UniversitySerializer(source="*")
    role = RoleSerializer(source="*")
    userImage = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    additionalUniversityUserData = serializers.SerializerMethodField()

    class Meta:
        model = UserUniversity
        fields = [
            "userId",
            "creationDate",
            "userImage",
            "university",
            "role",
            "courses",
            "additionalUniversityUserData",
        ]

    def get_userId(self, obj):
        if obj.user.role == Role.STUDENT:
            return obj.user.student.student_id
        elif obj.user.role == Role.PROFESSOR:
            return obj.user.professor.professor_id
        elif obj.user.role == Role.SERVICES:
            return obj.user.staff_profile.staff_id
        else:
            return "000000"

    def get_courses(self, obj):
        if obj.user.role == "services":
            # For 'services', map department to 'name' in courses
            staff_profile = getattr(obj.user, "staff_profile", None)
            department_name = staff_profile.department if staff_profile else "Default Department"
            return [{"name": department_name, "type": "other"}]
        elif obj.user.role == "student":
            user_university = getattr(obj.user, "user_university", None)
            if user_university:
                try:
                    student = Student.objects.get(student_id=user_university.user_identifier)
                    subjects = student.get_subjects_list()
                    university_career = {
                        "name": user_university.career,
                        "type": user_university.type,
                    }
                    return [university_career] + subjects

                except Student.DoesNotExist as e:
                    logger.error(f"Student not found {e.args}.", exc_info=True)
                    return None
                except Exception as e:
                    logger.error(f"Unexpected error occurred {e.args}.", exc_info=True)
                    return None
        elif obj.user.role == "professor":
            user_university = getattr(obj.user, "user_university", None)
            if user_university:
                try:
                    professor = Professor.objects.get(professor_id=user_university.user_identifier)
                    subject_list = professor.get_courses_list()
                    university_career = {
                        "name": user_university.career,
                        "type": user_university.type,
                    }
                    return [university_career] + subject_list

                except Professor.DoesNotExist as e:
                    logger.error(f"Professor not found {e.args}.", exc_info=True)
                    return None
                except Exception as e:
                    logger.error(f"Unexpected error occurred {e.args}.", exc_info=True)
                    return None
        elif obj.career and obj.type:
            # For other roles, include career and type
            return [{"name": obj.career, "type": obj.type}]
        return None

    def get_additionalUniversityUserData(self, obj):
        # Default values for additional university user data
        return [
            {
                "label": "Face",
                "value": "https://www.facebook.com/uvaqoficial",
                "valueType": "link",
            },
            {
                "label": "Group",
                "value": "Grupo A",
                "valueType": "text",
            },
            {
                "label": "Image",
                "value": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwJksRWkLgybSxiHatpg3FtU5xEgJhg4ZglQ&s",
                "valueType": "image",
            },
        ]

    def get_userImage(self, obj):
        return (
            {"url": obj.user.photo}
            if obj.user.photo
            else {"url": "https://funi.edu.mx/default_image.jpg"}
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Clean up unused fields
        if not representation.get("courses"):
            representation.pop("courses", None)
        if not representation.get("userId"):
            representation["userId"] = "000000"
        if not representation.get("creationDate"):
            representation["creationDate"] = "1900-01-01"
        if not representation["role"]["name"]:
            representation["role"]["name"] = "Tester"

        return representation


class UserNotificationsGroupsSerializer(serializers.Serializer):
    mandatory = serializers.SerializerMethodField()
    optional = serializers.SerializerMethodField()

    class Meta:
        fields = ["mandatory", "optional"]

    def get_mandatory(self, obj):
        return [obj.user.role if obj.user.role else Role.TESTER]

    def get_optional(self, obj):
        optional_groups = []
        role = obj.user.role
        if role == "student":
            if obj.career:
                optional_groups.append(f"Estudiante de {obj.career}")
            if obj.campus:
                optional_groups.append(f"Estudiante de {obj.campus}")
        elif role == "professor":
            if obj.career:
                optional_groups.append(f"Profesor de {obj.career}")
            if obj.campus:
                optional_groups.append(f"Profesor de {obj.campus}")
        elif role == "services":
            if obj.campus:
                optional_groups.append(f"{obj.campus}")

        optional_notifications = obj.optional_notifications.all()
        for notification in optional_notifications:
            optional_groups.append(notification.name)
        return optional_groups if optional_groups else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not representation.get("mandatory"):
            representation["mandatory"] = [Role.TESTER]

        if not representation.get("optional"):
            representation.pop("optional", None)

        return representation


class PersonSerializer(serializers.ModelSerializer):
    personName = PersonNameSerializer(source="*")
    contactPoint = ContactPointSerializer(source="*")
    document = DocumentSerializer(source="*")
    nationality = serializers.SerializerMethodField()
    birthDate = serializers.DateField(source="birth_date")

    class Meta:
        model = PersonalInformation
        fields = ["personName", "contactPoint", "document", "nationality", "birthDate"]

    def get_nationality(self, obj):
        if obj.identification:
            nationality = obj.identification.nationality
            return {"countryCode": nationality if nationality else "MX"}
        return {"countryCode": "MX"}

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not representation.get("personName"):
            representation["personName"] = {
                "givenName": "Test",
                "lastName": "Tester",
                "secondLastName": "Tester",
            }
        if not representation.get("contactPoint"):
            representation["contactPoint"] = {
                "telephone": "(000) 000 0000",
                "emailAddress": "no-email@domain.com",
            }
        if not representation.get("document"):
            representation["document"] = {
                "documentNumber": "XXXX000000XXXXXX00",
                "issuerEntityCountry": "MX",
            }
        if not representation.get("nationality"):
            representation["nationality"] = {"countryCode": "MX"}
        if not representation.get("birthDate"):
            representation["birthDate"] = "1900-01-01"
        return representation


class SantanderPersonSerializer(serializers.ModelSerializer):
    person = PersonSerializer(source="*")
    userUniversities = serializers.SerializerMethodField()
    userNotificationsGroups = UserNotificationsGroupsSerializer(source="user_university")

    class Meta:
        model = PersonalInformation
        fields = ["person", "userUniversities", "userNotificationsGroups"]

    def get_userUniversities(self, obj):
        user_university = getattr(obj, "user_university", None)
        if user_university:
            serializer = UserUniversitySerializer(user_university)
            return [serializer.data]
        return []

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        non_required_fields = ["userUniversities", "userNotificationsGroups"]
        for field in non_required_fields:
            if not representation.get(field):
                representation.pop(field, None)

        return representation
