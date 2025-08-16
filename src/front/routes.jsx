import {
    createBrowserRouter,
    createRoutesFromElements,
    Route,
    Navigate // Importa el componente Navigate
} from "react-router-dom";
import { Layout } from "./pages/Layout";
import { Home } from "./pages/Home";
import { Single } from "./pages/Single";
import { Demo } from "./pages/Demo";

// Importa los nuevos componentes de autenticación
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Private from "./pages/Private";

export const router = createBrowserRouter(
    createRoutesFromElements(
      <Route path="/" element={<Layout />} errorElement={<h1>Not found!</h1>} >

        <Route index element={<Navigate to="/login" replace />} />

        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/private" element={<Private />} />

        <Route path= "/" element={<Home />} />
        <Route path="/single/:theId" element={ <Single />} />
        <Route path="/demo" element={<Demo />} />
      </Route>
    )
);