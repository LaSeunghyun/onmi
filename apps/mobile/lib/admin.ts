import { apiRequest } from '@/lib/api';

export type AdminTokenResponse = {
  access_token: string;
  token_type: string;
  must_change_password: boolean;
  role: string;
};

export type AdminMe = {
  id: string;
  admin_id: string;
  role: string;
  must_change_password: boolean;
  is_active: boolean;
};

export type AdminMember = {
  id: string;
  email: string;
  created_at: string;
  status: 'active' | 'suspended';
  points: number;
};

export type AdminModule = {
  id: string;
  module_key: string;
  name: string;
  route_path: string;
  description: string | null;
  is_active: boolean;
  updated_at: string;
};

export type AdminAuditLog = {
  id: string;
  admin_user_id: string;
  action_type: string;
  target_type: string;
  target_id: string | null;
  reason: string | null;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  created_at: string;
};

export async function adminLogin(adminId: string, password: string) {
  return apiRequest<AdminTokenResponse>('/admin/auth/login', {
    method: 'POST',
    body: { admin_id: adminId, password },
  });
}

export async function adminMe(token: string) {
  return apiRequest<AdminMe>('/admin/auth/me', { token });
}

export async function adminChangePassword(token: string, currentPassword: string, newPassword: string) {
  return apiRequest<{ status: string }>('/admin/auth/change-password', {
    method: 'POST',
    token,
    body: { current_password: currentPassword, new_password: newPassword },
  });
}

export async function adminListMembers(token: string, q?: string) {
  const path = q?.trim() ? `/admin/members?q=${encodeURIComponent(q.trim())}` : '/admin/members';
  return apiRequest<AdminMember[]>(path, { token });
}

export async function adminCreateMember(
  token: string,
  payload: { email: string; password: string; status: 'active' | 'suspended'; initial_points: number }
) {
  return apiRequest<{ id: string; email: string }>('/admin/members', {
    method: 'POST',
    token,
    body: payload,
  });
}

export async function adminUpdateMemberStatus(token: string, userId: string, status: 'active' | 'suspended', reason?: string) {
  return apiRequest<{ status: string; member_status: string }>(`/admin/members/${userId}/status`, {
    method: 'PATCH',
    token,
    body: { status, reason: reason ?? null },
  });
}

export async function adminListModules(token: string) {
  return apiRequest<AdminModule[]>('/admin/modules', { token });
}

export async function adminCreateModule(
  token: string,
  payload: { module_key: string; name: string; route_path: string; description?: string; is_active: boolean }
) {
  return apiRequest<{ id: string }>('/admin/modules', {
    method: 'POST',
    token,
    body: payload,
  });
}

export async function adminListAuditLogs(token: string) {
  return apiRequest<AdminAuditLog[]>('/admin/audit-logs', { token });
}
