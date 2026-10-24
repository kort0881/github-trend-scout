Всем привет! Сегодня у нас обзор 10 новых репозиториев, которые могут пригодиться абсолютно разным людям.

Первый наш участник — K0NL/B2recomp.
Чем он примечателен: B2recomp is an unofficial static recompilation of Bayonetta 2 (Switch) that translates the game’s AArch64 code to C and builds a native Windows executable. It re‑implements the system layer (threads, file I/O, audio, input, NVN‑to‑Vulkan graphics) so the game runs without emulation. The source contains no game assets or Nintendo SDK code.
Кому пригодится: Designed for owners of a legally dumped copy of Bayonetta 2 who want to play the title on Windows with native performance and without an emulator. Useful for preservation enthusiasts and developers interested in static recompilation techniques.
У него Runs Bayonetta 2 natively on Windows; No emulator overhead, full static translation; Vulkan renderer with HDR and high‑fps support; Active updates and community testing.
Но есть и недостатки: Requires a legally dumped copy of the game; Documentation limited to build steps; no extensive API docs; Linux support is still experimental.
Чем отличается от аналогов: Unlike traditional emulators, B2recomp performs a full static translation of the original binary to C, eliminating runtime interpretation or JIT. It also provides a custom Vulkan‑based renderer and system layer, offering near‑original performance and HDR support.
Целевая аудитория: gaming, windows, cli, graphics, reverse-engineering. На момент обзора у проекта 409 звёзд, 9 форков, основной язык — C, лицензия — GPL-3.0. Последний коммит: 2026-10-23.
Проверка безопасности: Находки — semgrep: 0, bandit: 82, gitleaks: 0; critical=0, high=0.

Номер два — humblemuzzu/dumbtv.
Чем он примечателен: dumbtv removes ads, tracking and clutter from Amazon Fire TV devices via ADB without requiring root, and provides a lightweight open‑source home screen. It also installs a DNS filter to block telemetry and can be undone.
Кому пригодится: Для владельцев Fire TV, Fire TV Stick и аналогичных Android‑TV устройств, желающих избавиться от рекламных и телеметрических сервисов, а также получить простой домашний экран без лишних разрешений.
У него Не требует root‑доступа; Полностью откатываемый процесс; Встроенный открытый лаунчер (54 KB); DNS‑фильтр блокирует телеметрию.
Но есть и недостатки: Наличие 5 high‑severity уязвимостей (semgrep/bandit); Документация разбросана по внешним сайтам, нет полного API‑гайда; Метаданные лицензии указаны как NOASSERTION, хотя в README указан MIT.
Чем отличается от аналогов: Работает полностью через ADB без рут‑доступа, сочетает скрипты очистки с собственным открытым лаунчером и встроенным DNS‑фильтром, что редко встречается в аналогичных проектах.
Целевая аудитория: android-tv, adb, cli, privacy, home-screen, devops. На момент обзора у проекта 1421 звёзд, 127 форков, основной язык — Java, лицензия — NOASSERTION. Последний коммит: 2026-10-22.
Проверка безопасности: Находки — semgrep: 5, bandit: 23, gitleaks: 0; critical=0, high=5.

Третий участник — pengchujin/aerial-tv.
Чем он примечателен: Aerial – открытый лаунчер для Android TV, стилизованный под tvOS, предоставляющий чистый рабочий стол без рекламных рекомендаций. Приложение автоматически захватывает запуск, поддерживает скринсейверы, обои и контрольный центр.
Кому пригодится: Для владельцев китайских Android‑телевизоров (Xiaomi, TCL, OPPO и др.), желающих заменить штатный рекламный интерфейс на минималистичный, настраиваемый и безрекламный лаунчер.
У него Отсутствие рекламы и рекомендаций; tvOS‑стильный UI, знакомый пользователям Apple TV; Не требует root и легко откатывается; Широкие возможности кастомизации (обои, скринсейвер, контрольный центр).
Но есть и недостатки: 8 high‑severity уязвимостей, обнаруженных сканерами; Документация в основном на китайском, ограничивает международных пользователей; Поддержка ограничена в основном китайскими брендами TV.
Чем отличается от аналогов: Отличается tvOS‑подобным дизайном, полной заменой домашнего экрана без необходимости рутировать устройство, а также встроенными скринсейверами и контрольным центром, чего нет у большинства стандартных Android TV‑пакетов.
Целевая аудитория: android, tv, mobile, ui, launcher. На момент обзора у проекта 4099 звёзд, 313 форков, основной язык — Kotlin, лицензия — MIT. Последний коммит: 2026-10-24.
Проверка безопасности: Находки — semgrep: 7, bandit: 6, gitleaks: 0; critical=0, high=8.

