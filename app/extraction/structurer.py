"""MOD-02: Multi-Lingual Extraction Structurer.

Converts informal, slang, and multi-lingual field text into structured project fields.
Supports: English, Tamil/Tanglish, Hindi/Hinglish, Assamese, and Bengali site slang.
Rule: Never invents missing fields - unknown values stay None.
"""
import re
from typing import Dict, Any, Optional

# Multi-lingual action mapping patterns
ACTION_PATTERNS = [
    # Concrete Pouring
    (
        r"(?:concrete\s*pour|concrete\s*dhalai|dhalai|dhalayi|dhalai\s*kaam|pouring|pour|poured|rcc\s*pour|concrete\s*ooth|oothiyaachu|oothiyachu|pottingaachu|கான்கிரீட்|ஊத்தியாச்சு)",
        "Concrete pouring",
        "Civil",
    ),
    # Shuttering Removal
    (
        r"(?:shuttering\s*remov|shuttering\s*khol|shuttering\s*khula|shuttering\s*strip|de-shutter|deshuttering|formwork\s*remov|shuttering\s*kalatt|shuttering\s*pirich|shuttering\s*eduth|ஷட்டரிங்)",
        "Shuttering removal",
        "Civil",
    ),
    # Rebar Inspection
    (
        r"(?:rebar\s*insp|rebar\s*check|rebar\s*jaanch|sariya\s*check|sariya\s*jaanch|reinforcement\s*insp|rebar\s*porikkha|sariya|kambi\s*check|kambi\s*katt|kambi\s*jaanch|கம்பி)",
        "Rebar inspection",
        "Civil",
    ),
    # Excavation
    (
        r"(?:excavat|khudai|mati\s*kata|earthwork|trenching|digging|kuzhi\s*thond|pallam\s*thond|man\s*vett|குழி)",
        "Site Excavation",
        "Civil",
    ),
    # PCC Foundation
    (
        r"(?:pcc\s*bed|pcc\s*layer|pcc\s*laying|pcc\s*kaam|pcc|pcc\s*pottaachu)",
        "PCC Foundation Bed",
        "Civil",
    ),
    # Hydro Testing
    (
        r"(?:hydro\s*test|hydrotest|water\s*pressure\s*test|paani\s*testing|hydrostatic\s*test|thanni\s*test|ஹைட்ரோ)",
        "Hydro testing",
        "Piping",
    ),
    # Pipe Spool Erection / Fabrication
    (
        r"(?:spool\s*erect|spool\s*fab|pipe\s*erect|piping\s*fit|pipe\s*spool|pipe\s*jodayi|pipeline|pipe\s*joth)",
        "Pipe Spool Erection",
        "Piping",
    ),
    # Field Welding
    (
        r"(?:welding\s*insp|weld\s*check|field\s*weld|ndt\s*check|radiography|welding)",
        "Field Welding & Inspection",
        "Piping",
    ),
    # Insulation
    (
        r"(?:thermal\s*insul|insulation|lagging|cladding|heat\s*insulation)",
        "Thermal Insulation",
        "Insulation",
    ),
    # Cable Tray
    (
        r"(?:cable\s*tray|tray\s*install|tray\s*fitting|tray\s*lagana|tray\s*pottaachu)",
        "Cable Tray Installation",
        "Electrical",
    ),
    # Cable Pulling
    (
        r"(?:cable\s*pull|cable\s*khichai|wire\s*pull|cable\s*laying|taar\s*khichna|cable\s*izhut|wire\s*izhut|கேபிள்)",
        "Cable Pulling",
        "Electrical",
    ),
    # Control Loop Testing
    (
        r"(?:loop\s*test|loop\s*check|transmitter\s*install|sensor\s*check|instrument\s*test)",
        "Loop Testing",
        "Instrumentation",
    ),
    # Tank Base / Shell
    (
        r"(?:base\s*plate|shell\s*plate|tank\s*shell|floating\s*roof|tank\s*erect)",
        "Tank Erection",
        "Structural",
    ),
]

# Multi-lingual completion / status patterns
COMPLETED_TERMS = [
    # English
    "completed", "complete", "done", "finished", "cleared", "passed", "ok", "ready",
    # Tamil / Tanglish
    "mudinjadhu", "mudinjachu", "mudinjudhu", "aayidichu", "pottaachu", "oothiyaachu",
    "oothiyachu", "kalattiyaachu", "eduthachu", "pirichaachu", "izhuthaachu", "thondiyaachu",
    "mudithathu", "முடிந்தது", "முடிஞ்சது", "ஆயிடுச்சு", "ஊத்தியாச்சு",
    # Hindi / Hinglish
    "ho gaya", "ho chuka", "ho gyi", "khatam", "pura hua", "pura ho gaya", "mukammal",
    "khol diya", "pass ho gaya", "niptaya",
    # Assamese
    "sompurno hol", "sompurno", "sesh hol", "xekh hol", "hoise", "hoise aji",
    # Bengali
    "shesh hol", "shesh hoyeche", "somponno", "complete hoyeche",
]

