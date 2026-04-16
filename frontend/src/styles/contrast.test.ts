import { describe, expect, it } from "vitest";

/**
 * Compute WCAG 2.1 relative luminance for a hex color.
 * https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
 */
function luminance(hex: string): number {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16) / 255;
  const g = parseInt(h.slice(2, 4), 16) / 255;
  const b = parseInt(h.slice(4, 6), 16) / 255;
  const channel = (c: number) =>
    c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

/** WCAG contrast ratio between two hex colors (always ≥ 1). */
function contrast(fg: string, bg: string): number {
  const l1 = luminance(fg);
  const l2 = luminance(bg);
  const [lighter, darker] = l1 > l2 ? [l1, l2] : [l2, l1];
  return (lighter + 0.05) / (darker + 0.05);
}

// Token values kept in sync with frontend/src/styles/tokens.css.
// If tokens change, update this table so the contrast guard stays honest.
const TOKENS = {
  bg: "#f4f5f7",
  surface: "#ffffff",
  surfaceMuted: "#f8f9fa",
  text: "#111827",
  textMuted: "#4b5563",
  textSubtle: "#6b7280",
  textInverted: "#ffffff",
  accent: "#714b67", // Odoo default; per-company brand_color overrides at runtime
  accentFg: "#ffffff",
  accentSoft: "#efe8ec",
  danger: "#b91c1c",
  dangerSoft: "#fee2e2",
  success: "#15803d",
  warning: "#b45309",
};

describe("WCAG AA contrast for design tokens", () => {
  it("body text on page background ≥ 4.5:1", () => {
    expect(contrast(TOKENS.text, TOKENS.bg)).toBeGreaterThanOrEqual(4.5);
  });

  it("body text on surface (card) ≥ 4.5:1", () => {
    expect(contrast(TOKENS.text, TOKENS.surface)).toBeGreaterThanOrEqual(4.5);
  });

  it("muted text on surface ≥ 4.5:1 (secondary labels still readable)", () => {
    expect(contrast(TOKENS.textMuted, TOKENS.surface)).toBeGreaterThanOrEqual(4.5);
  });

  it("accent foreground on accent background ≥ 4.5:1 (button contrast)", () => {
    expect(contrast(TOKENS.accentFg, TOKENS.accent)).toBeGreaterThanOrEqual(4.5);
  });

  it("danger text on danger-soft background ≥ 4.5:1 (error banners)", () => {
    expect(contrast(TOKENS.danger, TOKENS.dangerSoft)).toBeGreaterThanOrEqual(4.5);
  });

  it("text on danger background (destructive button) ≥ 4.5:1", () => {
    expect(contrast(TOKENS.textInverted, TOKENS.danger)).toBeGreaterThanOrEqual(4.5);
  });

  it("text on success background ≥ 4.5:1", () => {
    expect(contrast(TOKENS.textInverted, TOKENS.success)).toBeGreaterThanOrEqual(4.5);
  });

  it("accent text on accent-soft background ≥ 4.5:1 (sidebar active state)", () => {
    expect(contrast(TOKENS.accent, TOKENS.accentSoft)).toBeGreaterThanOrEqual(4.5);
  });
});
