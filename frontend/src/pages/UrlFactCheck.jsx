import { useState } from "react";
import api from "../api";
import "./UrlFactCheck.css";
import { downloadReport } from "../utils/downloadReport";
import Swal from "sweetalert2";

function UrlFactCheck() {

    const [url, setUrl] = useState("");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const checkUrl = async () => {

        if (!url.trim()) {

            Swal.fire({
                icon: "warning",
                title: "URL Required",
                text: "Please enter a URL",
                confirmButtonColor: "#14B8A6"
            });
            return;
        }

        try {

            setLoading(true);
            setResult(null);

            const res = await api.post(
                "/fact-check-url",
                { url }
            );

            setResult(res.data);

        } catch (err) {

            console.log(err);

            Swal.fire({
                icon: "warning",
                title: "Process Failed",
                text: "Failed to analyze URL",
                confirmButtonColor: "#14B8A6"
            });

        } finally {

            setLoading(false);

        }

    };

    return (
        <div className="url-page">

            <div className="url-card">

                <h1>URL Fact Checker</h1>

                <p>
                    Paste a news article URL and let TruthLens verify it.
                </p>

                <input
                    className="url-input"
                    type="text"
                    placeholder="Paste article URL..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                />

                <button
                    className="url-btn"
                    onClick={checkUrl}
                    disabled={loading}
                >
                    {loading ? "Analyzing..." : "Analyze URL"}
                </button>

                {loading && (
                    <div className="loading-box">

                        <div className="loader"></div>

                        <h3>Analyzing Article...</h3>

                        <p>
                            Extracting content, checking sources and verifying claims.
                        </p>

                    </div>
                )}

                {result && (

                    <div className="result-card">

                        <h2>{result.article_title}</h2>

                        <div
                            className={`verdict ${result.verdict === "Likely True"
                                ? "true"
                                : result.verdict === "Likely False"
                                    ? "false"
                                    : "uncertain"
                                }`}
                        >
                            {result.verdict}
                        </div>

                        <div className="overall-confidence">
                            Confidence: {result.confidence ?? 0}%
                        </div>

                        <div className="stats">

                            <div>
                                Supports: {result.supports}
                            </div>

                            <div>
                                Contradicts: {result.contradicts}
                            </div>

                            <div>
                                Neutral: {result.neutral}
                            </div>

                        </div>

                        <div className="report-section">

                            <h3>Export Report</h3>

                            <p>
                                Download a professional PDF report containing the verdict,
                                confidence metrics, and supporting evidence.
                            </p>

                            <button
                                className="pdf-btn"
                                onClick={() => downloadReport(result)}
                            >
                                📄 Download PDF Report
                            </button>

                        </div>

                        {result.article_preview && (
                            <>

                                <h3 style={{ marginBottom: "12px" }}>
                                    Article Preview
                                </h3>

                                <div className="article-preview">
                                    {result.article_preview}
                                </div>

                            </>
                        )}

                        {result.analysis?.length > 0 && (
                            <>

                                <h3>Evidence Sources</h3>

                                {result.analysis.map((item, index) => (
                                    <div
                                        key={index}
                                        className="source-card"
                                    >

                                        <h4>
                                            #{index + 1} {item.title}
                                        </h4>

                                        <p className="source-label">
                                            {item.label}
                                        </p>

                                        <p>
                                            AI Confidence: {(item.score * 100).toFixed(1)}%
                                        </p>

                                        <div
                                            className={`credibility-badge ${item.credibility_label
                                                ?.toLowerCase()
                                                .replace(" ", "-")
                                                }`}
                                        >
                                            ⭐ {item.credibility_label}
                                            ({item.credibility}/100)
                                        </div>

                                        <a
                                            href={item.url}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            🔗 Read Source
                                        </a>

                                    </div>
                                ))}

                            </>
                        )}

                    </div>

                )}

            </div>

        </div>
    );

}

export default UrlFactCheck;