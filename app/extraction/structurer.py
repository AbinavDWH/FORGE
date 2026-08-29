import re


def structure_text(raw_text: str) -> dict:
    """
    Convert informal field text into structured project fields.
    Never invents missing fields - unknown values stay None.
    """
    text = (raw_text or "").lower()

    spatial_zone = None
    discipline = None
    component = None
    action = None
    status = None
    percent_complete = None

    zone_match = re.search(r"(?:zone|sector)\s*([a-z0-9]+)", text)
    if zone_match:
        spatial_zone = f"Zone {zone_match.group(1).upper()}"

    pier_match = re.search(r"pier\s*(\d+)", text)
    if pier_match:
        component = f"Pier {pier_match.group(1)}"
        discipline = "Civil"

    if "concrete" in text:
        action = "Concrete pouring"
        discipline = discipline or "Civil"
    elif "shuttering" in text:
        action = "Shuttering removal"
        discipline = discipline or "Civil"
    elif "rebar" in text:
        action = "Rebar inspection"
        discipline = discipline or "Civil"
    elif "hydro" in text:
        action = "Hydro testing"
        discipline = discipline or "Piping"
    elif "insulation" in text:
        action = "Insulation"
        discipline = discipline or "Piping"

    if any(word in text for word in ["completed", "done", "complete", "finished"]):
        status = "Completed"
        percent_complete = 100
    else:
        percent_match = re.search(r"(\d{1,3})\s*%", text)
        if percent_match:
            percent_complete = min(100, int(percent_match.group(1)))
            status = "Completed" if percent_complete == 100 else "In Progress"
        elif action:
            status = "In Progress"

    return {
        "spatial_zone": spatial_zone,
        "discipline": discipline,
        "component": component,
        "action": action,
        "status": status,
        "percent_complete": percent_complete,
    }