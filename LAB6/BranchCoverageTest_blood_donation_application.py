"""Branch coverage tests for blood_donation_screening.py"""
import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


def make_cohort(donors, registered=True, ctype="standard", fast_track=False):
    return {"clinic_registered": registered, "type": ctype,
            "fast_track": fast_track, "donors": donors}


def donor(age=25, weight=65, hb=14.0):
    return {"age": age, "weight_kg": weight, "hb": hb}


# ---------- process_donor_cohort: input validation ----------
def test_single_accepted_donor():
    result = process_donor_cohort([make_cohort([donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_invalid_cohorts_not_list():
    with pytest.raises(ValueError):
        process_donor_cohort("not a list", 450)


@pytest.mark.parametrize("volume", [0, -100])
def test_invalid_volume(volume):
    with pytest.raises(ValueError):
        process_donor_cohort([make_cohort([donor()])], volume)


# ---------- registration branch ----------
def test_unregistered_cohort_skipped():
    result = process_donor_cohort([make_cohort([donor()], registered=False)], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_missing_registration_key_defaults_to_skipped():
    result = process_donor_cohort([{"donors": [donor()]}], 450)
    assert result["status"] == "ZERO_YIELD"


def test_missing_optional_keys_use_defaults():
    # no "type", "donors", "fast_track" -> defaults; empty loop
    result = process_donor_cohort([{"clinic_registered": True}], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_empty_cohort_list():
    assert process_donor_cohort([], 450) == {"collected_ml": 0, "status": "ZERO_YIELD"}


# ---------- age / weight branch (both operands of the OR) ----------
def test_underage_deferred():
    result = process_donor_cohort([make_cohort([donor(age=16), donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_underweight_deferred():
    result = process_donor_cohort([make_cohort([donor(weight=49), donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_boundary_age17_weight50_accepted():
    result = process_donor_cohort([make_cohort([donor(age=17, weight=50)])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_missing_donor_fields_deferred():
    result = process_donor_cohort([make_cohort([{}])], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


# ---------- hemoglobin branches ----------
def test_low_hb_standard_cohort_continues():
    cohorts = [make_cohort([donor(hb=12.4), donor()])]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_low_hb_high_altitude_resets_and_breaks():
    cohorts = [make_cohort([donor(), donor(hb=11.0), donor()], ctype="high_altitude")]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_altitude_normal_hb_accepted():
    result = process_donor_cohort([make_cohort([donor()], ctype="high_altitude")], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_high_hb_deferred():
    result = process_donor_cohort([make_cohort([donor(hb=18.1), donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


@pytest.mark.parametrize("hb", [12.5, 18.0])
def test_hb_boundaries_accepted(hb):
    result = process_donor_cohort([make_cohort([donor(hb=hb)])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


# ---------- fast-track branch ----------
def test_fast_track_adds_bonus():
    result = process_donor_cohort([make_cohort([donor()], fast_track=True)], 450)
    assert result == {"collected_ml": 500, "status": "ACCEPTED"}


def test_fast_track_after_high_altitude_break():
    cohorts = [make_cohort([donor(hb=10.0)], ctype="high_altitude", fast_track=True)]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 50, "status": "ACCEPTED"}


# ---------- final status branches ----------
def test_high_deferral_status():
    cohorts = [make_cohort([donor(age=10)] * 5 + [donor()])]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


def test_exactly_four_deferrals_not_high():
    cohorts = [make_cohort([donor(age=10)] * 4 + [donor()])]
    assert process_donor_cohort(cohorts, 450)["status"] == "ACCEPTED"


def test_zero_yield_status():
    result = process_donor_cohort([make_cohort([donor(age=10)])], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_multiple_cohorts_accumulate():
    cohorts = [make_cohort([donor()]), make_cohort([donor()], fast_track=True)]
    assert process_donor_cohort(cohorts, 300) == {"collected_ml": 650, "status": "ACCEPTED"}


# ---------- verify_storage_centrifuge ----------
def test_centrifuge_none_and_empty():
    assert verify_storage_centrifuge([]) == "NO_DATA"
    assert verify_storage_centrifuge(None) == "NO_DATA"


def test_centrifuge_abort_on_two_consecutive_drops():
    assert verify_storage_centrifuge([[3500, 2900, 2800]]) == "ABORT_SPIN"


def test_centrifuge_single_drop_then_recovery_stable():
    assert verify_storage_centrifuge([[3500, 2900, 3200, 2900, 3100]]) == "STABLE"


def test_centrifuge_abort_in_later_run():
    assert verify_storage_centrifuge([[3500, 3600], [2000, 2000]]) == "ABORT_SPIN"


def test_centrifuge_empty_run_stable():
    assert verify_storage_centrifuge([[]]) == "STABLE"


def test_centrifuge_streak_resets_between_runs():
    # one drop at end of run 1 and one at start of run 2 must NOT abort
    assert verify_storage_centrifuge([[3500, 2900], [2900, 3500]]) == "STABLE"
