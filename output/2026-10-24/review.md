# Обзор 10 репозиториев — 2026-10-24

Подборка собрана автоматически: репозитории отобраны по звёздам и активности, проверены статическими анализаторами безопасности и разобраны моделью.

## Содержание

1. [K0NL/B2recomp](#1-k0nlb2recomp)
2. [humblemuzzu/dumbtv](#2-humblemuzzudumbtv)
3. [pengchujin/aerial-tv](#3-pengchujinaerial-tv)
4. [ikow/php2shell-poc](#4-ikowphp2shell-poc)
5. [UniXNU/UniXNU](#5-unixnuunixnu)
6. [simbasjungles/free-my-tv](#6-simbasjunglesfree-my-tv)
7. [alchaincyf/huashu-motion](#7-alchaincyfhuashu-motion)
8. [Ansub/tv-detox](#8-ansubtv-detox)
9. [wesbos/3d-model-anything](#9-wesbos3d-model-anything)
10. [mihirgupta0900/tv-home](#10-mihirgupta0900tv-home)

### Первый — [K0NL/B2recomp](https://github.com/K0NL/B2recomp)

B2recomp is an unofficial static recompilation of Bayonetta 2 (Switch) that translates the game’s AArch64 code to C and builds a native Windows executable. It re‑implements the system layer (threads, file I/O, audio, input, NVN‑to‑Vulkan graphics) so the game runs without emulation. The source contains no game assets or Nintendo SDK code.

**Кому пригодится:** Designed for owners of a legally dumped copy of Bayonetta 2 who want to play the title on Windows with native performance and without an emulator. Useful for preservation enthusiasts and developers interested in static recompilation techniques. (gaming, windows, cli, graphics, reverse-engineering)

**Чем отличается от аналогов:** Unlike traditional emulators, B2recomp performs a full static translation of the original binary to C, eliminating runtime interpretation or JIT. It also provides a custom Vulkan‑based renderer and system layer, offering near‑original performance and HDR support.

**Плюсы:**
- Runs Bayonetta 2 natively on Windows
- No emulator overhead, full static translation
- Vulkan renderer with HDR and high‑fps support
- Active updates and community testing

**Минусы:**
- Requires a legally dumped copy of the game
- Documentation limited to build steps; no extensive API docs
- Linux support is still experimental

**Метрики:** 409 звёзд · 9 форков · язык C · лицензия GPL-3.0 · создан 2026-10-17 · последний коммит 2026-10-23

**Проверка безопасности:** Находки — semgrep: 0, bandit: 82, gitleaks: 0; critical=0, high=0

**Оценка:** 8.0/10 · итоговый скор 3.68

### Второй — [humblemuzzu/dumbtv](https://github.com/humblemuzzu/dumbtv)

dumbtv removes ads, tracking and clutter from Amazon Fire TV devices via ADB without requiring root, and provides a lightweight open‑source home screen. It also installs a DNS filter to block telemetry and can be undone.

**Кому пригодится:** Для владельцев Fire TV, Fire TV Stick и аналогичных Android‑TV устройств, желающих избавиться от рекламных и телеметрических сервисов, а также получить простой домашний экран без лишних разрешений. (android-tv, adb, cli, privacy, home-screen, devops)

**Чем отличается от аналогов:** Работает полностью через ADB без рут‑доступа, сочетает скрипты очистки с собственным открытым лаунчером и встроенным DNS‑фильтром, что редко встречается в аналогичных проектах.

**Плюсы:**
- Не требует root‑доступа
- Полностью откатываемый процесс
- Встроенный открытый лаунчер (54 KB)
- DNS‑фильтр блокирует телеметрию

**Минусы:**
- Наличие 5 high‑severity уязвимостей (semgrep/bandit)
- Документация разбросана по внешним сайтам, нет полного API‑гайда
- Метаданные лицензии указаны как NOASSERTION, хотя в README указан MIT

**Метрики:** 1421 звёзд · 127 форков · язык Java · лицензия NOASSERTION · создан 2026-10-18 · последний коммит 2026-10-22

**Проверка безопасности:** Находки — semgrep: 5, bandit: 23, gitleaks: 0; critical=0, high=5

**Оценка:** 7.5/10 · итоговый скор 3.41

### Третий — [pengchujin/aerial-tv](https://github.com/pengchujin/aerial-tv)

Aerial – открытый лаунчер для Android TV, стилизованный под tvOS, предоставляющий чистый рабочий стол без рекламных рекомендаций. Приложение автоматически захватывает запуск, поддерживает скринсейверы, обои и контрольный центр.

**Кому пригодится:** Для владельцев китайских Android‑телевизоров (Xiaomi, TCL, OPPO и др.), желающих заменить штатный рекламный интерфейс на минималистичный, настраиваемый и безрекламный лаунчер. (android, tv, mobile, ui, launcher)

**Чем отличается от аналогов:** Отличается tvOS‑подобным дизайном, полной заменой домашнего экрана без необходимости рутировать устройство, а также встроенными скринсейверами и контрольным центром, чего нет у большинства стандартных Android TV‑пакетов.

**Плюсы:**
- Отсутствие рекламы и рекомендаций
- tvOS‑стильный UI, знакомый пользователям Apple TV
- Не требует root и легко откатывается
- Широкие возможности кастомизации (обои, скринсейвер, контрольный центр)

**Минусы:**
- 8 high‑severity уязвимостей, обнаруженных сканерами
- Документация в основном на китайском, ограничивает международных пользователей
- Поддержка ограничена в основном китайскими брендами TV

**Метрики:** 4099 звёзд · 313 форков · язык Kotlin · лицензия MIT · создан 2026-10-20 · последний коммит 2026-10-24

**Проверка безопасности:** Находки — semgrep: 7, bandit: 6, gitleaks: 0; critical=0, high=8

**Оценка:** 7.0/10 · итоговый скор 3.23

### Четвёртый — [ikow/php2shell-poc](https://github.com/ikow/php2shell-poc)

The repository provides exploit code and detection rules for CVE‑2026‑109618 and CVE‑2026‑109619, two critical pre‑authentication RCE vulnerabilities in PHP’s session.upload_progress feature. It includes five independent exploit chains, three public Python/PHP PoCs, and Suricata, Sigma and ModSecurity rules for detection.

**Кому пригодится:** Security researchers, red‑team operators and IDS/WAF developers can use it to understand the vulnerabilities, test defenses, and integrate detection signatures into their monitoring stacks. (security, exploit-development, ids, waf, php, cve)

**Чем отличается от аналогов:** It combines full exploit implementations with ready‑to‑use detection rules for multiple platforms, covering a very broad PHP version range (5.4‑8.5) and offering both public and paid exploit variants.

**Плюсы:**
- Comprehensive exploit chains covering multiple attack vectors
- Includes ready‑made detection rules for Suricata, Sigma and ModSecurity
- Covers 78 % of web sites across many frameworks
- Detailed README and external write‑up for deeper analysis

**Минусы:**
- Static analysis reports a high‑severity issue (bandit) in the code
- Tool is intended for research/red‑team use only, not production hardening
- Python scripts lack extensive type‑hinting/documentation

**Метрики:** 1718 звёзд · 599 форков · язык Python · лицензия MIT · создан 2026-10-21 · последний коммит 2026-10-22

**Проверка безопасности:** Находки — semgrep: 1, bandit: 1, gitleaks: 0; critical=0, high=1

**Оценка:** 7.0/10 · итоговый скор 3.21

### Пятый — [UniXNU/UniXNU](https://github.com/UniXNU/UniXNU)

UniXNU is an independent project that enables iOS and macOS to run on non-Apple ARM64 hardware via a UEFI boot manager and custom build driver. It provides patches, submodules and drivers, including a native Metal GPU driver for supported devices.

**Кому пригодится:** Useful for developers, researchers and hobbyists who want to experiment with or port Apple operating systems to generic ARM64 platforms, facilitating boot, debugging and driver development. (os, bootloader, firmware, hardware)

**Чем отличается от аналогов:** Combines a UEFI boot chain with custom XNU patches for 4 KiB pages and native Metal GPU support, a capability rarely found in other open-source Apple-OS boot projects.

**Плюсы:**
- Active development with recent updates
- Comprehensive online documentation
- Modular architecture via submodules
- Native Metal GPU driver support

**Минусы:**
- 38 high-severity security findings reported by scanners
- Complex setup requiring submodule handling
- Hardware support currently limited to few devices

**Метрики:** 871 звёзд · 159 форков · язык Python · лицензия NOASSERTION · создан 2026-10-19 · последний коммит 2026-10-23

**Проверка безопасности:** Находки — semgrep: 24, bandit: 1128, gitleaks: 4, osv: 22; critical=0, high=38

**Оценка:** 7.0/10 · итоговый скор 3.20

### Шестой — [simbasjungles/free-my-tv](https://github.com/simbasjungles/free-my-tv)

Free My TV is an open‑source launcher that replaces the default home screen on Google TV, LG webOS and Samsung Tizen devices. It provides an ad‑free, fast UI with personalized app shelves, weather, crypto prices and a dynamic light/dark theme.

**Кому пригодится:** Designed for TV owners who want a clean, responsive home screen without ads and with quick access to their favorite streaming apps and useful widgets. (android-tv, launcher, home-screen, open-source)

**Чем отличается от аналогов:** Combines a glass‑shelf UI, real‑time trending picks, and automatic sunset‑based theming, all built with Claude Code and offering a one‑click undo to the factory launcher.

**Плюсы:**
- Ad‑free experience
- High performance (60 fps, low memory)
- Rich widgets (weather, crypto, photos)
- One‑button revert to factory screen

**Минусы:**
- 21 high‑severity security findings (semgrep/bandit)
- Very new project – limited long‑term stability data
- Supports only TV platforms (no mobile/desktop)

**Метрики:** 4063 звёзд · 631 форков · язык Java · лицензия MIT · создан 2026-10-19 · последний коммит 2026-10-24

**Проверка безопасности:** Находки — semgrep: 21, bandit: 15, gitleaks: 0; critical=0, high=21

**Оценка:** 6.5/10 · итоговый скор 3.03

### Седьмой — [alchaincyf/huashu-motion](https://github.com/alchaincyf/huashu-motion)

huashu-motion is a JavaScript library that lets AI agents generate commercial‑grade launch videos with animation and music, and allows point‑and‑click edits of individual frames. It integrates with Claude Code, Codex and other agents to produce complete videos from a single prompt.

**Кому пригодится:** Designed for developers and product teams who want to automate video creation and quickly iterate on motion‑graphics without manual editing, especially when using AI coding agents. (cli, animation, ai, javascript, frontend)

**Чем отличается от аналогов:** Combines AI‑driven script and music generation with an interactive editor that can modify specific frames by pointing at them, a capability rare among existing video‑automation tools.

**Плюсы:**
- One‑click generation of full videos
- Interactive point‑and‑click editing
- Built‑in music composition using ABC notation
- Open‑source MIT license

**Минусы:**
- 14 high‑severity security findings reported by semgrep
- Documentation primarily in Chinese may limit non‑Chinese users
- Relatively new (created in 2026) – ecosystem still maturing

**Метрики:** 1563 звёзд · 154 форков · язык JavaScript · лицензия MIT · создан 2026-10-18 · последний коммит 2026-10-22

**Проверка безопасности:** Находки — semgrep: 8, bandit: 0, gitleaks: 6; critical=0, high=14

**Оценка:** 6.5/10 · итоговый скор 3.01

### Восьмой — [Ansub/tv-detox](https://github.com/Ansub/tv-detox)

TV Detox is an Android TV application that replaces the default home screen with a minimal, ad‑free interface and can disable bloatware using AI prompts. It leverages Claude Code or Codex to automate the cleanup process.

**Кому пригодится:** Designed for owners of older or sluggish Android TVs who want a faster, cleaner experience without ads or unwanted system apps. (android, mobile, ai, home-screen)

**Чем отличается от аналогов:** Combines AI‑driven instructions with a lightweight home‑screen replacement, unlike typical ad‑blockers that only hide content.

**Плюсы:**
- Simple one‑click cleanup via remote
- Ad‑free minimal UI
- Uses AI to safely turn off system apps
- Open‑source MIT license

**Минусы:**
- 10 high‑severity security findings reported by semgrep
- Documentation limited to basic setup steps
- Works only on Android TV devices

**Метрики:** 1415 звёзд · 145 форков · язык Java · лицензия MIT · создан 2026-10-18 · последний коммит 2026-10-24

**Проверка безопасности:** Находки — semgrep: 10, bandit: 0, gitleaks: 0; critical=0, high=10

**Оценка:** 6.5/10 · итоговый скор 3.01

### Девятый — [wesbos/3d-model-anything](https://github.com/wesbos/3d-model-anything)

The project provides an iPhone app that captures rooms using LiDAR or photos and reconstructs them into editable Three.js scenes. It also includes a web viewer and an AI‑driven skill to guide the reconstruction workflow. The code is source‑available and the viewer can be run locally with Node.js.

**Кому пригодится:** Designed for developers, AR/VR creators, and interior designers who need to digitize real spaces and integrate them into web‑based 3D environments. Also useful for AI‑agent developers looking to automate 3D reconstruction tasks. (ios, ar, 3d, computer-vision, web, ai, cli)

**Чем отличается от аналогов:** Combines on‑device LiDAR capture with an AI coding agent and a fully editable Three.js output, offering an iterative workflow rather than a one‑click conversion. Includes both iOS capture tools and a web viewer in a single repository.

**Плюсы:**
- Comprehensive README with setup instructions
- MIT‑licensed source code for the core components
- Integrated AI skill for automated reconstruction
- Live web viewer for immediate inspection

**Минусы:**
- High‑severity security findings (8 high) reported by scanners
- License metadata shows NOASSERTION despite MIT notice, causing ambiguity
- Limited to LiDAR‑equipped iOS devices for full capture functionality

**Метрики:** 1331 звёзд · 220 форков · язык Swift · лицензия NOASSERTION · создан 2026-10-21 · последний коммит 2026-10-22

**Проверка безопасности:** Находки — semgrep: 10, bandit: 8, gitleaks: 0, osv: 0; critical=0, high=8

**Оценка:** 6.5/10 · итоговый скор 3.01

### Десятый — [mihirgupta0900/tv-home](https://github.com/mihirgupta0900/tv-home)

The project provides scripts and a lightweight custom launcher to debloat Android TV devices over Wi‑Fi and replace the stock UI with an Apple‑TV‑style home screen. It supports both manual execution and automated generation via Claude Code prompts. All changes are reversible, disabling apps rather than uninstalling them.

**Кому пригодится:** Helps Android TV owners, especially those with low‑spec devices, to improve performance, remove unwanted ads/telemetry, and enjoy a cleaner, faster home screen experience. (android-tv, cli, launcher, automation)

**Чем отличается от аналогов:** Combines reversible ADB‑based debloating with a ready‑made minimalist launcher and integrates AI‑driven automation through Claude Code, a niche not commonly found in generic Android TV tweaks.

**Плюсы:**
- Significant memory and performance gains on low‑end TVs
- Reversible debloating – no permanent uninstallations
- Apple‑TV‑style launcher with rotating wallpapers
- One‑click AI automation via Claude Code

**Минусы:**
- High‑severity issue reported by Bandit (security risk)
- No explicit open‑source license (NOASSERTION)
- Documentation limited to README; no detailed guides or API docs

**Метрики:** 434 звёзд · 63 форков · язык Java · лицензия NOASSERTION · создан 2026-10-18 · последний коммит 2026-10-18

**Проверка безопасности:** Находки — semgrep: 0, bandit: 1, gitleaks: 0, osv: 0; critical=0, high=1

**Оценка:** 6.5/10 · итоговый скор 2.88

## Ссылки

1. K0NL/B2recomp — https://github.com/K0NL/B2recomp
2. humblemuzzu/dumbtv — https://github.com/humblemuzzu/dumbtv
3. pengchujin/aerial-tv — https://github.com/pengchujin/aerial-tv
4. ikow/php2shell-poc — https://github.com/ikow/php2shell-poc
5. UniXNU/UniXNU — https://github.com/UniXNU/UniXNU
6. simbasjungles/free-my-tv — https://github.com/simbasjungles/free-my-tv
7. alchaincyf/huashu-motion — https://github.com/alchaincyf/huashu-motion
8. Ansub/tv-detox — https://github.com/Ansub/tv-detox
9. wesbos/3d-model-anything — https://github.com/wesbos/3d-model-anything
10. mihirgupta0900/tv-home — https://github.com/mihirgupta0900/tv-home
