import json
import logging
import os
import sys

import django
import pandas as pd
from django.db import transaction

# Configura el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configuración para guardar el log en un archivo con ruta absoluta
log_file_path = os.path.abspath("staff_register.log")
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

# Importar modelos después de configurar Django
from uvaq.models import (
    AccessControl,
    AccessDevice,
    BiometricData,
    ContactInformation,
    EmergencyInformation,
    Identification,
    InsuranceInformation,
    Notification,
    PersonalInformation,
    Role,
    StaffProfile,
    UniversityInfo,
    UserUniversity,
    Vehicle,
)

# Construir la ruta al archivo CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "staff", "valid_rows.csv")

# Cargar el CSV con pandas
df = pd.read_csv(csv_path, quotechar='"', sep=",", encoding="utf-8")

# Reemplazar NaN con strings vacíos para evitar problemas con valores nulos
df = df.fillna("")

df["is_duplicate"] = df.duplicated(subset=["photo"], keep=False)


@transaction.atomic
def insert_staff_data(row):
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

        # Parsear JSON
        vehicle_details = (
            json.loads(row["vehicle_details"]) if row["vehicle_details"] else []
        )
        biometric_data = (
            json.loads(row["biometric_data"]) if row["biometric_data"] else []
        )
        access_devices = (
            json.loads(row["access_devices"]) if row["access_devices"] else []
        )

    except json.JSONDecodeError as e:
        logger.error(
            f"Error while parse JSON in the row:  {first_name} {last_name} {second_last_name}: {str(e)}"
        )
        logger.error(f"Problematic content: {row}")
        return
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return

    # Personal Information
    personal_info = PersonalInformation.objects.create(
        first_name=first_name,
        last_name=last_name,
        second_last_name=second_last_name,
        birth_date=row["birth_date"],
        gender=row["gender"],
        photo=photo_url,
        digital_signature=row["digital_signature"],
        role=Role.SERVICES,
    )

    # Contact Information
    ContactInformation.objects.create(
        user=personal_info,
        phone=row["phone"],
        cell_phone=row["cell_phone"],
        personal_email=row["personal_email"],
        institutional_email=institutional_email,
        preferred_contact_method=row["preferred_contact_method"],
    )

    # Identification
    Identification.objects.create(
        user=personal_info,
        curp=curp,
        identity_number=identity_number,
        nationality=row["nationality"],
    )

    # Staff Profile
    staff_profile = StaffProfile.objects.create(
        user=personal_info,
        department=row["department"],
        job_title=row["job_title"],
        work_hours=row["work_hours"],
        staff_id=row["staff_id"],
    )

    if vehicle_details:
        # Access Control
        access_control = AccessControl.objects.create(
            user=personal_info,
            access_level=row["access_level"],
            access_hours=row["access_hours"],
        )

        # Vehicle Details and Insurance
        vehicle_objects = []
        for vehicle_data in vehicle_details:
            vehicle, created = Vehicle.objects.get_or_create(
                owner=personal_info,
                plate_number=vehicle_data["plate_number"],
                model=vehicle_data["model"],
                vehicle_type=vehicle_data["vehicle_type"],
                color=vehicle_data["color"],
            )
            InsuranceInformation.objects.create(
                vehicle=vehicle,
                policy_number=vehicle_data["insurance_policy_number"],
                provider=vehicle_data["insurance_provider"],
            )
            vehicle_objects.append(vehicle)
            access_control.vehicle.set(vehicle_objects)
            access_control.save()

        # Biometric Data
        for biometric in biometric_data:
            BiometricData.objects.create(
                access_control=access_control,
                biometric_type=biometric["biometric_type"],
                data=biometric["data"],
            )

        # Access Devices
        for device in access_devices:
            AccessDevice.objects.create(
                access_control=access_control,
                device_type=device["device_type"],
                device_id=device["device_id"],
            )

    # Emergency Information
    EmergencyInformation.objects.create(
        user=personal_info,
        name=row["emergency_name"],
        phone=row["emergency_phone"],
    )

    # University Info
    university_info, created = UniversityInfo.objects.get_or_create(
        name=row["university_name"],
        identifier=row["university_identifier"],
        additional_info=row["university_additional_info"],
    )

    # UserUniversity (incluyendo Roles y Notificaciones)
    user_university = UserUniversity.objects.create(
        user=personal_info,
        user_identifier=row["staff_id"],
        user_roles=Role.SERVICES,
        mandatory_notification=Role.SERVICES,
        enrollment_date=row["enrollment_date"],
        campus=row["campus"],
        career=row["career"],
        university=university_info,
    )

    # Optional Notifications
    if row["optional_notifications"]:
        optional_notifications = json.loads(row["optional_notifications"])
        for notification in optional_notifications:
            notification_obj, _ = Notification.objects.get_or_create(
                name=notification["name"]
            )
            user_university.optional_notifications.add(notification_obj)

    return True


# Iterar sobre cada fila del CSV e insertar la información
for _, row in df.iterrows():
    try:
        if insert_staff_data(row):
            logger.info(f"Inserted data for {row['first_name']} {row['last_name']}.")
    except Exception as e:
        logger.error(
            f"Error while insert data for {row['first_name']} {row['last_name']}: {str(e)}"
        )
