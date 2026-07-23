import "./Footer.css";
import { Link } from "react-router-dom";

function Footer() {

  return (
    <footer className="footer">

      <div className="footer-container">

        <div className="footer-brand">
          <div className="footer-b">
            <img src="/logo.png" alt="TruthLens AI Logo" />
            <span>TruthLens AI</span>
          </div>

          <p>
            AI-powered fact verification platform
            helping you discover reliable information.
          </p>
        </div>


        <div className="footer-links">

          <div>
            <h3>Platform</h3>

            <Link to="/">
              Fact Check
            </Link>

            <Link to="/history">
              History
            </Link>

            <Link to="/dashboard">
              Dashboard
            </Link>

          </div>


          <div>
            <h3>Resources</h3>

            <Link to="/about">
              About
            </Link>

            <Link to="/">
              Home
            </Link>

            <a 
              href="https://prateek-dhar-dwivedi.github.io/-Portfolio/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Contact
            </a>

          </div>

        </div>

      </div>


      <div className="footer-bottom">

        © {new Date().getFullYear()} TruthLens.
        All rights reserved.

      </div>

    </footer>
  );
}

export default Footer;
