export const ZERO_SEEDERS_PREFERENCE_KEY = 'shelfmark-show-zero-seeders';

export function shouldShowZeroSeeders(value: number | null | undefined, showZeroSeeders: boolean): boolean {
  return showZeroSeeders || value !== 0;
}

export function getStoredShowZeroSeeders(): boolean {
  try {
    return window.localStorage.getItem(ZERO_SEEDERS_PREFERENCE_KEY) !== 'false';
  } catch {
    return true;
  }
}

export function storeShowZeroSeeders(value: boolean): void {
  try {
    window.localStorage.setItem(ZERO_SEEDERS_PREFERENCE_KEY, String(value));
  } catch {
    // Best effort only; the setting remains active for the current session.
  }
}

