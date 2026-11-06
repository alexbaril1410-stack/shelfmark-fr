import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  getStoredShowZeroSeeders,
  shouldShowZeroSeeders,
  storeShowZeroSeeders,
  ZERO_SEEDERS_PREFERENCE_KEY,
} from '../utils/zeroSeedersPreference';

const makeStorage = () => {
  const store = new Map<string, string>();
  return {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => store.set(key, value),
  };
};

describe('zeroSeedersPreference', () => {
  beforeEach(() => vi.stubGlobal('window', { localStorage: makeStorage() }));
  afterEach(() => vi.unstubAllGlobals());

  it('preserves the current behavior by showing zero-seeder results by default', () => {
    expect(getStoredShowZeroSeeders()).toBe(true);
    expect(shouldShowZeroSeeders(0, true)).toBe(true);
    expect(shouldShowZeroSeeders(null, false)).toBe(true);
  });

  it('can hide only results known to have zero seeders and persists the preference', () => {
    storeShowZeroSeeders(false);
    expect(window.localStorage.getItem(ZERO_SEEDERS_PREFERENCE_KEY)).toBe('false');
    expect(shouldShowZeroSeeders(0, false)).toBe(false);
    expect(shouldShowZeroSeeders(3, false)).toBe(true);
    expect(shouldShowZeroSeeders(undefined, false)).toBe(true);
  });
});

