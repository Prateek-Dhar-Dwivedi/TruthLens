import { NavLink, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import "./Navbar.css";
import { useTheme } from "../context/ThemeContext";
import { FaSun, FaMoon } from "react-icons/fa";

function Navbar() {
    const { darkMode, toggleTheme } = useTheme();

    const navigate = useNavigate();

    const [token, setToken] = useState(
        localStorage.getItem("token")
    );

    const [showAccountMenu, setShowAccountMenu] = useState(false);

    useEffect(() => {

        const checkToken = () => {

            setToken(
                localStorage.getItem("token")
            );

        };

        checkToken();

        window.addEventListener(
            "storage",
            checkToken
        );

        return () => {

            window.removeEventListener(
                "storage",
                checkToken
            );

        };

    }, []);

    const handleLogout = () => {

        localStorage.removeItem("token");
        setToken(null);
        setShowAccountMenu(false);
        navigate("/auth");

    };

    return (
        <nav className="navbar">
            <NavLink
                to="/"
                className="logo"
            >
                <img src="/logo.png" alt="Logo" />
                TruthLens
            </NavLink>

            <div className="nav-links">

                <NavLink to="/">
                    Fact Check
                </NavLink>

                <NavLink to="/url-check">
                    URL Check
                </NavLink>

                <NavLink to="/assistant">
                    AI Assistant
                </NavLink>

                <NavLink to="/trending-news">
                    Trending News
                </NavLink>

                {token && (

                    <div className="account-menu">

                        <button
                            className="account-btn"
                            onClick={() =>
                                setShowAccountMenu(
                                    !showAccountMenu
                                )
                            }
                        >
                            👤 Account
                        </button>

                        {showAccountMenu && (

                            <div className="dropdown-menu">

                                <NavLink
                                    to="/dashboard"
                                    onClick={() =>
                                        setShowAccountMenu(false)
                                    }
                                >
                                    Dashboard
                                </NavLink>

                                <NavLink
                                    to="/history"
                                    onClick={() =>
                                        setShowAccountMenu(false)
                                    }
                                >
                                    History
                                </NavLink>

                                <NavLink
                                    to="/saved-checks"
                                    onClick={() =>
                                        setShowAccountMenu(false)
                                    }
                                >
                                    Saved Checks
                                </NavLink>

                                <button
                                    className="logout-dropdown"
                                    onClick={handleLogout}
                                >
                                    Logout
                                </button>

                            </div>

                        )}


                    </div>

                )}

                {!token && (

                    <NavLink to="/auth">
                        Login / Register
                    </NavLink>

                )}

            </div>
            <button className="theme-toggle" onClick={toggleTheme}>

                {
                    darkMode ? <FaSun /> : <FaMoon />
                }

            </button>

        </nav>
    );
}

export default Navbar; 