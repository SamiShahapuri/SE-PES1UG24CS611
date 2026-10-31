"""Line (statement) coverage tests for blood_donation_screening.py"""
import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


def make_cohort(donors, registered=True, ctype="standard", fast_track=False):
    return {"clinic_registered": registered, "type": ctype,
            "fast_track": fast_track, "donors": donors}


def donor(age=25, weight=65, hb=14.0):
    return {"age": age, "weight_kg": weight, "hb": hb}


# ---------- process_donor_cohort ----------
def test_single_accepted_donor():
    result = process_donor_cohort([make_cohort([donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        process_donor_cohort("not a list", 450)


def test_unregistered_cohort_skipped():
    result = process_donor_cohort([make_cohort([donor()], registered=False)], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_underage_donor_deferred():
    result = process_donor_cohort([make_cohort([donor(age=16), donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_low_hb_high_altitude_resets_total():
    cohorts = [make_cohort([donor(), donor(hb=11.0), donor()], ctype="high_altitude")]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_hb_deferred():
    result = process_donor_cohort([make_cohort([donor(hb=19.0), donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_fast_track_bonus():
    result = process_donor_cohort([make_cohort([donor()], fast_track=True)], 450)
    assert result == {"collected_ml": 500, "status": "ACCEPTED"}


def test_high_deferral_status():
    cohorts = [make_cohort([donor(age=10)] * 5 + [donor()])]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


# ---------- verify_storage_centrifuge ----------
def test_centrifuge_no_data():
    assert verify_storage_centrifuge([]) == "NO_DATA"


def test_centrifuge_abort_spin():
    assert verify_storage_centrifuge([[3500, 2900, 2800]]) == "ABORT_SPIN"


def test_centrifuge_stable_with_streak_reset():
    assert verify_storage_centrifuge([[3500, 2900, 3200, 3100]]) == "STABLE"
