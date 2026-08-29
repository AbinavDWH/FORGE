# Replace: app/schedule/cpm_guard.py
from typing import Dict, Any, List

def check_cpm_dependencies(
    task_id: str, 
    proposed_percent: int, 
    schedule_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validates CPM logic. 
    Rule: A task cannot progress if its Finish-to-Start predecessors are not 100% complete.
    """
    target_task = next((t for t in schedule_data if t["task_id"] == task_id), None)
    if not target_task:
        return {"valid": False, "reason": "Task not found in schedule."}
        
    predecessors_str = target_task.get("predecessors")
    if not predecessors_str:
        return {"valid": True, "reason": "No predecessors. Logic holds."}
        
    pred_ids = [p.strip() for p in predecessors_str.split(",")]
    
    for pred_id in pred_ids:
        pred_task = next((t for t in schedule_data if t["task_id"] == pred_id), None)
        if pred_task:
            # If predecessor is not 100% complete, and we are trying to progress this task
            if pred_task["percent_complete"] < 100 and proposed_percent > 0:
                return {
                    "valid": False,
                    "reason": (
                        f"Dependency Violation: Predecessor '{pred_task['task_name']}' "
                        f"({pred_task['wbs_code']}) is only {pred_task['percent_complete']}% complete. "
                        f"Cannot start/progress '{target_task['task_name']}'."
                    )
                }
                
    return {"valid": True, "reason": "All predecessors are 100% complete. Logic holds."}