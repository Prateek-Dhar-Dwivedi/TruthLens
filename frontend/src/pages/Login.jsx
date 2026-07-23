import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import "./Login.css";
import Swal from "sweetalert2";

function Login({ setShowLogin }) {

    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleLogin = async (e) => {

        e.preventDefault();

        try {

            const res = await api.post(
                "/login",
                {
                    email,
                    password
                }
            );

            if (res.data.error) {

                setError(res.data.error);

                Swal.fire({
                    icon: "error",
                    title: "Login Failed",
                    text: res.data.error,
                    confirmButtonColor: "#14B8A6"
                });

                return;
            }

            localStorage.setItem(
                "token",
                res.data.token
            );

            await Swal.fire({
                icon: "success",
                title: "Login Successful",
                text: "Welcome back to TruthLens!",
                confirmButtonColor: "#14B8A6",
                timer: 1500,
                showConfirmButton: false
            });

            window.dispatchEvent(
                new Event("storage")
            );

            navigate("/");

        }
        catch (err) {

            const message =
                err.response?.data?.error ||
                "Invalid email or password";

            setError(message);

            Swal.fire({
                icon: "error",
                title: "Login Failed",
                text: message,
                confirmButtonColor: "#14B8A6"
            });

        }

    };

    return (

        <div className="login-page">

            <div className="login-card">

                <h1>Welcome Back</h1>

                <p>
                    Continue your journey of verifying truth with AI
                </p>

                {
                    error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )
                }

                <form onSubmit={handleLogin}>

                    <input
                        type="email"
                        placeholder="Enter your email"
                        value={email}
                        onChange={(e) =>
                            setEmail(e.target.value)
                        }
                    />

                    <input
                        type="password"
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) =>
                            setPassword(e.target.value)
                        }
                    />

                    <button type="submit">
                        Login
                    </button>

                </form>

                <div className="login-footer">

                    Don't have an account?{" "}

                    <Link
                        to="#"
                        onClick={(e) => {
                            e.preventDefault();
                            setShowLogin(false);
                        }}
                    >
                        Register
                    </Link>

                </div>

            </div>

        </div>

    );

}

export default Login;