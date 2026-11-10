# Language editions

Supported locales: en, fr, it, de, es, ru.

English source pages live in `templates/en/`. Editable translations live in `locales/<code>.json`. Preserve product names, addresses, store URLs and legal meaning when editing.

Build: `python3 scripts/build_languages.py`
Validate: `python3 scripts/check_languages.py`

The build emits static HTML for every section, reciprocal hreflang links, a language switcher, and local runtime dictionaries for interactive carousel, ASO and form text. No translation service is called by visitors. Language is kept by the page URL and internal links. English URLs stay compatible.

The initial translations used Google Translate with editorial corrections to product names, terminology and interface copy. This translation release preserves the existing English legal policy; it is not a new legal policy or a legal audit.

`scripts/localize.py` is an optional authoring helper for translating new public English strings through Google Translate. It caches results without replacing existing translations. Do not send private text through it.
