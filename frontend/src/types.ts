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
  conditions: string[];
  next_step_names: string[];
  character_script: string;
  selected_index: number | null;
};

export type SessionState = {
  scenario_name: string;
  current_step_name: string;
  is_terminal: boolean;
  profile_url: string;
  picture_url: string;
  scripts: string[];
  voice_urls: string[];
  dialog: DialogEntry[];
  state_log: StateLogEntry[];
};
