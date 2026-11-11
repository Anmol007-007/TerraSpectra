import React from "react";
import { AppLayout } from "./components/AppLayout";
import { MapContainer } from "./components/MapContainer";

export const App: React.FC = () => {
  return (
    <AppLayout>
      <MapContainer />
    </AppLayout>
  );
};

export default App;
