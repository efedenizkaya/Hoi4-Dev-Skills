# Performance — profiling and the cost of script

HOI4 runs your script every game hour. Late-game lag is almost always
script cost, and the game ships its own profiler to find it. This page is
the workflow; the validator's `periodic-effect-performance` rule is the
static guard.

## The profiler workflow

1. Launch the game in developer mode (console available; `-debug` works).
2. Open the console and run `imgui show profiler` — `imgui` is a
   documented console command (`Controls ImGui UIs. See the sub
   commands.` in `documentation/console_commands_documentation.md`).
   CLAIM(profiler-command)
3. In the profiler window press **Enable Collection** — per-process cost
   renders as a graph. `[unverified]`
4. Open the **Script** tab, press **Start**, advance time, then **Stop** —
   a ranked list of script costs appears. `[unverified]`
5. Read the list: `ms` per entry, entries grouped as `gamestate.hourly`,
   `gamestate.daily`, `gamestate.weekly` — the cadence the script runs
   at. `[unverified]`

CLAIM(profiler-workflow)

## The cost hierarchy

- **`hourly` runs 24× per game day per country** — anything heavy here
  (mission activation checks, `any_state`/`all_state` scans, variable
  loops) dominates late-game cost. CLAIM(hourly-dominates)
- `daily` runs once per day; `weekly` is cheap by comparison.
- Missions (decisions with `activation`) evaluate their activation
  trigger on the hourly tick — a mission with an `any_state` scan in
  `activation` costs that scan every hour for every country that can see
  it. Prefer plain decisions/events when continuous checking is not
  needed (see [decisions.md](decisions.md) mission grammar).
  CLAIM(mission-hourly-cost)

## The standard optimizations

1. **Early exit**: order triggers cheapest-first and make the most
   selective condition the first line — later lines only evaluate when
   earlier ones passed. `[unverified]`
2. **Replace heavy scans**: `any_state = { is_controlled_by = ITA ... }`
   evaluated hourly → precompute with variables on state capture
   (on_actions), or convert the mission into a plain decision or event.
3. **Fewer scripted GUI polling elements** — see
   [scripted-gui.md](scripted-gui.md).
4. Delete dead content: leftover events/ideas still load and evaluate
   (the dogfood census found 34 fired-but-undefined event targets and
   833 duplicate loc keys in one real mod — dead weight ships too).

CLAIM(perf-optimizations)

## Workflow

1. `scripts/validate.py` — the `periodic-effect-performance` rule flags
   every `on_daily`/`on_hourly` hook (heuristic label).
2. Profile with the steps above; fix the top `gamestate.hourly` entries.
3. Re-profile the SAME time window and compare `ms`.
