import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

function webStorageAvailable() {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

export async function getStoredValue(key: string): Promise<string | null> {
  if (Platform.OS === 'web') {
    if (!webStorageAvailable()) return null;
    return window.localStorage.getItem(key);
  }
  try {
    return await SecureStore.getItemAsync(key);
  } catch {
    return null;
  }
}

export async function setStoredValue(key: string, value: string): Promise<void> {
  if (Platform.OS === 'web') {
    if (!webStorageAvailable()) return;
    window.localStorage.setItem(key, value);
    return;
  }
  await SecureStore.setItemAsync(key, value);
}

export async function deleteStoredValue(key: string): Promise<void> {
  if (Platform.OS === 'web') {
    if (!webStorageAvailable()) return;
    window.localStorage.removeItem(key);
    return;
  }
  try {
    await SecureStore.deleteItemAsync(key);
  } catch {
    // Some environments expose partial SecureStore APIs; ignore deletion failures.
  }
}
