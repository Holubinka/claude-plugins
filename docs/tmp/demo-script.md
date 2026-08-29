# Сценарій демо-відео

Шість сцен, ~12 хвилин. Кожна має видиму зміну на екрані — не «повірте, воно спрацювало».

**Демо ходить між двома теками — тримайте два термінали, по одному на кожну.**

| | Тека | Що там робиться |
| :--- | :--- | :--- |
| **A** | `~/WebstormProjects/claude-plugins` | маркетплейс: валідація, лінтер, теги |
| **B** | `~/WebstormProjects/Lavego/luiverse` | цільовий проєкт: workflow, project-scope коміт |

Команди `claude plugin …` працюють із будь-якої теки — вони змінюють конфіг машини, а не
проєкту. Виняток один: усе з `--scope project` пише в ту теку, з якої запущено, тож для них
термінал **B** обов'язковий.

Каталог у браузері: <https://holubinka.github.io/claude-plugins/>

---

## Сцена 0 — підготовка (не знімається)

Привести машину до чистого старту й **повернути живий канал**, бо project-scope конфіг, який ми
закомітимо в сцені 1, має посилатися на GitHub, а не на локальну теку.

```sh
claude plugin uninstall sdd-engineering --keep-data
claude plugin marketplace remove dev-workbench
claude plugin marketplace add Holubinka/claude-plugins
```

Stable-клон лишаємо на диску — він знадобиться в сценах 3 і 6:

```sh
ls ~/dw-stable/.claude-plugin/marketplace.json   # має існувати
```

Якщо його немає:

```sh
git clone --depth 1 --branch sdd-engineering--v1.0.0 \
  https://github.com/Holubinka/claude-plugins ~/dw-stable
```

---

## Сцена 1 — repository marketplace · ~2 хв

**Показати в браузері:** <https://github.com/Holubinka/claude-plugins>

Пройтись по трьох речах, не читаючи вголос:

- `.claude-plugin/marketplace.json` — чотири записи, у кожного `source: ./plugins/<name>`, і **в жодного немає `version`**. Сказати чому: версія живе тільки в `plugin.json`, інакше два джерела розійдуться.
- `plugins/` — чотири теки, у кожної свій `.claude-plugin/plugin.json`, `README.md`.
- Вкладка **Tags** — десять тегів виду `{plugin}--v{version}`. Сказати: проти них резолвляться констрейнти залежностей; нетегований реліз не можна взяти в залежність.

**У терміналі A** — обидві команди йдуть із кореня маркетплейсу: крапка в `validate .` це
тека з `.claude-plugin/marketplace.json`, а лінтер лежить у тому ж репозиторії. З іншої теки
буде `✘ Validation failed · error: no .claude-plugin/marketplace.json`.

```sh
cd ~/WebstormProjects/claude-plugins
claude plugin validate .
python3 scripts/lint-structure.py
```

Показати `✔ Validation passed` і `0 error(s), 0 warning(s)`.

Одним реченням: `claude plugin validate` не бачить компонентів, вкладених у `.claude-plugin/`,
розбіжності імені з текою і незареєстрованого плагіна — тому другий лінтер існує окремо.

---

## Сцена 2 — catalog UI · ~2 хв

**Відкрити** <https://holubinka.github.io/claude-plugins/>

- Шапка: **4 plugins · 54 artifacts**.
- Ввести в пошук `a skill that reviews boundaries` — показати, що результат пояснює, **чому** він
  збігся, і скільки коштує контексту.
- Зняти запит і показати **фасети без жодного запиту**: `type`, `plugin`, `category`, `keyword`.
  Клацнути `keyword: spec-driven` → п'ять компонентів. Додати `type: agent` → чотири агенти.
- `/graph/` — граф залежностей, на ребрах діапазони. Сказати: намальовано індексатором як
  статичний SVG, жодної графової бібліотеки в браузер не їде.
