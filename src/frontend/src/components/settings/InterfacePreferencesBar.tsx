import { useState } from 'react';

import {
  getStoredUiLanguage,
  setUiLanguage,
  type UiLanguage,
} from '../../utils/uiLanguage';
import {
  getStoredShowZeroSeeders,
  storeShowZeroSeeders,
} from '../../utils/zeroSeedersPreference';

export const InterfacePreferencesBar = () => {
  const [language, setLanguage] = useState<UiLanguage>(getStoredUiLanguage);
  const [showZeroSeeders, setShowZeroSeeders] = useState(getStoredShowZeroSeeders);
  const isFrench = language === 'fr';

  return (
    <section
      aria-label={isFrench ? 'Préférences de l’interface' : 'Interface preferences'}
      className="flex shrink-0 flex-wrap items-center gap-x-6 gap-y-3 border-b border-(--border-muted) bg-(--bg-soft) px-5 py-3"
    >
      <label className="flex items-center gap-2 text-sm text-(--text)">
        <span>{isFrench ? 'Langue de l’interface' : 'Interface language'}</span>
        <select
          aria-label={isFrench ? 'Langue de l’interface' : 'Interface language'}
          value={language}
          onChange={(event) => {
            const next = event.target.value === 'fr' ? 'fr' : 'en';
            setLanguage(next);
            setUiLanguage(next);
          }}
          className="rounded-md border border-(--border-muted) bg-(--bg) px-2 py-1 text-(--text)"
        >
          <option value="en">English</option>
          <option value="fr">Français</option>
        </select>
      </label>

      <label className="flex items-center gap-2 text-sm text-(--text)">
        <input
          type="checkbox"
          checked={showZeroSeeders}
          onChange={(event) => {
            const next = event.target.checked;
            setShowZeroSeeders(next);
            storeShowZeroSeeders(next);
          }}
          className="h-4 w-4 rounded border-zinc-300 text-emerald-600 focus:ring-emerald-500"
        />
        <span>
          {isFrench ? 'Afficher les résultats avec 0 seeders' : 'Show results with 0 seeders'}
        </span>
      </label>
    </section>
  );
};
