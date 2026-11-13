
import math


def validate_blood_type(blood_code):
    """
    Standardizes blood group and Rh factor (e.g. 'O+', 'AB-').
    Handles invalid and unexpected inputs safely.
    """
    if not isinstance(blood_code, str):
        return "Invalid blood type"

    cleaned = blood_code.strip().upper()

    if len(cleaned) < 2:
        return "Invalid blood type"

    antigen = cleaned[:-1]
    rh_char = cleaned[-1]

    if antigen not in ("A", "B", "AB", "O") or rh_char not in ("+", "-"):
        return "Invalid blood type"

    rh_map = {"+": "Positive", "-": "Negative"}
    return f"{antigen} {rh_map[rh_char]}"


def calculate_pulse_pressure(bp_string):
    """
    Calculates pulse pressure (systolic - diastolic) and arterial ratio.
    Handles invalid formats and zero diastolic pressure safely.
    """
    if not isinstance(bp_string, str):
        return "Invalid blood pressure"

    parts = bp_string.strip().split('/')

    if len(parts) != 2:
        return "Invalid blood pressure"

    try:
        systolic = int(parts[0].strip())
        diastolic = int(parts[1].strip())
    except ValueError:
        return "Invalid blood pressure"

    if systolic <= 0 or diastolic <= 0 or systolic < diastolic:
        return "Invalid blood pressure"

    pulse_diff = systolic - diastolic
    ratio = round(systolic / diastolic, 2)

    return f"Diff: {pulse_diff}, Ratio: {ratio}"


def parse_donor_registry(donor_entry):
    """
    Parses pipe-delimited record: 'DonorID|WeightKg|Hemoglobin'.
    Handles malformed records and invalid numeric values safely.
    """
    if not isinstance(donor_entry, str):
        return "Invalid donor record"

    fields = donor_entry.split('|')

    if len(fields) != 3:
        return "Invalid donor record"

    donor_id = fields[0].strip()

    if not donor_id:
        return "Invalid donor record"

    try:
        weight = float(fields[1].strip())
        hemoglobin = float(fields[2].strip())
    except ValueError:
        return "Invalid donor record"

    if not math.isfinite(weight) or not math.isfinite(hemoglobin):
        return "Invalid donor record"

    if weight < 0 or hemoglobin < 0:
        return "Invalid donor record"

    eligible = weight >= 50.0 and hemoglobin >= 12.5

    return f"Donor {donor_id}: {'Eligible' if eligible else 'Deferred'}"


def main():
    print("==== Running validate_blood_type ====")
    b_input = input("Enter blood type (e.g. A+, O-, AB+): ")
    print("Validated:", validate_blood_type(b_input))

    print("\n==== Running calculate_pulse_pressure ====")
    bp_input = input("Enter BP (e.g. 120/80): ")
    print("BP Metrics:", calculate_pulse_pressure(bp_input))

    print("\n==== Running parse_donor_registry ====")
    d_input = input("Enter record (ID|Weight|Hemoglobin): ")
    print("Status:", parse_donor_registry(d_input))


if __name__ == "__main__":
    main()
