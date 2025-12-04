// frontend/src/App.jsx
import { useEffect, useState } from "react";
import api from "./api";

function App() {
  const [page, setPage] = useState("login"); // "login" | "register" | "dashboard"
  const [user, setUser] = useState(null);

  // state login
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState("");

  // state register
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regError, setRegError] = useState("");
  const [regSuccess, setRegSuccess] = useState("");

  // dashboard state
  const [credits, setCredits] = useState(null);
  const [files, setFiles] = useState([]);
  const [loadingFiles, setLoadingFiles] = useState(false);

  // register file
  const [regFile, setRegFile] = useState(null);
  const [regMetadata, setRegMetadata] = useState("");
  const [regResult, setRegResult] = useState(null);
  const [regLoading, setRegLoading] = useState(false);
  const [regErr, setRegErr] = useState("");

  // verify file
  const [verFile, setVerFile] = useState(null);
  const [verResult, setVerResult] = useState(null);
  const [verLoading, setVerLoading] = useState(false);
  const [verErr, setVerErr] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchMe();
      setPage("dashboard");
    }
  }, []);

  async function fetchMe() {
    try {
      const res = await api.get("/me");
      setUser(res.data);
      setCredits(res.data.credits);
      await fetchFiles();
    } catch (e) {
      console.error(e);
      localStorage.removeItem("access_token");
      setUser(null);
      setPage("login");
    }
  }

  async function fetchFiles() {
    setLoadingFiles(true);
    try {
      const res = await api.get("/files");
      setFiles(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingFiles(false);
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    setLoginError("");

    const data = new URLSearchParams();
    data.append("username", loginEmail);
    data.append("password", loginPassword);

    try {
      const res = await api.post("/auth/login", data, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      localStorage.setItem("access_token", res.data.access_token);
      await fetchMe();
      setPage("dashboard");
    } catch (e) {
      console.error(e);
      setLoginError(
        e.response?.data?.detail || "Login failed. Check email/password."
      );
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    setRegError("");
    setRegSuccess("");

    try {
      await api.post("/auth/register", {
        email: regEmail,
        password: regPassword,
      });
      setRegSuccess("Account created. You can now login.");
      setPage("login");
      setLoginEmail(regEmail);
    } catch (e) {
      console.error(e);
      setRegError(e.response?.data?.detail || "Failed to register.");
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    setUser(null);
    setFiles([]);
    setCredits(null);
    setPage("login");
  }

  async function handleRegisterFile(e) {
    e.preventDefault();
    setRegErr("");
    setRegResult(null);

    if (!regFile) {
      setRegErr("Please choose a file.");
      return;
    }

    setRegLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", regFile);
      formData.append("metadata", regMetadata);

      const res = await api.post("/files/register", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setRegResult(res.data);
      setCredits((prev) => (prev != null ? prev - 1 : prev));
      await fetchFiles();
    } catch (e) {
      console.error(e);
      setRegErr(
        e.response?.data?.detail ||
          "Failed to register file. Maybe no credits or blockchain error."
      );
    } finally {
      setRegLoading(false);
    }
  }

  async function handleVerifyFile(e) {
    e.preventDefault();
    setVerErr("");
    setVerResult(null);

    if (!verFile) {
      setVerErr("Please choose a file.");
      return;
    }

    setVerLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", verFile);

      const res = await api.post("/files/verify", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setVerResult(res.data);
    } catch (e) {
      console.error(e);
      setVerErr(
        e.response?.data?.detail || "Failed to verify file. Blockchain error."
      );
    } finally {
      setVerLoading(false);
    }
  }

  // ================= RENDER =================

  // === Login page ===
  if (page === "login") {
    return (
      <div style={{ maxWidth: 420, margin: "40px auto", fontFamily: "system-ui" }}>
        <h2>Login</h2>
        <form onSubmit={handleLogin} style={{ display: "grid", gap: "0.5rem" }}>
          <label>
            Email
            <input
              type="email"
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
              required
              style={{ width: "100%" }}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              required
              style={{ width: "100%" }}
            />
          </label>
          {loginError && <p style={{ color: "red" }}>{loginError}</p>}
          <button type="submit">Login</button>
        </form>

        <p style={{ marginTop: "1rem" }}>
          No account?{" "}
          <button type="button" onClick={() => setPage("register")}>
            Register here
          </button>
        </p>
      </div>
    );
  }

  // === Register page ===
  if (page === "register") {
    return (
      <div style={{ maxWidth: 420, margin: "40px auto", fontFamily: "system-ui" }}>
        <h2>Register</h2>
        <form onSubmit={handleRegister} style={{ display: "grid", gap: "0.5rem" }}>
          <label>
            Email
            <input
              type="email"
              value={regEmail}
              onChange={(e) => setRegEmail(e.target.value)}
              required
              style={{ width: "100%" }}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={regPassword}
              onChange={(e) => setRegPassword(e.target.value)}
              required
              style={{ width: "100%" }}
            />
          </label>
          {regError && <p style={{ color: "red" }}>{regError}</p>}
          {regSuccess && <p style={{ color: "green" }}>{regSuccess}</p>}
          <button type="submit">Create account</button>
        </form>

        <p style={{ marginTop: "1rem" }}>
          Already have an account?{" "}
          <button type="button" onClick={() => setPage("login")}>
            Back to login
          </button>
        </p>
      </div>
    );
  }

  // === Dashboard ===
  return (
    <div style={{ maxWidth: 1100, margin: "20px auto", fontFamily: "system-ui" }}>
      <header style={{ display: "flex", justifyContent: "space-between", marginBottom: "1rem" }}>
        <div>
          <h2>🔐 Blockchain File Integrity Registry</h2>
          {user && (
            <p>
              Logged in as <strong>{user.email}</strong> — Credits:{" "}
              <strong>{credits}</strong>
            </p>
          )}
        </div>
        <button onClick={handleLogout}>Logout</button>
      </header>

      <div style={{ display: "flex", gap: "2rem", alignItems: "flex-start" }}>
        {/* LEFT: Register & Verify */}
        <div style={{ flex: 1 }}>
          <section style={{ marginBottom: "2rem" }}>
            <h3>Register File</h3>
            <form onSubmit={handleRegisterFile} style={{ display: "grid", gap: "0.5rem" }}>
              <label>
                File
                <input
                  type="file"
                  onChange={(e) => setRegFile(e.target.files?.[0] || null)}
                />
              </label>
              <label>
                Metadata (optional)
                <input
                  type="text"
                  value={regMetadata}
                  onChange={(e) => setRegMetadata(e.target.value)}
                  placeholder="Example: contract v1.0"
                  style={{ width: "100%" }}
                />
              </label>
              {regErr && <p style={{ color: "red" }}>{regErr}</p>}
              <button type="submit" disabled={regLoading || credits <= 0}>
                {regLoading ? "Registering..." : "Register on Blockchain"}
              </button>
              {credits <= 0 && (
                <p style={{ color: "orange" }}>
                  No credits left. Implement top-up/payment flow later.
                </p>
              )}
            </form>
            {regResult && (
              <div style={{ marginTop: "1rem" }}>
                <h4>Registered:</h4>
                <p>Filename: {regResult.filename}</p>
                <p>Hash: {regResult.file_hash}</p>
                <p>Tx: {regResult.tx_hash}</p>
                <p>Block: {regResult.block_number}</p>
              </div>
            )}
          </section>

          <section>
            <h3>Verify File</h3>
            <form onSubmit={handleVerifyFile} style={{ display: "grid", gap: "0.5rem" }}>
              <label>
                File
                <input
                  type="file"
                  onChange={(e) => setVerFile(e.target.files?.[0] || null)}
                />
              </label>
              {verErr && <p style={{ color: "red" }}>{verErr}</p>}
              <button type="submit" disabled={verLoading}>
                {verLoading ? "Verifying..." : "Verify Against Blockchain"}
              </button>
            </form>
            {verResult && (
              <div style={{ marginTop: "1rem" }}>
                <h4>Verification Result</h4>
                <p>Filename: {verResult.filename}</p>
                <p>Hash: {verResult.file_hash}</p>
                <p>On-chain: {verResult.on_chain ? "Yes" : "No"}</p>
                {verResult.on_chain && (
                  <>
                    <p>Match: {verResult.match ? "✅ Match" : "❌ Mismatch"}</p>
                    <p>Owner: {verResult.record?.owner}</p>
                    <p>Registered at: {verResult.record?.timestamp_iso}</p>
                    <p>Metadata: {verResult.record?.metadata}</p>
                  </>
                )}
              </div>
            )}
          </section>
        </div>

        {/* RIGHT: History */}
        <div style={{ flex: 1 }}>
          <section>
            <h3>Your Registered Files</h3>
            {loadingFiles ? (
              <p>Loading...</p>
            ) : !files.length ? (
              <p>No files registered yet.</p>
            ) : (
              <table
                border="1"
                cellPadding="4"
                style={{ width: "100%", fontSize: "0.9rem" }}
              >
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Hash</th>
                    <th>Tx</th>
                    <th>Block</th>
                    <th>Metadata</th>
                    <th>Created at</th>
                  </tr>
                </thead>
                <tbody>
                  {files.map((f) => (
                    <tr key={f.id}>
                      <td>{f.filename}</td>
                      <td>{f.file_hash}</td>
                      <td>{f.tx_hash}</td>
                      <td>{f.block_number}</td>
                      <td>{f.metadata}</td>
                      <td>{String(f.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
