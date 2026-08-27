# SportsSmartBot

Статический сайт клубной операционной системы SportsSmartBot. Сайт показывает
один растущий продукт с уровнями подписки «Базовая», «Стандартная» и
«Максимум».

## Локальная сборка

```bash
python3 scripts/build_site.py --check
python3 -m http.server 8000 --directory _site
```

Контент находится в `data/site.json`. Сборка проверяет структуру уровней,
внутренние ссылки, Telegram CTA, обязательные атрибуты изображений и наличие
всех production-ассетов. Push в `main` автоматически публикует `_site` через
GitHub Pages.

Исходные PNG из `site/assets/generated/` сохранены для будущей переработки,
но не попадают в итоговую сборку. Страница использует адаптивные AVIF/WebP
копии из `site/assets/media/`. Герб для интерфейса и favicon собран отдельно
как `site/assets/brand-crest.svg`.
