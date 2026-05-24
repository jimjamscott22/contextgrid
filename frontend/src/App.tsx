import { Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import Home from "./routes/Home";
import Projects from "./routes/Projects";
import ProjectDetail from "./routes/ProjectDetail";
import Kanban from "./routes/Kanban";
import Tasks from "./routes/Tasks";
import Tags from "./routes/Tags";
import Templates from "./routes/Templates";
import Graph from "./routes/Graph";
import Analytics from "./routes/Analytics";
import Diagrams from "./routes/Diagrams";
import NotFound from "./routes/NotFound";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/kanban" element={<Kanban />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/tags" element={<Tags />} />
        <Route path="/templates" element={<Templates />} />
        <Route path="/graph" element={<Graph />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/diagrams" element={<Diagrams />} />
        <Route path="/index.html" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AppShell>
  );
}
