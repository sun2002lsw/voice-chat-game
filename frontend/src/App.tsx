import { Route, Routes } from "react-router-dom";

import { Lobby } from "./features/lobby/Lobby";
import { Play } from "./features/play/Play";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Lobby />} />
      <Route path="/play/:name" element={<Play />} />
    </Routes>
  );
}
