import AppRouter from "./routes/AppRouter";
import ChatbotWidget from "./components/Chatbot";
import "./index.css";

export default function App() {
  return (
    <>
      <AppRouter />
      <ChatbotWidget />
    </>
  );
}
