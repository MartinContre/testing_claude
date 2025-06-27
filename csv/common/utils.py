import logging
import os
import re

import pandas as pd


def setup_logger(name=__name__, level=logging.DEBUG):
    """
    Set up and return a logger.
    """
    logging.basicConfig(level=level)
    return logging.getLogger(name)


def get_project_base_dir(reference_file, levels_up=2):
    """
    Get the project's base directory.

    :param reference_file: The __file__ attribute of the calling script.
    :param levels_up: Number of directory levels to go up.
                      For example, if the calling script is in 'staff' or 'students',
                      using levels_up=2 returns the project root.
    :return: Absolute path of the project's base directory.
    """
    base_dir = os.path.abspath(reference_file)
    for _ in range(levels_up):
        base_dir = os.path.dirname(base_dir)
    return base_dir


def clean_phone_number(phone):
    """
    Clean a phone number by removing all non-digit characters and ensuring it has exactly 10 digits.
    Returns an empty string if the cleaned phone number does not have 10 digits.
    """
    if pd.isna(phone):
        return ""
    phone = str(phone)
    phone = re.sub(r"\D", "", phone)
    return phone if len(phone) == 10 else ""


def merge_names(
    df, first_name_col="first_name", middle_name_col="middle_name", new_col="name"
):
    """
    Combine the first name and middle name into a single column and drop the original columns.

    :param df: DataFrame containing the name columns.
    :param first_name_col: Name of the first name column.
    :param middle_name_col: Name of the middle name column.
    :param new_col: Name for the combined column.
    :return: DataFrame with the new combined name column.
    """
    df[new_col] = df.apply(
        lambda x: f"{x[first_name_col]} {x[middle_name_col]}".strip()
        if pd.notna(x[middle_name_col]) and x[middle_name_col].strip() != ""
        else x[first_name_col],
        axis=1,
    )
    return df.drop(columns=[first_name_col, middle_name_col])


def fill_missing_curp_and_phone(
    df,
    curp_col="curp",
    identity_number_col="identity_number",
    phone_col="phone",
    cell_phone_col="cell_phone",
    curp_default="XXXX000000XXXXXXXX",
    phone_default="1234567890",
):
    """
    For rows with missing values, update the CURP, identity number, phone, and cell phone columns
    with default values, and accumulate alerts in a single "alert" column.

    :param df: DataFrame containing the data.
    :param curp_col: Name of the CURP column.
    :param identity_number_col: Name of the identity number column.
    :param phone_col: Name of the phone column.
    :param cell_phone_col: Name of the cell phone column.
    :param curp_default: Default value for CURP (and identity number) if missing.
    :param phone_default: Default value for phone and cell phone if missing.
    :return: Updated DataFrame.
    """
    alerts = []

    for idx, row in df.iterrows():
        row_alerts = []
        # Check CURP
        if row[curp_col].strip() == "":
            df.at[idx, curp_col] = curp_default
            row_alerts.append("Missing CURP; default values inserted")
        # Check Identity Number
        if row[identity_number_col].strip() == "":
            df.at[idx, identity_number_col] = curp_default
            row_alerts.append("Missing Identity Number; default values inserted")
        # Check Phone
        if row[phone_col].strip() == "":
            df.at[idx, phone_col] = phone_default
            row_alerts.append("Missing Phone; default values inserted")
        # Check Cell Phone
        if row[cell_phone_col].strip() == "":
            df.at[idx, cell_phone_col] = phone_default
            row_alerts.append("Missing Cell Phone; default values inserted")
        alerts.append("; ".join(row_alerts))

    df["alert"] = alerts
    return df
