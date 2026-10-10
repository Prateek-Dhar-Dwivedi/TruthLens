import { useState } from "react";
import api from "../api";
import "./Register.css";
import { Link } from "react-router-dom";
import Swal from "sweetalert2";

function Register({setShowLogin}){

    const [name,setName]=useState("");
    const [email,setEmail]=useState("");
    const [password,setPassword]=useState("");
    const [message,setMessage]=useState("");

    const handleRegister=async(e)=>{
        e.preventDefault();

        try{

            const res=await api.post(
                "/register",
                {
                    name,
                    email,
                    password
                }
            );


            if(res.data.error){
                setMessage(res.data.error);

                Swal.fire({
                    icon: "error",
                    title: "Registration Failed",
                    text: res.data.error,
                    confirmButtonColor: "#14B8A6"
                });

                return;
            }


            setMessage(
                "Registration successful"
            );

            await Swal.fire({
                icon: "success",
                title: "Registration Successful!",
                text: "Your TruthLens account has been created. Redirecting to login...",
                confirmButtonColor: "#14B8A6",
                timer: 2000,
                showConfirmButton: false
            });

            setName("");
            setEmail("");
            setPassword("");

            setShowLogin(true);

        }
        catch(err){

            const errText = err.response?.data?.error || "Registration failed. Please try again.";
            setMessage(errText);

            Swal.fire({
                icon: "error",
                title: "Registration Failed",
                text: errText,
                confirmButtonColor: "#14B8A6"
            });

        }
    };


    return(
        <div className="register-page">

            <div className="register-card">

                <h1>Create Account</h1>

                <p>
                    Join TruthLens AI and verify information smarter
                </p>


                <form onSubmit={handleRegister}>

                    <input
                        type="text"
                        placeholder="Full Name"
                        value={name}
                        onChange={(e)=>setName(e.target.value)}
                        required
                    />


                    <input
                        type="email"
                        placeholder="Email Address"
                        value={email}
                        onChange={(e)=>setEmail(e.target.value)}
                        required
                    />


                    <input
                        type="password"
                        placeholder="Create Password"
                        value={password}
                        onChange={(e)=>setPassword(e.target.value)}
                        required
                    />


                    <button type="submit">
                        Register
                    </button>

                </form>


                {
                    message && (
                        <p className="message">
                            {message}
                        </p>
                    )
                }


                <div className="register-footer">

                    Already have an account?{" "}

                    <Link
                        to="#"
                        onClick={(e)=>{
                            e.preventDefault();
                            setShowLogin(true);
                        }}
                    >
                        Login
                    </Link>

                </div>


            </div>

        </div>
    );
}

export default Register;