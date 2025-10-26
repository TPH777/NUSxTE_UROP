import './App.css'

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { StageProvider } from "./context/stageContext.tsx";
import Homepage from "./pages/Homepage.tsx";
import Train from "./pages/Train.tsx";


const App: React.FC = () => (
  <StageProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="train" element={<Train />} />
      </Routes>
    </BrowserRouter>
  </StageProvider>
);

export default App;