IN_PROGRESS_TERMS = [
    # English
    "in progress", "ongoing", "started", "half done", "in-progress",
    # Tamil / Tanglish
    "nadandhuttu irukku", "nadakudhu", "vela pogudhu", "poyittu irukku", "paadhi aachu",
    "nadanthu", "நடந்துட்டு இருக்கு", "வேலை போகுது",
    # Hindi / Hinglish
    "chal raha hai", "chalu hai", "chal rha", "jari hai", "aadha hua", "half ho gaya",
    # Assamese
    "choli ase", "arombho hoise", "soli ase",
    # Bengali
    "cholche", "kaj cholche",
]


def detect_language(text: str) -> str:
    """Detects primary language or dialect in the update text."""
    lower = text.lower()
    # Tamil script range (\u0B80-\u0BFF) or Tanglish keywords
    if re.search(r"[\u0B80-\u0BFF]", text) or any(
        w in lower for w in [
            "mudinjadhu", "mudinjachu", "mudinjudhu", "oothiyachu", "oothiyaachu",
            "kambi", "vela", "aayidichu", "nadakudhu", "irukku", "thondiyachu",
            "pirichaachu", "kalattiyaachu", "pottaachu"
        ]
    ):
        return "Tamil / Tanglish"
    elif any(w in lower for w in ["hol", "choli ase", "sompurno", "xekh", "hoise", "soli ase", "aji"]):
        return "Assamese"
    elif any(w in lower for w in ["hoyeche", "cholche", "shesh", "somponno", "kaj"]):
        return "Bengali"
    elif any(w in lower for w in ["ho gaya", "chal raha", "chalu", "khatam", "sariya", "dhalai", "jaanch", "khudai", "kaam"]):
        return "Hinglish / Hindi"
    return "English"


def structure_text(raw_text: str) -> Dict[str, Any]:
    """
    Converts informal, multi-lingual field text into standardized project attributes.
    Supports English, Tamil/Tanglish, Hindi/Hinglish, Assamese, and Bengali vocabulary.
    """
    text = (raw_text or "").lower()

    spatial_zone = None
    discipline = None
    component = None
    action = None
    status = None
    percent_complete = None

    # 1. Spatial Zone Detection
    zone_match = re.search(r"(?:zone|sector|area|zila|vibhag|bhag|pagudhi|mandalam)\s*([a-z0-9]+)", text)
    if zone_match:
        spatial_zone = f"Zone {zone_match.group(1).upper()}"
    elif "tank farm" in text or "tank area" in text:
        spatial_zone = "Tank Farm"
    elif "pipeline" in text or "corridor" in text:
        spatial_zone = "Pipeline Corridor"
    elif "pump house" in text or "pumphouse" in text:
        spatial_zone = "Pump House"

    # 2. Component Detection
    pier_match = re.search(r"(?:pier|peer|pir|khamba|pillar|thoon)\s*(\d+)", text)
    if pier_match:
        component = f"Pier {pier_match.group(1)}"
        discipline = "Civil"
    elif "tank base" in text or "base plate" in text:
        component = "Tank Base Plate"
        discipline = discipline or "Structural"
    elif "shell" in text or "tank shell" in text:
        component = "Tank Shell"
        discipline = discipline or "Structural"
    elif "floating roof" in text or "roof" in text:
        component = "Floating Roof"
        discipline = discipline or "Structural"
    elif "line 1" in text or "spool 1" in text:
        component = "Line 1 Spool"
        discipline = discipline or "Piping"
    elif "line 2" in text or "line 2" in text:
        component = "Line 2"
        discipline = discipline or "Piping"
    elif "cable tray" in text:
        component = "Cable Tray"
        discipline = discipline or "Electrical"
    elif "feed cable" in text or "main cable" in text or "taar" in text or "wire" in text:
        component = "Main Feed Cable"
        discipline = discipline or "Electrical"
    elif "pressure transmitter" in text or "transmitter" in text or "sensor" in text:
        component = "Pressure Transmitter"
        discipline = discipline or "Instrumentation"
    elif "loop" in text:
        component = "Control Loop"
        discipline = discipline or "Instrumentation"

    # 3. Multi-Lingual Action & Discipline Matching
    for pattern, act_name, disc_name in ACTION_PATTERNS:
        if re.search(pattern, text):
            action = act_name
            discipline = discipline or disc_name
            break

    # 4. Status & Progress Percentage (Multi-Lingual)
    if any(term in text for term in COMPLETED_TERMS):
        status = "Completed"
        percent_complete = 100
    elif any(term in text for term in IN_PROGRESS_TERMS):
        status = "In Progress"
        percent_complete = 50
    else:
        # Numeric percentage pattern: e.g. "80%", "80 percent", "80 prathishat", "80 satham"
        percent_match = re.search(r"(\d{1,3})\s*(?:%|percent|pratishat|shotangsho|satham|satavigitham|pct)", text)
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