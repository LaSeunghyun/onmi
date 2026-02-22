import { Stack } from 'expo-router';

export default function StockLayout() {
  return (
    <Stack>
      <Stack.Screen name="add" options={{ title: '종목 추가', headerBackTitle: '목록' }} />
      <Stack.Screen name="[corpCode]" options={{ title: '종목 상세', headerBackTitle: '목록' }} />
    </Stack>
  );
}
