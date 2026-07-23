import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Navbar from "./components/Navbar";
import Auth from "./pages/Auth";
import FactCheck from "./pages/FactCheck";
import History from "./pages/History";
import Dashboard from "./pages/Dashboard";
import Footer from "./components/Footer";
import UrlFactCheck from "./pages/UrlFactCheck";
import Assistant from "./pages/Assistant";
import TrendingNews from "./pages/TrendingNews";
import SavedChecks from "./pages/SavedChecks";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<FactCheck />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/history" element={<History />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route
          path="/url-check"
          element={<UrlFactCheck />}
        />
        <Route
          path="/assistant"
          element={<Assistant />}
        />
        <Route
          path="/trending-news"
          element={<TrendingNews />}
        />
        <Route
          path="/saved-checks"
          element={<SavedChecks />}
        />
      </Routes>

      <Footer />
    </BrowserRouter>
  );
}

export default App;