import json
import logging
import os
import sys

import django
import pandas as pd
from django.db import transaction
from django.db.models import Q

# Configura el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configuración para guardar el log en un archivo con ruta absoluta
log_file_path = os.path.abspath("professor_register.log")
file_handler = logging.FileHandler(log_file_path)  # Append mode
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# StreamHandler adicional para consola
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Configurar Django
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hub.settings")
django.setup()

from uvaq.models import (
    AccessControl,
    AccessDevice,
    BiometricData,
    Career,
    ContactInformation,
    EmergencyInformation,
    Identification,
    InsuranceInformation,
    Notification,
    PersonalInformation,
    Professor,
    Role,
    Subject,
    UniversityInfo,
    UserUniversity,
    Vehicle,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "professor", "professor_november_2024_cleaned.csv")

df = pd.read_csv(csv_path, quotechar='"', sep=",", encoding="utf-8")

df = df.fillna("")
df["is_duplicate"] = df.duplicated(subset=["photo"], keep=False)


@transaction.atomic
def insert_professor_data(row):
    try:
        first_name = row["first_name"]
        last_name = row["last_name"]
        second_last_name = row["second_last_name"]

        institutional_email = row["institutional_email"].strip().lower()
        if not institutional_email.endswith("@uvaq.edu.mx"):
            raise ValueError(
                f"The institutional email '{institutional_email}' does not have the mandatory domain '@uvaq.edu.mx'."
            )
        curp = row["curp"].strip().upper()
        if not curp:
            raise ValueError(f"The CURP for {first_name} {last_name} is incorrect.")
        photo_url = row["photo"]
        if row["is_duplicate"]:
            raise ValueError(
                f"Duplicated found: {photo_url} for {first_name} {last_name} {second_last_name} {photo_url}"
            )
        identity_number = row["identity_number"]
        if not identity_number:
            raise ValueError(
                f"The identity number for {first_name} {last_name} {second_last_name} is incorrect."
            )

        courses_taught = (
            json.loads(row["courses_taught"]) if row["courses_taught"] else []
        )
        vehicle_details = (
            json.loads(row["vehicle_details"]) if row["vehicle_details"] else []
        )
        biometric_data = (
            json.loads(row["biometric_data"]) if row["biometric_data"] else []
        )
        access_devices = (
            json.loads(row["access_devices"]) if row["access_devices"] else []
        )
        careers = json.loads(row["career"]) if row["career"] else []

    except json.JSONDecodeError as e:
        logger.error(
            f"Error al parsear JSON en la fila de {row['first_name']} {row['last_name']}: {str(e)}"
        )
        logger.error(f"Contenido problemático: {row}")
        return
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return

    contact_info = ContactInformation.objects.filter(
        Q(institutional_email=institutional_email)
    ).first()

    if not contact_info:
        personal_info = PersonalInformation.objects.create(
            first_name=first_name,
            last_name=last_name,
            second_last_name=second_last_name,
            birth_date=row["birth_date"],
            gender=row["gender"],
            photo=photo_url,
            digital_signature=row["digital_signature"],
            role=Role.PROFESSOR,
        )
    else:
        personal_info = contact_info.user

    ContactInformation.objects.update_or_create(
        user=personal_info,
        defaults={
            "phone": row["phone"],
            "cell_phone": row["cell_phone"],
            "personal_email": row["personal_email"],
            "institutional_email": institutional_email,
            "preferred_contact_method": row["preferred_contact_method"],
        },
    )

    Identification.objects.update_or_create(
        user=personal_info,
        curp=curp,
        identity_number=row["identity_number"],
        nationality=row["nationality"],
    )

    professor = Professor.objects.create(
        user=personal_info,
        professor_id=row["professor_id"],
        department=row["department"],
        work_hours=row["work_hours"],
    )

    first_career = None
    for career_data in careers:
        career_obj, created = Career.objects.get_or_create(name=career_data["name"])
        career_obj.professors.add(professor)
        if not first_career:
            first_career = career_obj.name

    for course_data in courses_taught:
        subject, _ = Subject.objects.get_or_create(name=course_data["name"])
        professor.courses_taught.add(subject)

    if vehicle_details:
        access_control = AccessControl.objects.update_or_create(
            user=personal_info,
            access_level=row["access_level"],
            access_hours=row["access_hours"],
        )

        vehicle_objects = []
        for vehicle_data in vehicle_details:
            vehicle, created = Vehicle.objects.get_or_create(
                owner=personal_info,
                plate_number=vehicle_data["plate_number"],
                model=vehicle_data["model"],
                vehicle_type=vehicle_data["vehicle_type"],
                color=vehicle_data["color"],
            )
            InsuranceInformation.objects.update_or_create(
                vehicle=vehicle,
                policy_number=vehicle_data["insurance_policy_number"],
                provider=vehicle_data["insurance_provider"],
            )
            vehicle_objects.append(vehicle)
            access_control.vehicle.set(vehicle_objects)
            access_control.save()

        for biometric in biometric_data:
            BiometricData.objects.update_or_create(
                access_control=access_control,
                biometric_type=biometric["biometric_type"],
                data=biometric["data"],
            )

        for device in access_devices:
            AccessDevice.objects.update_or_create(
                access_control=access_control,
                device_type=device["device_type"],
                device_id=device["device_id"],
            )

    EmergencyInformation.objects.update_or_create(
        user=personal_info,
        name=row["emergency_name"],
        phone=row["emergency_phone"],
    )

    university_info, created = UniversityInfo.objects.get_or_create(
        name=row["university_name"],
        identifier=row["university_identifier"],
        additional_info=row["university_additional_info"],
    )

    if not contact_info:
        user_university = UserUniversity.objects.update_or_create(
            user=personal_info,
            user_identifier=row["professor_id"],
            user_roles=Role.PROFESSOR,
            mandatory_notification=Role.PROFESSOR,
            enrollment_date=row["enrollment_date"],
            campus=row["campus"],
            career=first_career,
            university=university_info,
            type=row["career_type"],
        )
    else:
        user_university = personal_info

    if row["optional_notifications"]:
        optional_notifications = json.loads(row["optional_notifications"])
        for notification in optional_notifications:
            notification_obj, _ = Notification.objects.get_or_create(
                name=notification["name"]
            )
            user_university.optional_notifications.add(notification_obj)

    return True


for _, row in df.iterrows():
    try:
        if insert_professor_data(row):
            logger.info(f"Inserted data for {row['first_name']} {row['last_name']}.")
    except Exception as e:
        logger.error(
            f"Error while insert data for {row['first_name']} {row['last_name']}: {str(e)}"
        )
