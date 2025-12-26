export const Modal = ({
  selectedRow,
  onClose,
}: {
  selectedRow: any;
  onClose: () => void;
}) => {
  return (
    <>
      {/* Backdrop to dim the background */}
      <div
        onClick={() => onClose()}
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          background: "rgba(0,0,0,0.5)",
          zIndex: 999,
        }}
      />

      {/* The Actual Modal */}
      <div
        style={{
          position: "fixed",
          top: "10vh",
          left: "10vw",
          width: "80vw",
          height: "80vh",
          backgroundColor: "var(--surface)",
          color: "var(--text)",
          borderRadius: "12px",
          padding: "24px",
          zIndex: 1000,
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <a
            href={selectedRow.url}
            style={{ textDecoration: "none", color: "var(--accent)" }}
          >
            <h2>{selectedRow.name}</h2>
          </a>
          <button
            onClick={() => onClose()}
            style={{
              cursor: "pointer",
              background: "var(--accent)",
              color: "white",
              border: "none",
              padding: "8px 16px",
              borderRadius: "4px",
            }}
          >
            Close
          </button>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1rem",
          }}
        >
          <div
            style={{
              overflowX: "auto",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div
              style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr" }}
            >
              <h2>
                Ask:{" "}
                <span style={{ fontWeight: "bold", color: "var(--accent)" }}>
                  {selectedRow.price}
                </span>
              </h2>
              <h2>
                Predicted:{" "}
                <span style={{ fontWeight: "bold", color: "var(--accent)" }}>
                  {selectedRow.price_predicted}
                </span>
              </h2>
              <h2>
                Diff:{" "}
                <span style={{ fontWeight: "bold", color: "var(--accent)" }}>
                  {selectedRow.price_difference}
                </span>
              </h2>
            </div>
            <h3>{selectedRow.category}</h3>
            <p>{selectedRow.description}</p>
          </div>
          <img
            src={selectedRow.image}
            alt={selectedRow.name}
            width={500}
            height={500}
          />
        </div>
      </div>
    </>
  );
};
