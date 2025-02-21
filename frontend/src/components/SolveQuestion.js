import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { solveQuestion, downloadExcel } from "../services/api";
import "./SolveQuestion.css";

const SolveQuestion = () => {
    const [question, setQuestion] = useState("");
    const [response, setResponse] = useState("");
    const [displayedText, setDisplayedText] = useState(""); // ✅ Used for typing effect
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        if (response) {
            setDisplayedText(""); // Reset displayed text
            let index = 0;
            const interval = setInterval(() => {
                if (index < response.length) {
                    setDisplayedText((prev) => prev + response[index]);
                    index++;
                } else {
                    clearInterval(interval);
                }
            }, 10); // Typing speed
            return () => clearInterval(interval);
        }
    }, [response]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setResponse("");
        setDisplayedText(""); // Reset typing effect

        if (!question.trim()) {
            setError("Please enter a LeetCode question.");
            setLoading(false);
            return;
        }

        const result = await solveQuestion(question);

        if (result.error) {
            setError(result.error);
        } else {
            setResponse(result.response);
        }

        setLoading(false);
    };

    return (
        <div className="container">
            <h2>ABSTRACT - Your LeetCode AI Assistant</h2>

            <form onSubmit={handleSubmit} className="question-form">
                <div className="input-container">
                    <input
                        type="text"
                        placeholder="Enter a LeetCode question..."
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        required
                        className="question-input"
                        disabled={loading}
                    />
                    <button type="submit" disabled={loading} className="submit-button">
                        {loading ? "Solving..." : "Solve"}
                    </button>
                    <button className="download-button" onClick={downloadExcel} disabled={loading}>
                        {loading ? "Preparing..." : "Download Excel"}
                    </button>
                </div>


            </form>

            {error && <p className="error">{error}</p>}

            {response && (
                <div className="response-container">
                    <h3 className="response-title">AI Response:</h3>
                    <div className="response-text">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {displayedText}
                        </ReactMarkdown>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SolveQuestion;
