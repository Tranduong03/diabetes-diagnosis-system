import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "../pages";
// import Diagnosis from "../pages/Diagnosis";
// import Tracking from "../pages/Tracking";
// import Explanation from "../pages/Explanation";
// import About from "../pages/About";
// import Navbar from "../components/Navbar";

export default function AppRouter() {
  return (
    <BrowserRouter>
      {/* <Navbar /> */}
      <Routes>
        <Route path="/" element={<Home />} />
        {/* <Route path="/diagnosis" element={<Diagnosis />} /> */}
        {/* <Route path="/tracking" element={<Tracking />} /> */}
        {/* <Route path="/explanation" element={<Explanation />} /> */}
        {/* <Route path="/about" element={<About />} /> */}
      </Routes>
    </BrowserRouter>
  );
}
