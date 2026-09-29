"""Transparent fictional presets; never passed off as district estimates."""
from .model import Assumption, Scenario

R = "Illustrative training input only, not calibrated to a district or policy."


def a(low, mode, high, unit):
    return Assumption(low, mode, high, unit, R)


def training_scenario() -> Scenario:
    return Scenario(
        eligible=a(8_000, 10_000, 12_000, "people"),
        need_rate=a(.12, .20, .30, "rate"),
        awareness_rate=a(.25, .40, .55, "rate"),
        screening_rate=a(.30, .50, .70, "rate"),
        followup_rate=a(.35, .60, .80, "rate"),
        capacity=a(300, 500, 750, "people"),
        spend_inr=a(100_000, 150_000, 220_000, "INR"),
    )


def training_outreach() -> Scenario:
    base = training_scenario()
    return Scenario(base.eligible, base.need_rate,
                    a(.35, .55, .75, "rate"),
                    a(.40, .65, .80, "rate"), base.followup_rate,
                    base.capacity, a(170_000, 250_000, 350_000, "INR"))


def training_capacity() -> Scenario:
    base = training_scenario()
    return Scenario(base.eligible, base.need_rate, base.awareness_rate,
                    base.screening_rate, base.followup_rate,
                    a(450, 700, 900, "people"),
                    a(200_000, 300_000, 420_000, "INR"))


PRESETS = {"status-quo": training_scenario, "outreach": training_outreach,
           "capacity": training_capacity}
