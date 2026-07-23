import { useState } from "react";
import axios from "axios";
import "./FactCheck.css";
import api from "../api";
import { API_URL } from "../config/config";
import Swal from "sweetalert2";

function FactCheck() {
  const [claim, setClaim] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const saveCheck = async () => {

    const token = localStorage.getItem("token");

    if (!token) {

      Swal.fire({
        icon: "warning",
        title: "Login Required",
        text: "Please login first to use this feature.",
        confirmButtonColor: "#14B8A6"
      });

      return;

    }

    try {

      await api.post(
        "/save-check",
        {
          claim: result.claim,
          verdict: result.verdict,
          confidence: result.confidence,
          token
        }
      );

      Swal.fire({
        icon: "success",
        title: "Saved!",
        text: "Fact check saved successfully.",
        confirmButtonColor: "#14B8A6"
      });

    } catch (err) {

      console.log(err);

      Swal.fire({
        icon: "warning",
        title: "Process Failed",
        text: "Failed to save the Fact",
        confirmButtonColor: "#14B8A6"
      });

    }

  };

  const checkClaim = async () => {
    if (!claim.trim()) return;

    try {
      setLoading(true);

      const res = await axios.post(
        `${API_URL}/fact-check`,
        {
          claim,
          token: localStorage.getItem("token")
        }
      );

      setResult(res.data);
    } catch (error) {
      console.error(error);

      Swal.fire({
        icon: "warning",
        title: "Process Failed",
        text: "Failed to verify claim",
        confirmButtonColor: "#14B8A6"

      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fact-page">
      <div className="fact-container">

        <h1>TruthLens AI</h1>

        <p className="subtitle">
          Verify news claims using AI-powered fact checking
        </p>

        <textarea
          placeholder="Enter a claim..."
          value={claim}
          onChange={(e) => setClaim(e.target.value)}
        />

        <div className="action-buttons">

          <button
            className="fact-btn"
            onClick={checkClaim}
          >
            {loading ? "Analyzing..." : "Verify Claim"}
          </button>

          {result && (

            <button
              className="save-btn"
              onClick={saveCheck}
            >
              ⭐ Save Check
            </button>

          )}


        </div>

        {result && (
          <div className="result-card">

            <h2>{result.verdict}</h2>

            <div className="confidence">
              Confidence: {result.confidence}%
            </div>

            <div className="stats">
              <span>✅ Support: {result.supports}</span>
              <span>❌ Contradict: {result.contradicts}</span>
              <span>⚪ Neutral: {result.neutral}</span>
            </div>

            <h3>Evidence Sources</h3>

            {result.analysis?.map((item, index) => (
              <div
                key={index}
                className="source-card"
              >

                <h4>{item.title}</h4>

                <p>
                  <strong>
                    {item.label}
                  </strong>
                </p>

                <p>
                  Match Score:
                  {item.score}
                </p>

                <p>
                  Credibility:
                  {item.credibility}/100
                </p>

                <span
                  className={`credibility-badge ${item.credibility_label
                    ?.toLowerCase()
                    .replace(" ", "-")
                    }`}
                >
                  {item.credibility_label}
                </span>

                <br />

                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Read Source
                </a>

              </div>
            ))}

          </div>
        )}

      </div>
    </div>
  );
}

export default FactCheck;