import React, { useState, useEffect } from "react";
import { Container } from "@mui/material";
import Header from "./components/Header";
import DetectPage from "./pages/DetectPage";
import { getModelInfo } from "./services/detectApi";

export default function App() {
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    getModelInfo().then((r) => setModelInfo(r.data)).catch(() => {});
  }, []);

  return (
    <>
      <Header modelInfo={modelInfo} />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <DetectPage />
      </Container>
    </>
  );
}
