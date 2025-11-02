import './App.css'

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueueProvider } from './context/QueueContext.tsx';
import { StageProvider } from "./context/StageContext.tsx";
import Homepage from "./pages/Homepage.tsx";
import Train from "./pages/Train.tsx";


const App: React.FC = () => (
  <StageProvider>
  <QueueProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="train" element={<Train />} />
      </Routes>
    </BrowserRouter>
  </QueueProvider>
  </StageProvider>
);

export default App;