Номер четыре — ikow/php2shell-poc.
Чем он примечателен: The repository provides exploit code and detection rules for CVE‑2026‑109618 and CVE‑2026‑109619, two critical pre‑authentication RCE vulnerabilities in PHP’s session.upload_progress feature. It includes five independent exploit chains, three public Python/PHP PoCs, and Suricata, Sigma and ModSecurity rules for detection.
Кому пригодится: Security researchers, red‑team operators and IDS/WAF developers can use it to understand the vulnerabilities, test defenses, and integrate detection signatures into their monitoring stacks.
У него Comprehensive exploit chains covering multiple attack vectors; Includes ready‑made detection rules for Suricata, Sigma and ModSecurity; Covers 78 % of web sites across many frameworks; Detailed README and external write‑up for deeper analysis.
Но есть и недостатки: Static analysis reports a high‑severity issue (bandit) in the code; Tool is intended for research/red‑team use only, not production hardening; Python scripts lack extensive type‑hinting/documentation.
Чем отличается от аналогов: It combines full exploit implementations with ready‑to‑use detection rules for multiple platforms, covering a very broad PHP version range (5.4‑8.5) and offering both public and paid exploit variants.
Целевая аудитория: security, exploit-development, ids, waf, php, cve. На момент обзора у проекта 1718 звёзд, 599 форков, основной язык — Python, лицензия — MIT. Последний коммит: 2026-10-22.
Проверка безопасности: Находки — semgrep: 1, bandit: 1, gitleaks: 0; critical=0, high=1.

Пятый участник — UniXNU/UniXNU.
Чем он примечателен: UniXNU is an independent project that enables iOS and macOS to run on non-Apple ARM64 hardware via a UEFI boot manager and custom build driver. It provides patches, submodules and drivers, including a native Metal GPU driver for supported devices.
Кому пригодится: Useful for developers, researchers and hobbyists who want to experiment with or port Apple operating systems to generic ARM64 platforms, facilitating boot, debugging and driver development.
У него Active development with recent updates; Comprehensive online documentation; Modular architecture via submodules; Native Metal GPU driver support.
Но есть и недостатки: 38 high-severity security findings reported by scanners; Complex setup requiring submodule handling; Hardware support currently limited to few devices.
Чем отличается от аналогов: Combines a UEFI boot chain with custom XNU patches for 4 KiB pages and native Metal GPU support, a capability rarely found in other open-source Apple-OS boot projects.
Целевая аудитория: os, bootloader, firmware, hardware. На момент обзора у проекта 871 звёзд, 159 форков, основной язык — Python, лицензия — NOASSERTION. Последний коммит: 2026-10-23.
Проверка безопасности: Находки — semgrep: 24, bandit: 1128, gitleaks: 4, osv: 22; critical=0, high=38.

Номер шесть — simbasjungles/free-my-tv.
Чем он примечателен: Free My TV is an open‑source launcher that replaces the default home screen on Google TV, LG webOS and Samsung Tizen devices. It provides an ad‑free, fast UI with personalized app shelves, weather, crypto prices and a dynamic light/dark theme.
Кому пригодится: Designed for TV owners who want a clean, responsive home screen without ads and with quick access to their favorite streaming apps and useful widgets.
У него Ad‑free experience; High performance (60 fps, low memory); Rich widgets (weather, crypto, photos); One‑button revert to factory screen.
Но есть и недостатки: 21 high‑severity security findings (semgrep/bandit); Very new project – limited long‑term stability data; Supports only TV platforms (no mobile/desktop).
Чем отличается от аналогов: Combines a glass‑shelf UI, real‑time trending picks, and automatic sunset‑based theming, all built with Claude Code and offering a one‑click undo to the factory launcher.
Целевая аудитория: android-tv, launcher, home-screen, open-source. На момент обзора у проекта 4063 звёзд, 631 форков, основной язык — Java, лицензия — MIT. Последний коммит: 2026-10-24.
Проверка безопасности: Находки — semgrep: 21, bandit: 15, gitleaks: 0; critical=0, high=21.

Седьмой участник — alchaincyf/huashu-motion.
Чем он примечателен: huashu-motion is a JavaScript library that lets AI agents generate commercial‑grade launch videos with animation and music, and allows point‑and‑click edits of individual frames. It integrates with Claude Code, Codex and other agents to produce complete videos from a single prompt.
Кому пригодится: Designed for developers and product teams who want to automate video creation and quickly iterate on motion‑graphics without manual editing, especially when using AI coding agents.
У него One‑click generation of full videos; Interactive point‑and‑click editing; Built‑in music composition using ABC notation; Open‑source MIT license.
Но есть и недостатки: 14 high‑severity security findings reported by semgrep; Documentation primarily in Chinese may limit non‑Chinese users; Relatively new (created in 2026) – ecosystem still maturing.
Чем отличается от аналогов: Combines AI‑driven script and music generation with an interactive editor that can modify specific frames by pointing at them, a capability rare among existing video‑automation tools.
Целевая аудитория: cli, animation, ai, javascript, frontend. На момент обзора у проекта 1563 звёзд, 154 форков, основной язык — JavaScript, лицензия — MIT. Последний коммит: 2026-10-22.
Проверка безопасности: Находки — semgrep: 8, bandit: 0, gitleaks: 6; critical=0, high=14.

