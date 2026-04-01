import React from "react";
import { AppBar, Toolbar, Typography, Chip, Box } from "@mui/material";
import TrackChangesIcon from "@mui/icons-material/TrackChanges";

export default function Header({ modelInfo }) {
  return (
    <AppBar position="static" color="primary">
      <Toolbar sx={{ justifyContent: "space-between" }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <TrackChangesIcon />
          <Typography variant="h6" fontWeight="bold">
            Object Detection System
          </Typography>
        </Box>
        {modelInfo && (
          <Box sx={{ display: "flex", gap: 1 }}>
            <Chip label={`🤖 ${modelInfo.model}`} size="small"
              sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }} />
            <Chip label={modelInfo.classes} size="small"
              sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }} />
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
