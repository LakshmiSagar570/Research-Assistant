import { type ReactNode, type ButtonHTMLAttributes } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-end",
        padding: "32px 40px 24px",
        borderBottom: "1px solid var(--rule)",
        gap: 24,
      }}
    >
      <div>
        {eyebrow && (
          <div
            style={{
              fontFamily: "var(--mono)",
              fontSize: 11,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "var(--accent)",
              marginBottom: 8,
              fontWeight: 500,
            }}
          >
            {eyebrow}
          </div>
        )}
        <h1 style={{ fontSize: 26 }}>{title}</h1>
        {description && (
          <p style={{ margin: "8px 0 0", color: "var(--ink-soft)", fontSize: 14, maxWidth: 560 }}>
            {description}
          </p>
        )}
      </div>
      {action}
    </div>
  );
}

export function Card({
  children,
  style,
  padded = true,
}: {
  children: ReactNode;
  style?: React.CSSProperties;
  padded?: boolean;
}) {
  return (
    <div
      style={{
        background: "var(--paper-raised)",
        border: "1px solid var(--rule)",
        borderRadius: "var(--radius)",
        boxShadow: "var(--shadow-card)",
        padding: padded ? 20 : 0,
        ...style,
      }}
    >
      {children}
    </div>
  );
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md";
  icon?: ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  icon,
  children,
  style,
  disabled,
  ...rest
}: ButtonProps) {
  const base: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 7,
    fontWeight: 600,
    fontSize: size === "sm" ? 12.5 : 13.5,
    padding: size === "sm" ? "6px 12px" : "9px 16px",
    borderRadius: 4,
    border: "1px solid transparent",
    transition: "opacity 0.12s, background 0.12s, border-color 0.12s",
    opacity: disabled ? 0.5 : 1,
    cursor: disabled ? "not-allowed" : "pointer",
    whiteSpace: "nowrap",
  };

  const variants: Record<string, React.CSSProperties> = {
    primary: { background: "var(--ink)", color: "var(--paper-raised)" },
    secondary: {
      background: "var(--paper-raised)",
      color: "var(--ink)",
      borderColor: "var(--rule-strong)",
    },
    ghost: { background: "transparent", color: "var(--ink-soft)" },
    danger: { background: "transparent", color: "var(--accent)", borderColor: "var(--accent-soft)" },
  };

  return (
    <button style={{ ...base, ...variants[variant], ...style }} disabled={disabled} {...rest}>
      {icon}
      {children}
    </button>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "accent" | "well" | "gap";
}) {
  const tones: Record<string, React.CSSProperties> = {
    neutral: { background: "var(--rule)", color: "var(--ink-soft)" },
    accent: { background: "var(--accent-soft)", color: "var(--accent-strong)" },
    well: { background: "var(--well-soft)", color: "var(--well)" },
    gap: { background: "var(--gap-soft)", color: "var(--gap)" },
  };
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "2px 8px",
        borderRadius: 20,
        fontSize: 11,
        fontWeight: 600,
        fontFamily: "var(--mono)",
        letterSpacing: "0.01em",
        ...tones[tone],
      }}
    >
      {children}
    </span>
  );
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div
      style={{
        textAlign: "center",
        padding: "64px 24px",
        color: "var(--ink-faint)",
      }}
    >
      <h3 style={{ fontSize: 17, color: "var(--ink-soft)", marginBottom: 6 }}>{title}</h3>
      {description && <p style={{ fontSize: 13.5, maxWidth: 380, margin: "0 auto 16px" }}>{description}</p>}
      {action}
    </div>
  );
}

export function Spinner({ size = 16 }: { size?: number }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        border: "2px solid var(--rule-strong)",
        borderTopColor: "var(--accent)",
        borderRadius: "50%",
        animation: "spin 0.7s linear infinite",
      }}
    />
  );
}