- `/releases/` — десять релізів. Показати, що вони згенеровані з git-тегів, а не написані руками.

Сказати: сторінка збирається з репозиторію на кожен пуш у `main`, тож вона не може описати
плагін, якого немає, і не може пропустити той, що є.

---

## Сцена 3 — встановлення sdd-engineering@1.0.0 · ~2 хв

Живий канал зараз віддав би 1.1.0, а нам потрібна саме 1.0.0 — тож ставимо зі **stable-каналу,
пришпиленого до тега релізу**. Термінал будь-який — далі зручно лишитись в **A**.

```sh
claude plugin marketplace remove dev-workbench
claude plugin marketplace add ~/dw-stable
claude plugin install sdd-engineering@dev-workbench
```

**Показати вивід:** `+ 3 dependencies` — залежності приїхали самі.

```sh
claude plugin list --json \
  | jq '[.[] | select(.id | endswith("@dev-workbench"))] | map({id, version, enabled, errors})'
```

Чотири записи, і в кожному:

- `"enabled": true`;
- **`"errors": null`** — ні `dependency-unsatisfied`, ні `range-conflict`, ні `no-matching-tag`;
- у `sdd-engineering` версія рівно `1.0.0`, а в трьох залежностей — з суфіксом коміта
  (`1.0.0-e7d4ac88bccd`). Сказати чому: джерело це клон, пришпилений до тега, тож Claude Code
  дописує SHA. Для відкату це саме та мітка походження, яку хочеться бачити.

```sh
claude plugin details sdd-engineering
```

Показати інвентар — 4 агенти, 3 скіли — і рядок **Always-on: ~1,087 tok**. Сказати: це те, що
лежить у контексті кожної сесії; тіла платяться на виклику.

---

## Сцена 4 — робочий workflow на 1.0.0 · ~3 хв

**Термінал B.** Оголошувати плагіни на рівні проєкту тут **ще рано** — це сцена 5, і чому саме
так, сказано там. Зараз вони доступні через user scope, тобто в кожному проєкті на машині.

```sh
cd ~/WebstormProjects/Lavego/luiverse
claude          # відкрити Claude Code саме тут
```

Дати `spec-creator` запит, у якому одна ціль навмисно без числа:

> Use the spec-creator agent to specify a "saved views" feature: a user can save the current
> filter set under a name, share it by link, and the list of saved views should load fast enough
> not to delay the page.

**На що дивитись у відповіді:**

- агент **питає, а не вигадує** — або повертає блок уточнення, або пише спеку з `Q-N`;
- критерії у форматі EARS: `WHEN …, the system shall …`;
- **третя ціль про «fast enough» проходить без числа** — на 1.0.0 гейта покриття ще немає.

Це та поведінка, яку 1.1.0 змінює. Запам'ятати вивід — він знадобиться для порівняння.

---

## Сцена 5 — update до 1.1.0 · ~2 хв

Спершу показати, що **оновлення каталогу і оновлення плагіна це різні речі**. Термінал
будь-який:

```sh
claude plugin marketplace remove dev-workbench
claude plugin marketplace add Holubinka/claude-plugins
claude plugin marketplace update dev-workbench
claude plugin list          # ← версія ще стара
```

Наголосити: каталог освіжився, встановлене не змінилось. Тепер саме оновлення:

```sh
claude plugin update sdd-engineering
```

Показати рядок `updated from 1.0.0 to 1.1.0` і **`Restart to apply changes`** — сесія, що вже
працює, лишається на старій версії.

```
/reload-plugins
```

Тепер, коли `dev-workbench` знову вказує на GitHub, **оголосити плагіни на рівні проєкту**, щоб
їх отримав кожен, хто склонує репозиторій. **Обов'язково термінал B** — `--scope project` пише в
теку, з якої запущено:

```sh
cd ~/WebstormProjects/Lavego/luiverse
claude plugin marketplace add Holubinka/claude-plugins --scope project
claude plugin install sdd-engineering@dev-workbench --scope project
git diff .claude/settings.json
```