Номер восемь — Ansub/tv-detox.
Чем он примечателен: TV Detox is an Android TV application that replaces the default home screen with a minimal, ad‑free interface and can disable bloatware using AI prompts. It leverages Claude Code or Codex to automate the cleanup process.
Кому пригодится: Designed for owners of older or sluggish Android TVs who want a faster, cleaner experience without ads or unwanted system apps.
У него Simple one‑click cleanup via remote; Ad‑free minimal UI; Uses AI to safely turn off system apps; Open‑source MIT license.
Но есть и недостатки: 10 high‑severity security findings reported by semgrep; Documentation limited to basic setup steps; Works only on Android TV devices.
Чем отличается от аналогов: Combines AI‑driven instructions with a lightweight home‑screen replacement, unlike typical ad‑blockers that only hide content.
Целевая аудитория: android, mobile, ai, home-screen. На момент обзора у проекта 1415 звёзд, 145 форков, основной язык — Java, лицензия — MIT. Последний коммит: 2026-10-24.
Проверка безопасности: Находки — semgrep: 10, bandit: 0, gitleaks: 0; critical=0, high=10.

Девятый участник — wesbos/3d-model-anything.
Чем он примечателен: The project provides an iPhone app that captures rooms using LiDAR or photos and reconstructs them into editable Three.js scenes. It also includes a web viewer and an AI‑driven skill to guide the reconstruction workflow. The code is source‑available and the viewer can be run locally with Node.js.
Кому пригодится: Designed for developers, AR/VR creators, and interior designers who need to digitize real spaces and integrate them into web‑based 3D environments. Also useful for AI‑agent developers looking to automate 3D reconstruction tasks.
У него Comprehensive README with setup instructions; MIT‑licensed source code for the core components; Integrated AI skill for automated reconstruction; Live web viewer for immediate inspection.
Но есть и недостатки: High‑severity security findings (8 high) reported by scanners; License metadata shows NOASSERTION despite MIT notice, causing ambiguity; Limited to LiDAR‑equipped iOS devices for full capture functionality.
Чем отличается от аналогов: Combines on‑device LiDAR capture with an AI coding agent and a fully editable Three.js output, offering an iterative workflow rather than a one‑click conversion. Includes both iOS capture tools and a web viewer in a single repository.
Целевая аудитория: ios, ar, 3d, computer-vision, web, ai, cli. На момент обзора у проекта 1331 звёзд, 220 форков, основной язык — Swift, лицензия — NOASSERTION. Последний коммит: 2026-10-22.
Проверка безопасности: Находки — semgrep: 10, bandit: 8, gitleaks: 0, osv: 0; critical=0, high=8.

Номер десять — mihirgupta0900/tv-home.
Чем он примечателен: The project provides scripts and a lightweight custom launcher to debloat Android TV devices over Wi‑Fi and replace the stock UI with an Apple‑TV‑style home screen. It supports both manual execution and automated generation via Claude Code prompts. All changes are reversible, disabling apps rather than uninstalling them.
Кому пригодится: Helps Android TV owners, especially those with low‑spec devices, to improve performance, remove unwanted ads/telemetry, and enjoy a cleaner, faster home screen experience.
У него Significant memory and performance gains on low‑end TVs; Reversible debloating – no permanent uninstallations; Apple‑TV‑style launcher with rotating wallpapers; One‑click AI automation via Claude Code.
Но есть и недостатки: High‑severity issue reported by Bandit (security risk); No explicit open‑source license (NOASSERTION); Documentation limited to README; no detailed guides or API docs.
Чем отличается от аналогов: Combines reversible ADB‑based debloating with a ready‑made minimalist launcher and integrates AI‑driven automation through Claude Code, a niche not commonly found in generic Android TV tweaks.
Целевая аудитория: android-tv, cli, launcher, automation. На момент обзора у проекта 434 звёзд, 63 форков, основной язык — Java, лицензия — NOASSERTION. Последний коммит: 2026-10-18.
Проверка безопасности: Находки — semgrep: 0, bandit: 1, gitleaks: 0, osv: 0; critical=0, high=1.

И в конце — все ссылки на репозитории в описании к видео.
Спасибо за просмотр, подписывайтесь, чтобы не пропустить следующий выпуск!

---

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
