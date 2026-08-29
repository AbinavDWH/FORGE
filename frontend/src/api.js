const API_BASE = 'http://127.0.0.1:8000';

const handleResponse = async (res) => {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'API request failed');
  }
  return res.json();
};

export const api = {
  // Schedule
  getTasks: () => fetch(`${API_BASE}/api/schedule/tasks`).then(handleResponse),
  
  // Review Tray
  getReviewTray: () => fetch(`${API_BASE}/api/review/tray`).then(handleResponse),
  approveUpdate: (id, approvedBy = 'Manager') => 
    fetch(`${API_BASE}/api/review/${id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved_by: approvedBy })
    }).then(handleResponse),
  rejectUpdate: (id, approvedBy = 'Manager') => 
    fetch(`${API_BASE}/api/review/${id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved_by: approvedBy })
    }).then(handleResponse),

  // Audit
  getAuditLogs: () => fetch(`${API_BASE}/api/audit/logs`).then(handleResponse),
};