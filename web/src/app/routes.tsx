import { createBrowserRouter, Navigate } from "react-router";
import { Layout } from "./components/Layout";
import { ApiPresets } from "./components/pages/ApiPresets";
import { ApiTesting } from "./components/pages/ApiTesting";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: ApiTesting },
      { path: "presets", Component: ApiPresets },
      { path: "*", Component: () => <Navigate to="/" replace /> },
    ],
  },
]);