Показати доданий `extraKnownMarketplaces` із `{"source": "github", "repo": "Holubinka/claude-plugins"}`
— **не локальний шлях**. Закомітити: це і є дедлайновий артефакт «commit у проєкті, де плагін
встановлено».

**Чому саме тут, а не в сцені 4.** У сцені 3 user-scope `dev-workbench` вказує на `~/dw-stable`.
Оголошення project-scope **мовчки перекриває** user-scope для того самого імені — перевірено:
`marketplace list` після цього показує джерело з project, без жодного попередження. Тобто в
сцені 4 команда або закомітила б локальний шлях, або поставила б 1.1.0 замість 1.0.0, який та
сцена демонструє. Тут обидві пастки зникають.

Повторити **той самий запит** зі сцени 4. Показати різницю:

- у звіті з'явився рядок `## Coverage`;
- ціль «fast enough» більше не проходить мовчки — вона або отримала число, або стала `Q-N` зі
  спекою в статусі заблокованої.

Одна фраза: те саме питання, дві версії, різна поведінка — це і є доказ, що оновлення доїхало,
а не просто змінився номер.

---

## Сцена 6 — повернення через stable channel · ~2 хв

```sh
claude plugin uninstall sdd-engineering --keep-data
claude plugin marketplace remove dev-workbench
claude plugin marketplace add ~/dw-stable
claude plugin install sdd-engineering@dev-workbench
/reload-plugins
```

**Перевірити на трьох рівнях, а не за номером:**

```sh
claude plugin list | grep -A2 sdd-engineering
grep -c "The coverage gate" ~/.claude/plugins/cache/dev-workbench/sdd-engineering/1.0.0/agents/spec-creator.md
ls ~/.claude/plugins/cache/dev-workbench/sdd-engineering/
```

Показати: версія `1.0.0`; гейта у файлі агента **немає**; у кеші лежать `1.0.0` і `1.1.0`
**одночасно** — відкат переставив вказівник, а не завантажив щось наново.

Повторити запит утретє: рядок `## Coverage` зник, «fast enough» знову проходить.

Закрити двома тезами:

- **команди `plugin rollback` не існує** — відкат це чотири звичайні команди;
- **номер версії не йде вниз.** Це відкат каналу. Якщо ламане у всіх, а не в одного —
  відкат виглядає інакше: реверт у `main` і реліз *вищої* версії зі старою поведінкою, бо
  повторно випустити той самий номер означало б, що одна версія описує два різні дерева.

---

## Після зйомки

Повернути машину на живий канал:

```sh
claude plugin uninstall sdd-engineering --keep-data
claude plugin marketplace remove dev-workbench
claude plugin marketplace add Holubinka/claude-plugins
claude plugin install sdd-engineering@dev-workbench
```

## Чотири речі, які зіпсують дубль

- **Обидва канали звуться `dev-workbench`.** Разом вони не стоять — перед `add` завжди `remove`.
- **`/reload-plugins` обов'язковий** після кожного `install` чи `update`, інакше на екрані стара
  поведінка при новому номері, і це виглядає як зламане оновлення.
- **`--scope project` треба робити на живому каналі** (тому воно в сцені 5, а не 4). Однакове
  ім'я в двох scope не конфліктує й не попереджає — project просто виграє, тож із `~/dw-stable`
  у коміт тихо потрапив би локальний шлях.
- **`marketplace update` не полагодить зіпсоване джерело.** Воно освіжає з того, що записано в
  `~/.claude/plugins/known_marketplaces.json`, а не з `settings.json`. Якщо `marketplace list`
  показує не те джерело — рятує тільки `remove` і `add` наново.
- **`jq` має бути в PATH** — на ньому тримається write-gate у `spec-creator`. Без нього агент
  відмовить на першому ж записі, і на відео це виглядатиме як баг плагіна.
