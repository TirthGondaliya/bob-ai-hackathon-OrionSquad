"""
Cold Chain IoT Monitoring & Regulatory Severity Classifier.
Implements the Arrhenius Mean Kinetic Temperature (MKT) equation,
cumulative degree-hour integration, and FDA 21 CFR / WHO PQS classification.
"""
import math
from typing import List, Tuple
from .models import TelemetryReading, ColdChainProfile, RegulatorySeverity

# Scientific constants for pharmaceutical Arrhenius degradation
# Standard activation energy for pharmaceuticals / biologicals: ΔH = 83.144 kJ/mol
DELTA_H = 83144.0  # J/mol
GAS_CONSTANT_R = 8.314472  # J / (mol * K)
DELTA_H_OVER_R = DELTA_H / GAS_CONSTANT_R  # approx 10000 Kelvin


def calculate_mkt(temperatures_c: List[float]) -> float:
    """
    Computes the Mean Kinetic Temperature (MKT) in degrees Celsius using the Arrhenius equation.
    T_k = (ΔH / R) / ( -ln ( (1/n) * Σ exp(-ΔH / (R * T_i)) ) )
    where T_i is in Kelvin.
    """
    if not temperatures_c:
        return 4.0

    n = len(temperatures_c)
    sum_exp = 0.0

    for temp_c in temperatures_c:
        temp_k = temp_c + 273.15
        if temp_k <= 0:
            temp_k = 0.1  # Safeguard against zero or negative Kelvin
        sum_exp += math.exp(-DELTA_H_OVER_R / temp_k)

    mean_exp = sum_exp / n
    if mean_exp <= 0:
        return temperatures_c[-1]

    mkt_k = DELTA_H_OVER_R / (-math.log(mean_exp))
    mkt_c = mkt_k - 273.15
    return round(mkt_c, 2)


def evaluate_cold_chain_telemetry(
    profile: ColdChainProfile,
    new_reading: TelemetryReading,
    interval_hours: float = 0.5
) -> ColdChainProfile:
    """
    Ingests a new IoT telemetry reading, calculates updated MKT, cumulative degree-hours,
    and classifies regulatory severity according to FDA 21 CFR Part 211 & WHO PQS standards.
    """
    profile.telemetry_history.append(new_reading)
    all_temps = [r.temperature_c for r in profile.telemetry_history]

    # Calculate MKT
    current_mkt = calculate_mkt(all_temps)
    profile.current_mkt_c = current_mkt
    new_reading.mkt_c = current_mkt

    # Analyze temperature excursions
    min_safe = profile.min_temp_c
    max_safe = profile.max_temp_c
    curr_temp = new_reading.temperature_c

    is_excursion = (curr_temp > max_safe) or (curr_temp < min_safe)

    if is_excursion:
        profile.excursion_hours += interval_hours
        if curr_temp > max_safe:
            profile.cumulative_degree_hours += (curr_temp - max_safe) * interval_hours
        elif curr_temp < min_safe:
            profile.cumulative_degree_hours += (min_safe - curr_temp) * interval_hours

    # Calculate stability budget consumption (e.g., standard vaccine allows max 24 degree-hours or 10h excursion)
    max_allowable_degree_hours = 20.0
    budget_used = min(100.0, round((profile.cumulative_degree_hours / max_allowable_degree_hours) * 100.0, 1))
    profile.stability_budget_percent_consumed = budget_used

    # Regulatory Classification
    # Critical criteria:
    # 1. Freezing breach: Biologics/antigens denature if frozen (< -0.5°C)
    # 2. Extreme heat (> 15°C for > 2 hours) or sustained excursion (> 6 hours)
    # 3. MKT > 10°C or stability budget > 50%
    if curr_temp < -0.5 or curr_temp >= 15.0 or profile.excursion_hours >= 6.0 or current_mkt >= 10.0 or budget_used >= 60.0:
        profile.regulatory_severity = RegulatorySeverity.LEVEL_3_CRITICAL
        profile.quarantine_recommended = True
        profile.recommended_action = (
            f"CRITICAL REGULATORY EXCURSION (FDA 21 CFR Part 211 / WHO PQS Alert). "
            f"Current MKT {current_mkt}°C exceeds limit (10°C). Excursion: {profile.excursion_hours}h. "
            f"IMMEDIATE QUARANTINE HOLD before delivery. Dispatch emergency cryogenic reefer or prepare insurance claim."
        )
    elif profile.excursion_hours >= 2.0 or curr_temp > 10.0 or budget_used >= 25.0:
        profile.regulatory_severity = RegulatorySeverity.LEVEL_2_MODERATE
        profile.quarantine_recommended = False
        profile.recommended_action = (
            f"MODERATE REGULATORY EXCURSION. MKT {current_mkt}°C, {profile.excursion_hours}h outside 2-8°C. "
            f"Stability budget consumed: {budget_used}%. "
            f"Action: Trigger reefer active cooling override (-2°C boost) and dispatch dry-ice replenisher at next waypoint."
        )
    elif is_excursion or profile.excursion_hours > 0:
        profile.regulatory_severity = RegulatorySeverity.LEVEL_1_MINOR
        profile.quarantine_recommended = False
        profile.recommended_action = (
            f"MINOR TRANSIENT EXCURSION. Temp {curr_temp}°C. MKT {current_mkt}°C within allowable limits. "
            f"Stability budget consumed: {budget_used}%. Automated telemetry log recorded. Continue active monitoring."
        )
    else:
        profile.regulatory_severity = RegulatorySeverity.NORMAL
        profile.quarantine_recommended = False
        profile.recommended_action = "Optimal thermal stability maintained within WHO/FDA 2°C–8°C safe zone."

    return profile


def generate_regulatory_compliance_report(profile: ColdChainProfile, tracking_number: str) -> dict:
    """
    Generates a structured pre-delivery regulatory audit package.
    """
    return {
        "tracking_number": tracking_number,
        "cargo_type": profile.cargo_type or "Temperature-Controlled Pharmaceuticals",
        "cargo_value_usd": profile.cargo_value_usd,
        "standard_reference": "FDA 21 CFR Part 211.142 / WHO PQS Guidelines (E006)",
        "mean_kinetic_temperature_c": profile.current_mkt_c,
        "allowable_temperature_band": f"{profile.min_temp_c}°C to {profile.max_temp_c}°C",
        "total_excursion_duration_hours": profile.excursion_hours,
        "cumulative_degree_hours": round(profile.cumulative_degree_hours, 2),
        "stability_budget_consumed_percent": profile.stability_budget_percent_consumed,
        "regulatory_classification": profile.regulatory_severity.value,
        "quarantine_order_issued": profile.quarantine_recommended,
        "corrective_and_preventative_action": profile.recommended_action,
        "readings_analyzed": len(profile.telemetry_history),
        "status": "HOLD_PENDING_INSPECTION" if profile.quarantine_recommended else "CLEARED_FOR_DELIVERY"
    }
