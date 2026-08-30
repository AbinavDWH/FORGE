"""MOD-05: Schedule XML Parser — MS Project XML schedule reader."""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any
import shutil

SCHEDULE_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_schedule" / "nrl_crude_tank.xml"
BACKUP_PATH = SCHEDULE_PATH.with_suffix(".xml.backup")


def _ensure_backup():
    """Creates a baseline backup of the original schedule on first run."""
    if not BACKUP_PATH.exists() and SCHEDULE_PATH.exists():
        shutil.copy(SCHEDULE_PATH, BACKUP_PATH)


def _safe_int(val: Any, default: int = 0) -> int:
    """Safely parse integer from string, ignoring 'None', empty, or malformed strings."""
    if val is None:
        return default
    s = str(val).strip()
    if s.lower() in ("none", "null", ""):
        return default
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default


def parse_schedule() -> List[Dict[str, Any]]:
    """
    Parses the MS Project XML file into a list of task dictionaries.
    """
    _ensure_backup()
    
    raw_content = SCHEDULE_PATH.read_text(encoding="utf-8").lstrip()
    if raw_content.startswith('\ufeff'):
        raw_content = raw_content[1:]
        
    root = ET.fromstring(raw_content)
    
    ns = {'msp': 'http://schemas.microsoft.com/project'}
    tasks = []
    
    task_elements = root.findall('.//msp:Task', ns)
    if not task_elements:
        task_elements = root.findall('.//Task')
        
    for task_el in task_elements:
        def get_text(tag):
            el = task_el.find(f'msp:{tag}', ns)
            if el is None:
                el = task_el.find(tag)
            if el is not None and el.text:
                txt = el.text.strip()
                return None if txt.lower() in ("none", "null", "") else txt
            return None

        pct = _safe_int(get_text("PercentComplete"), 0)

        task = {
            "task_id": get_text("UID"),
            "wbs_code": get_text("WBS"),
            "task_name": get_text("Name"),
            "planned_start": get_text("Start"),
            "planned_finish": get_text("Finish"),
            "actual_start": get_text("ActualStart"),
            "actual_finish": get_text("ActualFinish"),
            "percent_complete": pct,
            "zone": get_text("Zone"),
            "discipline": get_text("Discipline"),
            "component": get_text("Component"),
            "predecessors": get_text("Predecessors"),
        }
        
        if task["component"]:
            task["component_aliases"] = [task["component"], task["component"].replace(" ", "")]
            
        if task["task_name"]:
            task["activity_keywords"] = task["task_name"].lower().split()
            
        if pct == 100:
            task["status"] = "Completed"
            task["is_active"] = False
        elif pct > 0:
            task["status"] = "In Progress"
            task["is_active"] = True
        else:
            task["status"] = "Not Started"
            task["is_active"] = False
            
        tasks.append(task)
        
    return tasks