import './App.css'

import { BrowserRouter, Routes, Route } from "react-router-dom";
import Homepage from "./pages/Homepage.tsx";
import Train from "./pages/Train.tsx";


const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Homepage />} />
      <Route path="train" element={<Train />} />
    </Routes>
  </BrowserRouter>
);

export default App;
