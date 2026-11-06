export type UiLanguage = 'en' | 'fr';

export const UI_LANGUAGE_STORAGE_KEY = 'shelfmark-ui-language';

const french: Record<string, string> = {
  'Search': 'Rechercher',
  'Settings': 'Paramètres',
  'Downloads': 'Téléchargements',
  'Report a Bug': 'Signaler un bug',
  'Sign Out': 'Se déconnecter',
  'Download as': 'Télécharger en tant que',
  'Myself': 'Moi-même',
  'Loading users...': 'Chargement des utilisateurs…',
  'Apply': 'Appliquer',
  'Format': 'Format',
  'Language': 'Langue',
  'Indexers': 'Indexeurs',
  'All Formats': 'Tous les formats',
  'All Indexers': 'Tous les indexeurs',
  'Filter releases': 'Filtrer les résultats',
  'Sort releases': 'Trier les résultats',
  'No releases found for this book.': 'Aucun résultat pour ce livre.',
  'Searching…': 'Recherche…',
  'Search Settings': 'Préférences de recherche',
  'Show results with 0 seeders': 'Afficher les résultats avec 0 seeder',
  'Hide results with 0 seeders': 'Masquer les résultats avec 0 seeder',
  'UI language': "Langue de l’interface",
  'English': 'Anglais',
  'French': 'Français',
  'Select language': 'Choisir la langue',
  'No books found': 'Aucun livre trouvé',
  'Loading...': 'Chargement…',
  'Cancel': 'Annuler',
  'Save': 'Enregistrer',
  'Close': 'Fermer',
  'Download': 'Télécharger',
  'Request': 'Demander',
  'Search books...': 'Rechercher des livres…',
  'All Languages': 'Toutes les langues',
  'All sources': 'Toutes les sources',
  'Search Results': 'Résultats de recherche',
};

const reverseFrench = new Map(Object.entries(french).map(([english, translated]) => [translated, english]));
let activeLanguage: UiLanguage = 'en';

export function normalizeUiLanguage(value: unknown): UiLanguage {
  return value === 'fr' ? 'fr' : 'en';
}

export function translateUiText(value: string, language: UiLanguage): string {
  const english = reverseFrench.get(value) ?? value;
  return language === 'fr' ? french[english] ?? english : english;
}

export function getStoredUiLanguage(): UiLanguage {
  try {
    return normalizeUiLanguage(window.localStorage.getItem(UI_LANGUAGE_STORAGE_KEY));
  } catch {
    return 'en';
  }
}

export function setUiLanguage(language: UiLanguage): void {
  activeLanguage = language;
  try {
    window.localStorage.setItem(UI_LANGUAGE_STORAGE_KEY, language);
  } catch {
    // Language remains active for this page even when storage is unavailable.
  }
  document.documentElement.lang = language;
  document.documentElement.dataset.uiLanguage = language;
  translateDocument(language);
}

function translateDocument(language: UiLanguage): void {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node = walker.nextNode();
  while (node) {
    const value = node.nodeValue;
    if (value?.trim()) {
      const leading = value.match(/^\s*/)?.[0] ?? '';
      const trailing = value.match(/\s*$/)?.[0] ?? '';
      const content = value.slice(leading.length, value.length - trailing.length);
      const translated = `${leading}${translateUiText(content, language)}${trailing}`;
      if (translated !== value) node.nodeValue = translated;
    }
    node = walker.nextNode();
  }

  document.querySelectorAll<HTMLElement>('[placeholder], [aria-label], [title]').forEach((element) => {
    for (const attribute of ['placeholder', 'aria-label', 'title'] as const) {
      const value = element.getAttribute(attribute);
      if (value) element.setAttribute(attribute, translateUiText(value, language));
    }
  });
}

export function initializeUiLanguage(): void {
  activeLanguage = getStoredUiLanguage();
  document.documentElement.lang = activeLanguage;
  document.documentElement.dataset.uiLanguage = activeLanguage;
  const observer = new MutationObserver(() => translateDocument(activeLanguage));
  observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  translateDocument(activeLanguage);
}

