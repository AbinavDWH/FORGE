# Replace: app/schedule/xml_parser.py
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

def parse_schedule() -> List[Dict[str, Any]]:
    """
    Parses the MS Project XML file into a list of task dictionaries.
    """
    _ensure_backup()
    
    # Read and clean the XML content to prevent "not at start of entity" errors
    # caused by leading blank lines, spaces, or BOM characters added by text editors.
    raw_content = SCHEDULE_PATH.read_text(encoding="utf-8")
    clean_content = raw_content.lstrip() # Removes leading whitespace/newlines
    
    # If it starts with a Byte Order Mark (BOM), remove it
    if clean_content.startswith('\ufeff'):
        clean_content = clean_content[1:]
        
    # Parse from the cleaned string instead of directly from the file
    root = ET.fromstring(clean_content)
    
    # Handle MS Project namespace
    ns = {'msp': 'http://schemas.microsoft.com/project'}
    tasks = []
    
    # Try with namespace first, then without (for simplified XMLs)
    task_elements = root.findall('.//msp:Task', ns)
    if not task_elements:
        task_elements = root.findall('.//Task')
        
    for task_el in task_elements:
        def get_text(tag):
            el = task_el.find(f'msp:{tag}', ns)
            if el is None:
                el = task_el.find(tag)
            return el.text.strip() if el is not None and el.text else None

        task = {
            "task_id": get_text("UID"),
            "wbs_code": get_text("WBS"),
            "task_name": get_text("Name"),
            "planned_start": get_text("Start"),
            "planned_finish": get_text("Finish"),
            "actual_start": get_text("ActualStart"),
            "actual_finish": get_text("ActualFinish"),
            "percent_complete": int(get_text("PercentComplete") or 0),
            "zone": get_text("Zone"),
            "discipline": get_text("Discipline"),
            "component": get_text("Component"),
            "predecessors": get_text("Predecessors"), # Comma separated UIDs
        }
        
        # Generate component aliases for the RapidFuzz matcher
        if task["component"]:
            task["component_aliases"] = [task["component"], task["component"].replace(" ", "")]
            
        # Generate activity keywords for the matcher
        if task["task_name"]:
            task["activity_keywords"] = task["task_name"].lower().split()
            
        # Determine status based on progress
        if task["percent_complete"] == 100:
            task["status"] = "Completed"
            task["is_active"] = False
        elif task["percent_complete"] > 0:
            task["status"] = "In Progress"
            task["is_active"] = True
        else:
            task["status"] = "Not Started"
            task["is_active"] = False
            
        tasks.append(task)
        
    return tasks