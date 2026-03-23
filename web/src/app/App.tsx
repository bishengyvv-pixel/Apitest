import { RouterProvider } from "react-router";
import { router } from "./routes";
import { ApiProvider } from "./context/ApiContext";
import { Toaster } from "sonner";

export default function App() {
  return (
    <ApiProvider>
      <Toaster position="top-center" richColors />
      <RouterProvider router={router} />
    </ApiProvider>
  );
}
