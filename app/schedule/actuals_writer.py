# Replace: app/schedule/actuals_writer.py
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

SCHEDULE_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_schedule" / "nrl_crude_tank.xml"

def write_actuals_to_xml(
    task_id: str, 
    percent_complete: int, 
    actual_start: Optional[str] = None,
    actual_finish: Optional[str] = None
) -> bool:
    """
    Safely updates only the actual progress fields in the XML file.
    Preserves baseline dates and dependencies.
    """
    tree = ET.parse(SCHEDULE_PATH)
    root = tree.getroot()
    
    ns = {'msp': 'http://schemas.microsoft.com/project'}
    task_elements = root.findall('.//msp:Task', ns)
    if not task_elements:
        task_elements = root.findall('.//Task')
        
    updated = False
    
    for task_el in task_elements:
        uid_el = task_el.find('msp:UID', ns) or task_el.find('UID')
        if uid_el is not None and uid_el.text == task_id:
            # Update Percent Complete
            pct_el = task_el.find('msp:PercentComplete', ns) or task_el.find('PercentComplete')
            if pct_el is not None:
                pct_el.text = str(percent_complete)
                
            # Update Actual Start
            if actual_start:
                as_el = task_el.find('msp:ActualStart', ns) or task_el.find('ActualStart')
                if as_el is not None:
                    as_el.text = actual_start
                    
            # Update Actual Finish
            if actual_finish:
                af_el = task_el.find('msp:ActualFinish', ns) or task_el.find('ActualFinish')
                if af_el is not None:
                    af_el.text = actual_finish
                    
            updated = True
            break
            
    if updated:
        # Write back to file with XML declaration
        tree.write(SCHEDULE_PATH, encoding="UTF-8", xml_declaration=True)
        return True
        
    return False