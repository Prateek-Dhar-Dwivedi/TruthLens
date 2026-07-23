import { useEffect, useState } from "react";
import api from "../api";
import "./TrendingNews.css";

function TrendingNews() {

    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [checking, setChecking] = useState(null);
    const [results, setResults] = useState({});

    useEffect(() => {
        fetchNews();
    }, []);

    const fetchNews = async () => {

        try {

            const res = await api.get("/trending-news");

            setNews(res.data);

        } catch (err) {

            console.log(err);

        } finally {

            setLoading(false);

        }

    };

    const verifyNews = async (title, index) => {

        try {

            setChecking(index);

            const res = await api.post(
                "/fact-check",
                {
                    claim: title,
                    token: localStorage.getItem("token")
                }
            );

            setResults(prev => ({
                ...prev,
                [index]: res.data
            }));

        } catch (err) {

            console.log(err);

        } finally {

            setChecking(null);

        }

    };

    if (loading) {

        return (
            <div className="trending-page">
                <h1>Loading News...</h1>
            </div>
        );

    }

    return (
        <div className="trending-page">

            <h1>🔥 Trending News</h1>

            <p>
                Latest headlines verified by TruthLens.
            </p>

            <div className="news-grid">

                {news.map((item, index) => (

                    <div
                        key={index}
                        className="news-card"
                    >

                        <h3>{item.title}</h3>

                        <span>
                            {item.source}
                        </span>

                        <div className="news-actions">

                            <a
                                href={item.url}
                                target="_blank"
                                rel="noreferrer"
                            >
                                Read Article
                            </a>

                            <button
                                onClick={() => verifyNews(item.title, index)}
                                disabled={checking === index}
                            >
                                {checking === index
                                    ? "Verifying..."
                                    : "Verify"}
                            </button>

                        </div>

                        {results[index] && (

                            <div className="verify-result">

                                <div className={`trend-verdict ${results[index].verdict === "Likely True"
                                        ? "trend-true"
                                        : results[index].verdict === "Likely False"
                                            ? "trend-false"
                                            : "trend-uncertain"
                                    }`}>
                                    {results[index].verdict}
                                </div>

                                <p>
                                    Confidence: {results[index].confidence}%
                                </p>

                                <p>
                                    Supports: {results[index].supports}
                                </p>

                                <p>
                                    Contradicts: {results[index].contradicts}
                                </p>

                                <p>
                                    Neutral: {results[index].neutral}
                                </p>

                                <h4>
                                    Evidence Sources ({results[index].analysis?.length || 0})
                                </h4>

                                {results[index].analysis?.slice(0, 3).map((source, i) => (

                                    <div
                                        key={i}
                                        className="evidence-item"
                                    >

                                        <p className="evidence-title">
                                            #{i + 1} {source.title}
                                        </p>

                                        <p className="evidence-label">
                                            {source.label}
                                        </p>

                                        <a
                                            href={source.url}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            🔗 Read Source
                                        </a>

                                    </div>

                                ))}

                            </div>

                        )}

                    </div>

                ))}

            </div>

        </div>
    );

}

export default TrendingNews;