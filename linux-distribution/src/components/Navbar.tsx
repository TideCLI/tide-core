"use client";

import Link from 'next/link';
import { Terminal, Github, Download, Menu, X, ChevronDown, Book, Server, CheckCircle, Smartphone } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

const NAV_LINKS = [
    { href: "#features", label: "Product" },
    { href: "#community", label: "Community" },
    { href: "/docs", label: "Wiki" },
];

export default function Navbar() {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isDownloadOpen, setIsDownloadOpen] = useState(false);

    return (
        <nav className="sticky top-0 z-50 h-20 w-full border-b border-border bg-white/95 backdrop-blur-sm">
            <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-6">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2 text-primary hover:opacity-90 transition-opacity">
                    <Terminal className="h-6 w-6 text-accent" strokeWidth={2.5} />
                    <span className="text-xl font-bold tracking-tight">TIDE OS</span>
                    <span className="hidden sm:inline-block rounded-md bg-section-bg border border-border px-2 py-0.5 text-xs font-mono text-secondary">
                        v1.2.0
                    </span>
                </Link>

                {/* Desktop Nav */}
                <div className="hidden lg:flex items-center gap-8">
                    {NAV_LINKS.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href} // This points to an ID on the same page for demonstration, or external for Wiki
                            className="relative text-sm font-medium text-secondary hover:text-primary transition-colors hover:underline underline-offset-4 decoration-accent/50 decoration-2"
                        >
                            {link.label}
                        </Link>
                    ))}
                </div>

                {/* Right CTA */}
                <div className="hidden lg:flex items-center gap-4">
                    {/* GitHub Stats Mock */}
                    <Link
                        href="https://github.com"
                        target="_blank"
                        className="flex items-center gap-2 rounded-lg border border-border bg-white px-3 py-1.5 text-xs font-medium text-secondary hover:bg-section-bg hover:text-primary transition-colors"
                    >
                        <Github className="h-4 w-4" />
                        <span>1.2k</span>
                    </Link>

                    {/* Download Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setIsDownloadOpen(!isDownloadOpen)}
                            onBlur={() => setTimeout(() => setIsDownloadOpen(false), 200)}
                            className="flex items-center gap-2 rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-accent outline-none"
                        >
                            <Download className="h-4 w-4" />
                            <span>Get ISO</span>
                            <ChevronDown className={cn("h-4 w-4 transition-transform", isDownloadOpen && "rotate-180")} />
                        </button>

                        {isDownloadOpen && (
                            <div className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-border bg-white shadow-xl p-1 animate-in fade-in zoom-in-95 duration-200">
                                <div className="px-3 py-2 text-xs font-semibold text-muted uppercase tracking-wider border-b border-border/50 mb-1">
                                    Stable Release v1.2.0
                                </div>
                                <Link href="#" className="flex items-center gap-3 px-3 py-2.5 text-sm text-primary hover:bg-section-bg rounded-lg">
                                    <Server className="h-4 w-4 text-accent" />
                                    <div>
                                        <div className="font-medium">x86_64 ISO</div>
                                        <div className="text-xs text-muted">For Intel/AMD Desktops</div>
                                    </div>
                                </Link>
                                <Link href="#" className="flex items-center gap-3 px-3 py-2.5 text-sm text-primary hover:bg-section-bg rounded-lg">
                                    <Smartphone className="h-4 w-4 text-accent" />
                                    <div>
                                        <div className="font-medium">ARM64 ISO</div>
                                        <div className="text-xs text-muted">For Raspberry Pi / Mac</div>
                                    </div>
                                </Link>
                            </div>
                        )}
                    </div>
                </div>

                {/* Mobile Menu Button */}
                <button
                    className="lg:hidden p-2 text-secondary hover:text-primary"
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                >
                    {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </button>
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="lg:hidden absolute top-20 left-0 w-full bg-white border-b border-border p-6 flex flex-col gap-4 shadow-lg animate-in slide-in-from-top-5">
                    {NAV_LINKS.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className="text-base font-medium text-secondary hover:text-primary py-2 border-b border-border/50 last:border-0"
                            onClick={() => setIsMobileMenuOpen(false)}
                        >
                            {link.label}
                        </Link>
                    ))}
                    <div className="flex flex-col gap-3 mt-4">
                        <Link
                            href="https://github.com"
                            target="_blank"
                            className="flex items-center justify-center gap-2 w-full rounded-xl border border-border px-4 py-3 text-sm font-medium text-secondary hover:bg-section-bg"
                        >
                            <Github className="h-5 w-5" />
                            GitHub (1.2k)
                        </Link>
                        <button className="flex items-center justify-center gap-2 w-full rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700">
                            <Download className="h-4 w-4" />
                            Download ISO v1.2.0
                        </button>
                    </div>
                </div>
            )}
        </nav>
    );
}
