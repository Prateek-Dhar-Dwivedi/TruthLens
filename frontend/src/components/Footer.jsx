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
            <h3>
              Platform
            </h3>

            <Link href="/">
              Fact Check
            </Link>

            <Link href="/history">
              History
            </Link>

            <Link href="/dashboard">
              Dashboard
            </Link>

          </div>


          <div>
            <h3>
              Resources
            </h3>

            <Link href="#">
              About
            </Link>

            <Link href="#">
              Home
            </Link>

            <Link href="https://prateek-dhar-dwivedi.github.io/-Portfolio/">
              Contact
            </Link>

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
