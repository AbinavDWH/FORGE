"""MOD-05: Schedule Write-Back — Actuals Writer."""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

SCHEDULE_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_schedule" / "nrl_crude_tank.xml"
NS = 'http://schemas.microsoft.com/project'

ET.register_namespace('', NS)


def write_actuals_to_xml(
    task_id: str, 
    percent_complete: Optional[int] = None, 
    actual_start: Optional[str] = None,
    actual_finish: Optional[str] = None
) -> bool:
    """
    Safely updates only actual execution progress fields in the XML schedule.
    Preserves planned baseline dates, float, and CPM dependencies.
    """
    raw_content = SCHEDULE_PATH.read_text(encoding="utf-8").lstrip()
    if raw_content.startswith('\ufeff'):
        raw_content = raw_content[1:]
        
    root = ET.fromstring(raw_content)
    ns = {'msp': NS}
    updated = False
    
    for task_el in root.findall('.//msp:Task', ns):
        uid_el = task_el.find('msp:UID', ns)
        if uid_el is None:
            uid_el = task_el.find('UID')
            
        if uid_el is not None and uid_el.text == str(task_id):
            if percent_complete is not None:
                pct_el = task_el.find('msp:PercentComplete', ns)
                if pct_el is None:
                    pct_el = task_el.find('PercentComplete')
                if pct_el is not None:
                    try:
                        pct_el.text = str(max(0, min(100, int(percent_complete))))
                    except (ValueError, TypeError):
                        pass
                    
            if actual_start is not None:
                as_el = task_el.find('msp:ActualStart', ns)
                if as_el is None:
                    as_el = task_el.find('ActualStart')
                if as_el is not None:
                    as_el.text = str(actual_start)
                    
            if actual_finish is not None:
                af_el = task_el.find('msp:ActualFinish', ns)
                if af_el is None:
                    af_el = task_el.find('ActualFinish')
                if af_el is not None:
                    af_el.text = str(actual_finish)
                    
            updated = True
            break
            
    if updated:
        tree = ET.ElementTree(root)
        tree.write(SCHEDULE_PATH, encoding="UTF-8", xml_declaration=False)
        return True
        
    return False