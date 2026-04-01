import React, { useState, useRef } from "react";
import {
  Box, CircularProgress, Alert, Typography, Paper,
  Chip, Table, TableBody, TableCell, TableHead,
  TableRow, LinearProgress, Divider, Grid,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { detectObjects } from "../services/detectApi";

const COLORS = ["#1976d2", "#388e3c", "#f57c00", "#7b1fa2", "#c62828",
                 "#00838f", "#558b2f", "#e65100", "#4527a0", "#37474f"];

export default function DetectPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await detectObjects(fd);
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Detection failed.");
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? Object.entries(result.class_summary).map(([label, count], i) => ({ label, count, fill: COLORS[i % COLORS.length] }))
    : [];

  return (
    <Box>
      {/* Drop zone */}
      <Paper
        variant="outlined"
        onClick={() => fileRef.current.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => e.preventDefault()}
        sx={{ p: 3, mb: 2, textAlign: "center", cursor: "pointer", borderStyle: "dashed", "&:hover": { bgcolor: "action.hover" } }}
      >
        <input ref={fileRef} type="file" hidden accept=".jpg,.jpeg,.png,.bmp,.webp"
          onChange={(e) => handleFile(e.target.files[0])} />
        {loading
          ? <Box><CircularProgress size={28} sx={{ mb: 1 }} /><Typography color="text.secondary">Detecting objects…</Typography></Box>
          : <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <UploadFileIcon color="action" />
              <Typography color="text.secondary">Drag & drop or click — JPG / PNG / BMP / WEBP</Typography>
            </Box>
        }
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Box>
          {/* Stats */}
          <Box sx={{ display: "flex", gap: 1.5, mb: 2, flexWrap: "wrap" }}>
            <Chip label={`${result.object_count} object${result.object_count !== 1 ? "s" : ""} detected`}
              color={result.object_count > 0 ? "success" : "default"} />
            <Chip label={`${result.image_width} × ${result.image_height} px`} variant="outlined" size="small" />
            <Chip label={result.model} variant="outlined" size="small" />
          </Box>

          <Grid container spacing={2}>
            {/* Annotated image */}
            <Grid item xs={12} md={7}>
              <Paper variant="outlined" sx={{ p: 1 }}>
                <img src={`data:image/jpeg;base64,${result.annotated_image}`}
                  alt="annotated" style={{ width: "100%", borderRadius: 4 }} />
              </Paper>
            </Grid>

            {/* Class summary chart */}
            <Grid item xs={12} md={5}>
              {chartData.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Detected Classes</Typography>
                  <ResponsiveContainer width="100%" height={Math.max(120, chartData.length * 40)}>
                    <BarChart data={chartData} layout="vertical"
                      margin={{ top: 0, right: 30, bottom: 0, left: 60 }}>
                      <XAxis type="number" allowDecimals={false} />
                      <YAxis type="category" dataKey="label" tick={{ fontSize: 12 }} width={60} />
                      <Tooltip />
                      <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                        {chartData.map((d, i) => <Cell key={i} fill={d.fill} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              )}
            </Grid>
          </Grid>

          {/* Detections table */}
          {result.detections.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" gutterBottom>All Detections</Typography>
              <Paper variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ bgcolor: "grey.50" }}>
                      <TableCell>#</TableCell>
                      <TableCell>Label</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell>Position (x, y)</TableCell>
                      <TableCell>Size (w × h)</TableCell>
                      <TableCell sx={{ minWidth: 100 }}>Bar</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {result.detections.map((d, i) => (
                      <TableRow key={i} hover>
                        <TableCell>{i + 1}</TableCell>
                        <TableCell>
                          <Chip label={d.label} size="small" color="primary" variant="outlined" />
                        </TableCell>
                        <TableCell>{d.confidence}%</TableCell>
                        <TableCell>({d.x}, {d.y})</TableCell>
                        <TableCell>{d.width} × {d.height}</TableCell>
                        <TableCell>
                          <LinearProgress variant="determinate" value={d.confidence}
                            sx={{ height: 6, borderRadius: 3 }} />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Paper>
            </>
          )}

          {result.object_count === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              No objects detected. Try a clearer image or lower the confidence threshold.
            </Alert>
          )}
        </Box>
      )}
    </Box>
  );
}
