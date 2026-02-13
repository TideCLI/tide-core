import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#FFFFFF",
                "section-bg": "#F8FAFC",
                primary: "#0F172A", // primary text
                secondary: "#334155", // secondary text
                muted: "#64748B", // muted text
                accent: "#2563EB",
                border: "#E2E8F0",
            },
            fontFamily: {
                sans: ["var(--font-inter)", "sans-serif"],
                mono: ["var(--font-fira-code)", "monospace"],
            },
            borderRadius: {
                xl: "0.75rem",
            },
        },
    },
    plugins: [],
};

export default config;
