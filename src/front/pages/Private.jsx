import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Private = () => {
    const [message, setMessage] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const token = sessionStorage.getItem("jwt-token");

        if (!token) {
            navigate("/login");
            return;
        }

        const fetchPrivateData = async () => {
            const response = await fetch("http://localhost:5000/private", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setMessage(data.msg);
            } else {
                sessionStorage.removeItem("jwt-token");
                navigate("/login");
            }
        };

        fetchPrivateData();
    }, [navigate]);

    return (
        <div className="text-center mt-5">
            {message ? (
                <>
                    <h1>{message}</h1>
                    <p>
                        ¡Has accedido a la página privada con éxito! 🎉
                    </p>
                </>
            ) : (
                <p>Cargando datos privados...</p>
            )}
        </div>
    );
};

export default Private;