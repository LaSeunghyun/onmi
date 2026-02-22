import { apiRequest } from '@/lib/api';

export type NotificationSetting = {
  daily_report_time_hhmm: string;
  is_enabled: boolean;
};

export async function getNotificationSetting(token: string) {
  return await apiRequest<NotificationSetting>('/settings/notification', { token });
}

export async function updateNotificationSetting(token: string, payload: NotificationSetting) {
  return await apiRequest<NotificationSetting>('/settings/notification', {
    token,
    method: 'PUT',
    body: payload,
  });
}

