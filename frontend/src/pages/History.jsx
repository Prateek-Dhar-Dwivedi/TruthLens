import { useEffect, useState } from "react";
import api from "../api";
import "./History.css";

function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem("token");

      const res = await api.get("/my-history", {
        headers: {
          Authorization: token
        }
      });

      console.log(res.data);

      if (Array.isArray(res.data)) {
        setHistory(res.data);
      } else {
        setHistory([]);
      }
    } catch (err) {
      console.log(err);
      setHistory([]);
    }
  };

  const deleteHistory = async (id) => {
    try {
      await api.delete(`/history/${id}`);

      setHistory(
        history.filter(
          item => item.id !== id
        )
      );
    } catch (err) {
      console.log(err);
    }
  };

  const clearHistory = async () => {
    try {
      await api.delete("/history");
      setHistory([]);
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="history-page">
      <h1>Fact Check History</h1>

      <button
        className="clear-btn"
        onClick={clearHistory}
      >
        Clear All History
      </button>

      <div className="history-grid">
        {!Array.isArray(history) || history.length === 0 ? (
          <div className="empty-card">
            <h3>No History Found</h3>
          </div>
        ) : (
          history.map((item, index) => (
            <div
              key={index}
              className="history-card"
            >
              <h3>{item.claim}</h3>

              <div
                className={`verdict ${
                  item.verdict === "Likely True"
                    ? "true"
                    : item.verdict === "Likely False"
                    ? "false"
                    : "uncertain"
                }`}
              >
                {item.verdict}
              </div>

              <p>
                Confidence:
                <span> {item.confidence}%</span>
              </p>

              <button
                className="delete-btn"
                onClick={() => deleteHistory(item.id)}
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default History;