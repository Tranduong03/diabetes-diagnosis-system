import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await axios.post("http://localhost:5000/api/user/logout", {}, { withCredentials: true });
    navigate("/login");
  };

  return (
    <div style={{ margin: "20px" }}>
      <h1>Welcome to Home Page</h1>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
