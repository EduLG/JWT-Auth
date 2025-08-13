import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { Context } from "../store/appContext";

const Signup = () => {
    const { store, actions } = useContext(Context);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const success = await actions.signup(email, password);
        if (success) {
            navigate("/login");
        } else {
            alert("Error al registrarse. El email podría ya estar en uso.");
        }
    };

    return (
        <div className="signup-container">
            <h2>Registro</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit">Registrarme</button>
            </form>
        </div>
    );
};

export default Signup;