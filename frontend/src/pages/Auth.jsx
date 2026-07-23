import { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import "./Auth.css";

function Auth() {
  const [showLogin, setShowLogin] = useState(true);

  return (
    <div className="auth-container">
      {showLogin ? (
        <Login setShowLogin={setShowLogin} />
      ) : (
        <Register setShowLogin={setShowLogin} />
      )}
    </div>
  );
}

export default Auth;