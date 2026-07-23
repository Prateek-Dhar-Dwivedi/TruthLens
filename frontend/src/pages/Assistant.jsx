import { useState } from "react";
import api from "../api";
import "./Assistant.css";
import Swal from "sweetalert2";

function Assistant() {

    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState(null);
    const [loading, setLoading] = useState(false);

    const askQuestion = async () => {

        if (!question.trim()) {
            Swal.fire({
                icon: "warning",
                title: "Question Required",
                text: "Enter a question",
                confirmButtonColor: "#14B8A6"
            });
            return;
        }

        try {

            setLoading(true);
            setAnswer(null);

            const res = await api.post(
                "/ask",
                {
                    question,
                    token: localStorage.getItem("token")
                }
            );

            console.log(res.data);

            setAnswer(res.data);

        } catch (err) {

            console.log(err);
            Swal.fire({
                icon: "warning",
                title: "Process Failed",
                text: "Failed to process question",
                confirmButtonColor: "#14B8A6"
            });

        } finally {

            setLoading(false);

        }

    };

    return (
        <div className="assistant-page">

            <div className="assistant-card">

                <h1>TruthLens AI Assistant</h1>

                <p>
                    Ask any factual question and TruthLens will verify it using trusted news sources.
                </p>

                <textarea
                    className="assistant-input"
                    placeholder="Example: Did Apple sue OpenAI?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                />

                <button
                    className="assistant-btn"
                    onClick={askQuestion}
                    disabled={loading}
                >
                    {loading ? "Thinking..." : "Ask AI"}
                </button>

                {answer && (

                    <div className="assistant-result">

                        <h2>{answer.verdict}</h2>

                        <div className="assistant-confidence">
                            Confidence: {answer.confidence}%
                        </div>

                        <div className="assistant-stats">

                            <span>
                                Supports: {answer.supports}
                            </span>

                            <span>
                                Contradicts: {answer.contradicts}
                            </span>

                            <span>
                                Neutral: {answer.neutral}
                            </span>

                        </div>

                        {answer.explanation && (

                            <div className="assistant-summary">

                                <h3>AI Summary</h3>

                                {Array.isArray(answer.explanation) ? (

                                    answer.explanation.map((item, index) => (
                                        <p key={index}>{item}</p>
                                    ))

                                ) : (

                                    <p>{answer.explanation}</p>

                                )}

                            </div>

                        )}

                    </div>

                )}

            </div>

        </div>
    );

}

export default Assistant;