import './App.css'

import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index.tsx";


const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Index />} />
    </Routes>
  </BrowserRouter>
);

export default App;
