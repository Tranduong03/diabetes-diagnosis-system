import { useState } from "react";
import api from "../api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await api.post("/forgot-password", { email });
    setMessage(res.data.message);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Forgot Password</h2>
      <input placeholder="Enter your email" onChange={(e) => setEmail(e.target.value)} />
      <button>Send Reset Link</button>
      <p>{message}</p>
    </form>
  );
}
