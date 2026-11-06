export type UiLanguage = 'en' | 'fr';

export const UI_LANGUAGE_STORAGE_KEY = 'shelfmark-ui-language';

const french: Record<string, string> = {
  'Search': 'Rechercher',
  'Settings': 'Paramètres',
  'Downloads': 'Téléchargements',
  'My Account': 'Mon compte',
  'Report a Bug': 'Signaler un bug',
  'Sign Out': 'Se déconnecter',
  'Go To Library': 'Aller à la bibliothèque',
  'Library': 'Bibliothèque',
  'Activity': 'Activité',
  'Debug': 'Débogage',
  'Restart': 'Redémarrer',
  'Download as': 'Télécharger en tant que',
  'Myself': 'Moi-même',
  'Loading users...': 'Chargement des utilisateurs…',
  'Loading user details...': 'Chargement du profil…',
  'Loading settings...': 'Chargement des paramètres…',
  'Loading account settings...': 'Chargement des paramètres du compte…',
  'Loading setup wizard...': 'Chargement de l’assistant de configuration…',
  'Unable to load account details.': 'Impossible de charger les informations du compte.',
  'No users yet.': 'Aucun utilisateur pour le moment.',
  'No results found.': 'Aucun résultat.',
  'No cover available': 'Aucune couverture disponible',
  'Apply': 'Appliquer',
  'Save': 'Enregistrer',
  'Cancel': 'Annuler',
  'Close': 'Fermer',
  'Retry': 'Réessayer',
  'Select an option': 'Choisir une option',
  'Select...': 'Choisir…',
  'Format': 'Format',
  'Language': 'Langue',
  'Indexers': 'Indexeurs',
  'Search Mode': 'Mode de recherche',
  'Search by': 'Rechercher par',
  'Search context': 'Contexte de recherche',
  'All Formats': 'Tous les formats',
  'All Indexers': 'Tous les indexeurs',
  'Filter releases': 'Filtrer les résultats',
  'Sort releases': 'Trier les résultats',
  'No releases found for this book.': 'Aucun résultat pour ce livre.',
  'Best Match (Default)': 'Meilleure correspondance (par défaut)',
  'Choose formats to download': 'Choisir les formats à télécharger',
  'No results found': 'Aucun résultat trouvé',
  'Search Results': 'Résultats de recherche',
  'Sort results': 'Trier les résultats',
  'Search books': 'Rechercher des livres',
  'Show more': 'Afficher plus',
  'Show less': 'Afficher moins',
  'View details': 'Voir les détails',
  'Book details': 'Détails du livre',
  'Book cover': 'Couverture du livre',
  'Download file': 'Télécharger le fichier',
  'Treat as a single book': 'Traiter comme un seul livre',
  'Series #': 'N° de série',
  'Search in library': 'Rechercher dans la bibliothèque',
  'Search results': 'Résultats de recherche',
  'Results': 'Résultats',
  'Page': 'Page',
  'Next': 'Suivant',
  'Previous': 'Précédent',
  'More': 'Plus',
  'Less': 'Moins',
  'Sort by': 'Trier par',
  'Title': 'Titre',
  'Author': 'Auteur',
  'Authors': 'Auteurs',
  'Narrator': 'Narrateur',
  'Description': 'Description',
  'ISBN': 'ISBN',
  'Series': 'Série',
  'Year': 'Année',
  'Publisher': 'Éditeur',
  'Files': 'Fichiers',
  'Source': 'Source',
  'Default': 'Par défaut',
  'Not supported': 'Non pris en charge',
  'Requested': 'Demandé',
  'User Preferences': 'Préférences utilisateur',
  'Theme': 'Thème',
  'Choose your preferred color scheme.': 'Choisissez votre thème de couleurs.',
  'Save Changes': 'Enregistrer les modifications',
  'Are you sure?': 'Confirmer ?',
  'Confirm': 'Confirmer',
  'Settings saved': 'Paramètres enregistrés',
  'Search Preferences': 'Préférences de recherche',
  'Enable Audible.fr': 'Activer Audible.fr',
  'Enable Audible.fr as a metadata provider for audiobook searches.': 'Autoriser Audible.fr comme fournisseur de métadonnées pour les recherches de livres audio.',
  "Audiobook metadata from Audible.fr's catalog search endpoint. This endpoint is undocumented and may change; only search requests are made, results are cached, and each item links back to Audible.fr. No Audible account is required.": 'Métadonnées de livres audio provenant du catalogue Audible.fr. Ce point d’accès n’est pas documenté et peut changer. Les recherches sont mises en cache et chaque résultat renvoie vers Audible.fr. Aucun compte Audible n’est nécessaire.',
  'Test Connection': 'Tester la connexion',
  'Audiobook metadata from Audible.fr catalog search. No Audible account is required.': 'Métadonnées de livres audio du catalogue Audible.fr. Aucun compte Audible n’est requis.',
  'Connected to the Audible.fr catalog': 'Connexion au catalogue Audible.fr réussie',
  'Audible.fr catalog API is not reachable': 'Le catalogue Audible.fr est inaccessible',
  'Audible.fr returned an unexpected catalog response': 'Audible.fr a renvoyé une réponse inattendue',
  'Show results with 0 seeders': 'Afficher les résultats avec 0 seeders',
  'Hide results with 0 seeders': 'Masquer les résultats sans seeders',
  'Searching…': 'Recherche…',
  'Search Settings': 'Préférences de recherche',
  'UI language': "Langue de l’interface",
  'Interface language': "Langue de l’interface",
  'Interface preferences': "Préférences de l’interface",
  'English': 'Anglais',
  'French': 'Français',
  'Select language': 'Choisir la langue',
  'No books found': 'Aucun livre trouvé',
  'Loading...': 'Chargement…',
  'Download': 'Télécharger',
  'Request': 'Demander',
  'Search books...': 'Rechercher des livres…',
  'All Languages': 'Toutes les langues',
  'All sources': 'Toutes les sources',
  'All': 'Tout',
  'Ebook': 'Livre numérique',
  'Audiobook': 'Livre audio',
  'On': 'Activé',
  'Off': 'Désactivé',
  'Account updated': 'Compte mis à jour',
  'Passwords do not match': 'Les mots de passe ne correspondent pas',
  'Current password is required': 'Le mot de passe actuel est requis',
  'Password is required': 'Le mot de passe est requis',
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
