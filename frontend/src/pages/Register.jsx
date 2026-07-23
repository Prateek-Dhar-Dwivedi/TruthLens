import { useState } from "react";
import api from "../api";
import "./Register.css";
import { Link } from "react-router-dom";

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
                return;
            }


            setMessage(
                "Registration successful"
            );


            setName("");
            setEmail("");
            setPassword("");


            setTimeout(()=>{
                setShowLogin(true);
            },1000);


        }
        catch(err){

            setMessage(
                err.response?.data?.error ||
                "Registration failed"
            );

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