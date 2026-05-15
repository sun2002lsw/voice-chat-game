export type ScenarioSummary = {
  name: string;
  profile_url: string;
};

export type DialogEntry = {
  role: "character" | "user";
  text: string;
  created_at: string;
};

export type StateLogEntry = {
  step_name: string;
  visit_count: number;
  conditions: string[];
  next_step_names: string[];
  character_script: string;
  user_input: string;
  llm_index: number | null;
};

export type SessionState = {
  scenario_name: string;
  current_step_name: string;
  current_visit_count: number;
  is_terminal: boolean;
  profile_url: string;
  picture_url: string;
  voice_url: string;
  dialog: DialogEntry[];
  state_log: StateLogEntry[];
};
