# SportsSmartBot website redesign brief

## Product position

SportsSmartBot is a Telegram-based club operating system for football,
basketball, volleyball and other team sports. It takes care of operational
routine, analytics and media workflows so clubs can focus on sport.

Primary message: **«Автоматизируем рутину. Оставляем спорт.»**

The previous four-module sales model is obsolete. The website must present one
growing product with three subscription levels. Do not call them modules and do
not preserve copy such as «начните с одного модуля» or «4 модуля».

## Subscription levels

### Базовая

- Опросы участников перед матчем.
- Заполнение игровых протоколов.
- Оценка судей.
- Минимальный SMM: таблицы дивизионов, анонс матча, результат игры,
  день матча, состав на игру, рассылка фотографий и ссылок на видео.
- Рассылка капитана участникам матча с суммой сбора.
- Награды.
- Минимальная статистика.

### Стандартная

- Всё из Базовой.
- Организация тренировок.
- Сбор и обработка чеков.
- Отчётность.
- Система мотивации.
- Расширенный SMM: бот автоматически создаёт видеоконтент, публикации об MVP
  и тексты, ведёт контентную логику на неделю и запускает дополнительные опросы.

### Максимум

- Всё из Стандартной.
- Дополнительный видеоконтент.
- Фирменные спортивные анимации.
- Дальнейшее развитие возможностей.

Present Maximum as a flexible premium roadmap with copy such as
«Новые возможности добавляются» / «To be continued». Do not invent features,
deadlines or prices.

## Brand and art direction

Use the generated SportsSmartBot crest concept: a heraldic shield, three blue
lanes and one gold S-shaped route with three nodes. Rebuild it as a clean,
scalable SVG instead of using the raster concept as the production logo. The
name is **SportsSmartBot**; `SSB` may be used as a compact abbreviation.

Visual direction is Modern Heritage:

- deep azzurro and midnight navy;
- muted antique gold, cold ivory and steel blue;
- no national flag accents in the logo, interface or generated media;
- premium European club heritage, stadium/arena light, editorial grid;
- subtle sports textile and archival-paper texture;
- large condensed display typography and neutral readable body typography;
- thin structural lines rather than heavy shadows;
- multi-sport visuals across football, basketball and volleyball.

Avoid neon esports, generic SaaS gradients, excessive gold, glossy 3D, balls as
the primary motif, copied club identities and rigid repeated card systems.
Sections should feel related but may use different compositions. The system
must remain easy to revise after client feedback.

## Information architecture

1. Accessible header: brand, «Возможности», «Подписки», «SMM»,
   «Как работает», CTA «Открыть бота».
2. Hero: `DIGITAL CLUB OPERATIONS`, «Автоматическое управление клубом», short copy
   about matches, training, payments, statistics and content in Telegram,
   CTA to subscriptions and Telegram. Use desktop/mobile hero art and the
   product-platform visual where compositionally appropriate.
3. Problem → result: chats to lineup, receipts to reporting, match data to
   statistics/content, manual reminders to automated scenarios.
4. One product capability system grouped as «Матчи», «Команда», «Финансы»,
   «Развитие», «Медиа». These are not separately sold modules.
5. Three subscription levels with Standard visually recommended. No prices.
   Include a desktop comparison and usable mobile disclosure/list treatment;
   important differences must not depend on hover.
6. SMM showcase: show Modern Heritage, Street Calcio and Tactical Grid as
   selectable full visual systems, then announcement, match day/lineup, result,
   MVP, standings/week, video and animation. Explain how SMM grows by level.
7. Four-step workflow: club connects, SportsSmartBot gathers data, automated
   scenarios run, the team receives the result.
8. Automation: show how the bot prepares a match, reconciles collections,
   updates club data and releases content. Do not present people as product
   modules or imply that a separate SMM specialist is required.
9. Closing CTA: «Пусть команда занимается спортом, а не таблицами и
   напоминаниями».
10. Footer with brand, concise positioning, navigation and existing Telegram
    link from the current site.

## Copy rules

Write natural, concise Russian. Avoid hype, bureaucracy and unverified claims.
Do not invent customer numbers, savings percentages, testimonials, prices,
integrations, legal data or social accounts. Useful phrasing includes:

- «Один бот — весь клубный ритм».
- «От опроса на матч до готовой публикации».
- «Меньше ручной координации. Больше времени на игру».
- «Данные клуба начинают работать на клуб».

## Technical requirements

- Keep the project static and GitHub Pages compatible.
- Inspect and update the template, build script, data model, CSS, JS and assets.
- Semantic HTML, mobile-first from 360px, WCAG AA, keyboard navigation,
  visible focus, useful alt text and `prefers-reduced-motion`.
- Optimize generated PNG sources into WebP/AVIF as appropriate. Preserve the
  original PNG files as source assets but serve optimized versions.
- Hero/LCP media must not use lazy loading; below-the-fold images should.
- Add explicit image dimensions and responsive `<picture>` where useful.
- Use restrained `transform`/`opacity` motion only.
- No horizontal overflow and no dead buttons.
- Keep the existing Telegram URL for every Telegram CTA.
- Update metadata, Open Graph image, favicon and title/description for
  SportsSmartBot.
- The build script must validate and build the redesigned site without relying
  on the obsolete four-module catalog contract.
- Do not add a heavyweight framework or runtime dependency.

## Generated source asset map

All generated source images are in `site/assets/generated/`:

- `hero-desktop.png`, `hero-mobile.png` — responsive hero art.
- `product-platform.png` — product UI visualization.
- `tier-basic.png`, `tier-standard.png`, `tier-maximum.png` — subscriptions.
- `capabilities-grid.png` — capability mosaic.
- `smm-match-announce.png`, `smm-match-result-v2.png`, `smm-mvp.png`,
  `smm-standings-v2.png` — SMM gallery.
- `style-modern-heritage.png`, `style-street-calcio.png`,
  `style-tactical-grid.png` — visual-system showcase.
- `workflow.png` — workflow visual.
- `cta-team-v3.png` — closing CTA background with corrected anatomy.
- `texture.png` — quiet background texture.
- `og-cover-v2.png` — Open Graph art without baked-in copy.

Use judgment: not every asset must appear at full size. Crop responsively and
prefer hierarchy over displaying everything. The design must remain modular
and easy to change after client review, not a rigid template system.
