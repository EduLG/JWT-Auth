import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Context } from "../store/appContext";

const Private = () => {
    const { store, actions } = useContext(Context);
    const [message, setMessage] = useState("Cargando...");
    const navigate = useNavigate();

    useEffect(() => {
        const token = sessionStorage.getItem("jwt-token");
        if (!token) {
            // Si no hay token, redirigir al login
            navigate("/login");
        } else {
            // Si hay token, llamar al backend para obtener el mensaje privado
            actions.getPrivateMessage();
        }
    }, [navigate]); // navigate se incluye como dependencia para evitar warnings

    return (
        <div className="private-container">
            <h2>Página Privada</h2>
            <p>{store.message}</p>
            <button onClick={() => actions.logout(navigate)}>Cerrar Sesión</button>
        </div>
    );
};

export default Private;