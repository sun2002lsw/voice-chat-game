CREATE TABLE IF NOT EXISTS scenario_progress (
  scenario_name TEXT PRIMARY KEY,
  current_step_name TEXT NOT NULL,
  step_visits_json TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dialog_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scenario_name TEXT NOT NULL,
  role TEXT NOT NULL,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS state_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scenario_name TEXT NOT NULL,
  step_name TEXT NOT NULL,
  visit_count INTEGER NOT NULL,
  conditions_json TEXT NOT NULL,
  next_step_names_json TEXT NOT NULL,
  character_script TEXT NOT NULL,
  user_input TEXT NOT NULL,
  llm_index INTEGER
);

CREATE INDEX IF NOT EXISTS idx_dialog_scenario ON dialog_log(scenario_name, id);
CREATE INDEX IF NOT EXISTS idx_state_scenario ON state_log(scenario_name, id);
