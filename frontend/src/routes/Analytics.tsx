import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
} from "recharts";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/Empty";
import { useTheme } from "@/components/ThemeProvider";

const PALETTE = ["#60A5FA", "#A78BFA", "#34D399", "#FBBF24", "#F87171", "#22D3EE", "#FB7185", "#A3E635"];

export default function Analytics() {
  const { theme } = useTheme();
  const { data, isLoading, error } = useQuery({
    queryKey: qk.analytics,
    queryFn: api.analytics,
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  if (!data) return null;

  const axis = theme === "dark" ? "#A8B0BF" : "#6B7280";
  const grid = theme === "dark" ? "#263041" : "#E5E7EB";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="mt-1 text-fg-soft">Insights into your portfolio of projects.</p>
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
        <Stat label="Total" value={data.summary.total} />
        <Stat label="Active" value={data.summary.active} tone="success" />
        <Stat label="Ideas" value={data.summary.ideas} tone="warning" />
        <Stat label="Paused" value={data.summary.paused} />
        <Stat label="Avg progress" value={`${Math.round(data.summary.avg_progress)}%`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard title="Projects by status">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={data.by_status}
                dataKey="value"
                nameKey="label"
                outerRadius={90}
                label
              >
                {data.by_status.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="By language">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.by_language}>
              <CartesianGrid stroke={grid} strokeDasharray="3 3" />
              <XAxis dataKey="label" stroke={axis} />
              <YAxis stroke={axis} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#60A5FA" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="By type">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.by_type}>
              <CartesianGrid stroke={grid} strokeDasharray="3 3" />
              <XAxis dataKey="label" stroke={axis} />
              <YAxis stroke={axis} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#A78BFA" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Activity over time">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={data.activity_over_time}>
              <CartesianGrid stroke={grid} strokeDasharray="3 3" />
              <XAxis dataKey="label" stroke={axis} />
              <YAxis stroke={axis} allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#34D399" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Progress distribution">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.progress_distribution}>
              <CartesianGrid stroke={grid} strokeDasharray="3 3" />
              <XAxis dataKey="label" stroke={axis} />
              <YAxis stroke={axis} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#FBBF24" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Top tags">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.by_tag} layout="vertical">
              <CartesianGrid stroke={grid} strokeDasharray="3 3" />
              <XAxis type="number" stroke={axis} allowDecimals={false} />
              <YAxis dataKey="label" type="category" stroke={axis} width={100} />
              <Tooltip />
              <Bar dataKey="value" fill="#F87171" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  tone,
}: {
  label: string;
  value: string | number;
  tone?: "success" | "warning";
}) {
  return (
    <Card>
      <CardContent>
        <div className="text-xs uppercase text-fg-soft">{label}</div>
        <div
          className={
            tone === "success"
              ? "text-2xl font-bold text-success"
              : tone === "warning"
              ? "text-2xl font-bold text-warning"
              : "text-2xl font-bold"
          }
        >
          {value}
        </div>
      </CardContent>
    </Card>
  );
}

function ChartCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
