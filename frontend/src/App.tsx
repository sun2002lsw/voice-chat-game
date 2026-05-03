import { Route, Routes } from "react-router-dom";

import { Lobby } from "./pages/Lobby";
import { Play } from "./pages/Play";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Lobby />} />
      <Route path="/play/:name" element={<Play />} />
    </Routes>
  );
}
