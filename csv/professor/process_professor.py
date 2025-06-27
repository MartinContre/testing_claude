import logging
import os
import re

import pandas as pd
from common.utils import (
    clean_phone_number,
    fill_missing_curp_and_phone,
    get_project_base_dir,
    merge_names,
    setup_logger,
)

from .career_type_mapper import map_career_type

logger = setup_logger(__name__)

# Define file paths
BASE_DIR = get_project_base_dir(__file__, levels_up=2)
csv_path = os.path.join(BASE_DIR, "professor", "professors february 2025.csv")

# Load CSV file
try:
    df = pd.read_csv(csv_path, quotechar='"', sep=",", encoding="utf-8")
except FileNotFoundError:
    logger.error(f"File not found: {csv_path}")
    exit(1)


# Replace '\N' values with empty strings
df = df.fillna("")
df = df.astype(str)
df = df.replace(r"\\N", "", regex=True)

# If the professor file includes first_name and middle_name, merge them.
# (If not, you can comment out the following line.)
df = merge_names(
    df, first_name_col="first_name", middle_name_col="middle_name", new_col="name"
)


# Clean phone number columns using the common function
df["phone"] = df["phone"].apply(clean_phone_number)
df["cell_phone"] = df["cell_phone"].apply(clean_phone_number)

df["phone"] = df.apply(
    lambda x: x["cell_phone"] if not x["phone"] else x["phone"], axis=1
)
df["cell_phone"] = df.apply(
    lambda x: x["phone"] if not x["cell_phone"] else x["cell_phone"], axis=1
)


# Fill missing CURP (and update phone) if necessary; rows will have an alert if defaults were inserted
df = fill_missing_curp_and_phone(
    df,
    curp_col="curp",
    identity_number_col="identity_number",
    phone_col="phone",
    cell_phone_col="cell_phone",
)

column_order = ["name"] + [col for col in df.columns if col != "name"]
df = df[column_order]

if "university_additional_info" in df.columns:
    df["university_additional_info"] = df["university_additional_info"].replace(
        r"^\s*$", "", regex=True
    )
    df["university_additional_info"] = df["university_additional_info"].replace("0", "")


df["institutional_email_lower"] = df["institutional_email"].str.strip().str.lower()


df["career_type"] = df["career"].apply(map_career_type)

group_invalid_email = df[
    ~df["institutional_email_lower"].str.endswith("@uvaq.edu.mx", na=False)
].copy()

if "alert" in group_invalid_email.columns:
    group_invalid_email = group_invalid_email.drop(columns=["alert"])
group_invalid_email["alert"] = "Invalid email"

group_defaults = df[
    (df["alert"].str.strip() != "")
    & (df["institutional_email_lower"].str.endswith("@uvaq.edu.mx", na=False))
].copy()

group_valid = df[
    df["institutional_email_lower"].str.endswith("@uvaq.edu.mx", na=False)
].copy()
if "alert" in group_valid.columns:
    group_valid = group_valid.drop(columns=["alert"])

for group in [group_invalid_email, group_defaults, group_valid]:
    if "institutional_email_lower" in group.columns:
        group.drop(columns=["institutional_email_lower"], inplace=True)

invalid_email_path = os.path.join(BASE_DIR, "professor", "invalid_email.csv")
defaults_path = os.path.join(BASE_DIR, "professor", "defaults_filled.csv")
valid_path = os.path.join(BASE_DIR, "professor", "valid_rows.csv")

group_invalid_email.to_csv(invalid_email_path, index=False, encoding="utf-8")
group_defaults.to_csv(defaults_path, index=False, encoding="utf-8")
group_valid.to_csv(valid_path, index=False, encoding="utf-8")

logger.info(f"Invalid email data saved to {invalid_email_path}")
logger.info(f"Defaults filled data saved to {defaults_path}")
logger.info(f"Valid data saved to {valid_path}")
