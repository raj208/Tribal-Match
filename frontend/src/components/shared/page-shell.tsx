export function PageShell({ title, description }: { title: string; description: string }) {
  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "40px 20px" }}>
      <h1 style={{ marginBottom: 8 }}>{title}</h1>
      <p style={{ opacity: 0.8 }}>{description}</p>
    </main>
  );
}
