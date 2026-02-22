import * as Notifications from 'expo-notifications';
import * as SecureStore from 'expo-secure-store';

const NOTIF_ID_KEY = 'touch.dailyReportNotificationId';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldShowBanner: true,
    shouldShowList: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

export async function ensureNotificationPermission() {
  const current = await Notifications.getPermissionsAsync();
  if (current.granted) return true;
  const next = await Notifications.requestPermissionsAsync();
  return next.granted;
}

export async function cancelDailyReportNotification() {
  const id = await SecureStore.getItemAsync(NOTIF_ID_KEY);
  if (id) {
    await Notifications.cancelScheduledNotificationAsync(id);
    await SecureStore.deleteItemAsync(NOTIF_ID_KEY);
  }
}

export async function scheduleDailyReportNotification(opts: { hour: number; minute: number }) {
  await cancelDailyReportNotification();
  const id = await Notifications.scheduleNotificationAsync({
    content: {
      title: '오늘의 리포트',
      body: '오늘의 키워드 이슈를 확인해보세요.',
      data: { type: 'daily_report' },
    },
    trigger: {
      type: Notifications.SchedulableTriggerInputTypes.CALENDAR,
      hour: opts.hour,
      minute: opts.minute,
      repeats: true,
    },
  });
  await SecureStore.setItemAsync(NOTIF_ID_KEY, id);
  return id;
}

