/**
 * TerraSpectra root application component.
 *
 * Renders the top-level layout: header, sidebar, 3D GIS map, analytics panel,
 * and timeline slider. Actual map/panel content is lazy-loaded.
 */
function App(): JSX.Element {
  return (
    <div className="app-root" style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <header style={{ padding: "0.5rem 1rem", background: "#1a1a2e", color: "#eee" }}>
        <h1 style={{ margin: 0, fontSize: "1.2rem" }}>🌿 TerraSpectra</h1>
      </header>
      <main style={{ flex: 1, display: "flex" }}>
        <div style={{ flex: 1, background: "#0f3460", display: "flex", alignItems: "center", justifyContent: "center", color: "#eee" }}>
          Map placeholder — Deck.gl + Mapbox
        </div>
      </main>
    </div>
  );
}

export default App;
