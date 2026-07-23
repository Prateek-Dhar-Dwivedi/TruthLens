import { useEffect, useState } from "react";
import api from "../api";
import "./SavedChecks.css";
import { Link } from "react-router-dom";

function SavedChecks() {

    const [data, setData] = useState([]);
    const token = localStorage.getItem("token");

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {

        const res = await api.get(
            "/saved-checks",
            {
                headers: {
                    Authorization:
                        localStorage.getItem("token")
                }
            }
        );

        setData(res.data);

    };

    if (!token) {

        return (

            <div className="saved-page">

                <div className="saved-login-card">

                    <h1>🔒 Login Required</h1>

                    <p>
                        Please login first to access your saved fact checks.
                    </p>

                    <Link
                        to="/login"
                        className="login-required-btn"
                    >
                        Login Now
                    </Link>

                </div>

            </div>

        );

    }

    return (
        <div className="saved-page">

            <div className="saved-container">

                <h1>Saved Checks</h1>

                {data.length === 0 ? (

                    <div className="empty-state">
                        No saved checks yet.
                    </div>

                ) : (

                    data.map(item => (

                        <div
                            key={item.id}
                            className="saved-card"
                        >

                            <h3>{item.claim}</h3>

                            <div
                                className={`saved-verdict ${item.verdict === "Likely True"
                                        ? "true"
                                        : item.verdict === "Likely False"
                                            ? "false"
                                            : "uncertain"
                                    }`}
                            >
                                {item.verdict}
                            </div>

                            <p>
                                Confidence: {item.confidence}%
                            </p>

                        </div>

                    ))

                )}

            </div>

        </div>
    );

}

export default SavedChecks;