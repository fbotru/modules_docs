# FBOT Modules

Публичный каталог модулей футбольного Telegram-бота FBOT.

## Локальная сборка

```bash
python3 scripts/build_site.py
python3 -m http.server 8000 --directory _site
```

Каталог находится в `data/modules.json`. Сборка проверяет уникальность ключей,
обязательные поля и наличие всех изображений. Push в `main` автоматически
публикует сайт через GitHub Pages.
