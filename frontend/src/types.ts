export type ScenarioSummary = {
  name: string;
  profile_url: string;
  first_step_name: string;
};

export type StepInfo = {
  step_name: string;
  is_terminal: boolean;
  loop: boolean;
  picture_url: string;
  scripts: string[];
  voice_urls: string[];
  conditions: string[];
  next_step_names: string[];
};
