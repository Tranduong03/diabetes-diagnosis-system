import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import Diagnosis from "../pages/Diagnosis";
import Tracking from "../pages/Tracking";
import Explanation from "../pages/Explanation";
import About from "../pages/About";
import Navbar from "../components/Navbar";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/diagnosis" element={<Diagnosis />} />
        <Route path="/tracking" element={<Tracking />} />
        <Route path="/explanation" element={<Explanation />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}
