import "./Footer.css";

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

            <a href="/">
              Fact Check
            </a>

            <a href="/history">
              History
            </a>

            <a href="/dashboard">
              Dashboard
            </a>

          </div>


          <div>
            <h3>
              Resources
            </h3>

            <a href="#">
              About
            </a>

            <a href="#">
              Privacy
            </a>

            <a href="#">
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