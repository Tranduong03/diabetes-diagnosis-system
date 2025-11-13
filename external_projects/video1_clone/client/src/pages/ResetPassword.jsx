import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import api from "../api";

export default function ResetPassword() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await api.post(`/reset-password/${token}`, { password });
    navigate("/login");
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Reset Password</h2>
      <input type="password" placeholder="New password" onChange={(e) => setPassword(e.target.value)} />
      <button>Reset</button>
    </form>
  );
}
