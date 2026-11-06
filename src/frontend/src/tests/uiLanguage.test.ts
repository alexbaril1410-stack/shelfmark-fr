import { describe, expect, it } from 'vitest';

import { normalizeUiLanguage, translateUiText } from '../utils/uiLanguage';

describe('uiLanguage', () => {
  it('defaults unknown language values to English', () => {
    expect(normalizeUiLanguage('fr')).toBe('fr');
    expect(normalizeUiLanguage('de')).toBe('en');
    expect(normalizeUiLanguage(null)).toBe('en');
  });

  it('translates known interface labels and leaves unknown text readable', () => {
    expect(translateUiText('Settings', 'fr')).toBe('Paramètres');
    expect(translateUiText('Search books...', 'fr')).toBe('Rechercher des livres…');
    expect(translateUiText('No results found.', 'fr')).toBe('Aucun résultat.');
    expect(translateUiText('Show results with 0 seeders', 'fr')).toBe(
      'Afficher les résultats avec 0 seeders',
    );
    expect(translateUiText('Paramètres', 'en')).toBe('Settings');
    expect(translateUiText('Untranslated text', 'fr')).toBe('Untranslated text');
  });
});
