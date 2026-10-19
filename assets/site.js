'use strict';
(() => {
  const root = document.documentElement;
  const read = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  const requested = new URLSearchParams(location.search).get('lang');
  let language = ['ar', 'en'].includes(requested) ? requested : read('mirsad.site.language') || 'ar';
  if (!['ar', 'en'].includes(language)) language = 'ar';
  root.dataset.theme = read('mirsad.site.theme') === 'light' ? 'light' : 'dark';
  root.dataset.enhanced = 'true';
  const languageButton = document.querySelector('[data-toggle-language]');
  const normalize = value => value.toLowerCase().normalize('NFKC').replace(/[\u064b-\u065f\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا');

  function filter(group) {
    const controls = document.querySelector(`[data-filter-controls="${group}"]`);
    if (!controls) return;
    const query = normalize(controls.querySelector('input[type="search"]').value.trim());
    const selections = [...controls.querySelectorAll('select')];
    const cards = [...document.querySelectorAll(`[data-filter-card="${group}"]`)];
    let visible = 0;
    for (const card of cards) {
      const selectedTool = selections.find(select => select.dataset.filterKey === 'tools')?.value;
      const selectedTime = selections.find(select => select.dataset.filterKey === 'temporal')?.value;
      const compatible = !selectedTool || !selectedTime || (card.dataset.capabilities || '').split(' ').includes(`${selectedTool}:${selectedTime}`);
      const match = compatible && normalize(card.textContent).includes(query) && selections.every(select => !select.value || (card.dataset[select.dataset.filterKey] || '').split(' ').includes(select.value));
      card.hidden = !match;
      if (match) visible++;
    }
    const status = document.querySelector(`[data-filter-status="${group}"]`);
    if (status) status.textContent = language === 'ar' ? `${visible} من ${cards.length} ${group === 'sources' ? 'مصدرًا / منتجًا' : 'عنصرًا مناخيًا'}` : `${visible} of ${cards.length} ${group === 'sources' ? 'sources / products' : 'climate modules'}`;
    const empty = document.querySelector(`[data-filter-empty="${group}"]`);
    if (empty) empty.hidden = visible !== 0;
  }
  function applyLanguage(updateURL = false) {
    root.lang = language;
    root.dir = language === 'ar' ? 'rtl' : 'ltr';
    if (languageButton) {
      languageButton.textContent = language === 'ar' ? 'English' : 'العربية';
      languageButton.lang = language === 'ar' ? 'en' : 'ar';
    }
    document.title = root.dataset[`title${language === 'ar' ? 'Ar' : 'En'}`] || document.title;
    document.querySelectorAll('[data-option-ar]').forEach(option => { option.textContent = option.dataset[language === 'ar' ? 'optionAr' : 'optionEn']; });
    document.querySelectorAll('[data-placeholder-ar]').forEach(input => { input.placeholder = input.dataset[language === 'ar' ? 'placeholderAr' : 'placeholderEn']; });
    document.querySelectorAll('[data-keep-language]').forEach(link => {
      const url = new URL(link.getAttribute('href'), location.href);
      url.searchParams.set('lang', language);
      link.href = url.href;
    });
    document.querySelectorAll('[data-filter-controls]').forEach(controls => filter(controls.dataset.filterControls));
    save('mirsad.site.language', language);
    if (updateURL) { const url = new URL(location.href); url.searchParams.set('lang', language); history.replaceState(null, '', url); }
  }
  if (languageButton) languageButton.addEventListener('click', () => { language = language === 'ar' ? 'en' : 'ar'; applyLanguage(true); });
  document.querySelector('[data-toggle-theme]')?.addEventListener('click', () => { root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark'; save('mirsad.site.theme', root.dataset.theme); });
  const menuButton = document.querySelector('[data-toggle-menu]');
  const menu = document.querySelector('.site-nav');
  function closeMenu() { menu?.removeAttribute('data-open'); menuButton?.setAttribute('aria-expanded', 'false'); }
  menuButton?.addEventListener('click', () => { const open = !menu.hasAttribute('data-open'); menu.toggleAttribute('data-open', open); menuButton.setAttribute('aria-expanded', String(open)); });
  menu?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });
  document.addEventListener('click', event => { if (!event.target.closest('.site-header')) closeMenu(); });
  document.querySelectorAll('[data-filter-controls]').forEach(controls => { controls.addEventListener('input', () => filter(controls.dataset.filterControls)); controls.addEventListener('change', () => filter(controls.dataset.filterControls)); });
  document.querySelectorAll('[data-clear-filter]').forEach(button => button.addEventListener('click', () => {
    const controls = document.querySelector(`[data-filter-controls="${button.dataset.clearFilter}"]`);
    controls.querySelectorAll('input,select').forEach(field => { field.value = ''; });
    filter(button.dataset.clearFilter); controls.querySelector('input').focus();
  }));
  document.querySelectorAll('.directory-nav a[href^="#"]').forEach(link => link.addEventListener('click', () => {
    const target = document.getElementById(link.hash.slice(1));
    if (!target?.matches('[data-filter-card="sources"]')) return;
    document.querySelectorAll('[data-filter-controls="sources"] input,[data-filter-controls="sources"] select').forEach(field => { field.value = ''; });
    filter('sources');
  }));
  applyLanguage();
})();
