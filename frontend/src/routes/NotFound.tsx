import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <h1 className="text-3xl font-bold">404</h1>
      <p className="text-fg-soft">The page you&apos;re looking for doesn&apos;t exist.</p>
      <Link to="/">
        <Button variant="primary">Go home</Button>
      </Link>
    </div>
  );
}
