import React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./api/queryClient";
import { AppLayout } from "./components/AppLayout";
import { MapContainer } from "./components/MapContainer";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ToastContainer } from "./components/Toast";

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <AppLayout>
          <MapContainer />
          <ToastContainer />
        </AppLayout>
      </ErrorBoundary>
    </QueryClientProvider>
  );
};

export default App;
