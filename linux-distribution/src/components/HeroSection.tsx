"use client";

import { Copy, Terminal as TerminalIcon, Check, Plus, Minus, GitCommit, Users, Clock } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import Image from 'next/image';

const TerminalMock = ({ className }: { className?: string }) => {
    const [isCopied, setIsCopied] = useState(false);

    const handleCopy = () => {
        setIsCopied(true);
        navigator.clipboard.writeText("curl -fsSL https://tide-os.org/install.sh | bash");
        setTimeout(() => setIsCopied(false), 2000);
    };

    return (
        <div className={cn("relative overflow-hidden rounded-xl border border-border bg-[#0f172a] shadow-2xl font-mono text-sm leading-relaxed", className)}>
            {/* Window Header */}
            <div className="flex items-center justify-between border-b border-white/10 bg-white/5 px-4 py-3 backdrop-blur-md">
                <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-[#ef4444] border border-red-500/50"></div>
                    <div className="h-3 w-3 rounded-full bg-[#eab308] border border-yellow-500/50"></div>
                    <div className="h-3 w-3 rounded-full bg-[#22c55e] border border-green-500/50"></div>
                </div>
                <div className="text-xs text-slate-400 font-medium tracking-wide">user@tide-build-server: ~</div>
                <div className="w-12"></div> {/* Spacer for balance */}
            </div>

            {/* Terminal Body */}
            <div className="p-6 space-y-4 text-slate-300">
                {/* Command Line 1 */}
                <div className="group relative pr-12">
                    <div className="flex items-center gap-3">
                        <span className="text-emerald-400 font-bold">➜</span>
                        <span className="text-blue-400 font-bold">~</span>
                        <span className="typing-effect text-white">tide build --release --arch=x86_64</span>
                    </div>
                    {/* Copy Button */}
                    <button
                        onClick={handleCopy}
                        className="absolute right-0 top-1/2 -translate-y-1/2 p-1.5 rounded-md text-slate-500 hover:text-white hover:bg-white/10 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
                        title="Copy Command"
                    >
                        {isCopied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                    </button>
                </div>

                {/* Output Simulation */}
                <div className="space-y-1 opacity-90 text-xs">
                    <div className="flex gap-2">
                        <span className="text-emerald-500 font-bold">[SUCCESS]</span>
                        <span>Configuration loaded from tide.toml</span>
                    </div>
                    <div className="flex gap-2">
                        <span className="text-blue-500 font-bold">[BUILD]</span>
                        <span>Compiling kernel v6.8.12-rt... <span className="text-slate-500">(2.4s)</span></span>
                    </div>
                    <div className="flex gap-2">
                        <span className="text-blue-500 font-bold">[LINK]</span>
                        <span>Linking statically standard libraries...</span>
                    </div>
                    <div className="flex gap-2">
                        <span className="text-yellow-500 font-bold">[WARN]</span>
                        <span>Optimizing for instruction set: AVX2</span>
                    </div>
                    <div className="flex gap-2">
                        <span className="text-emerald-500 font-bold">[DONE]</span>
                        <span>Finished release [optimized] target(s) in 15.2s</span>
                    </div>
                </div>

                {/* Active Prompt */}
                <div className="flex items-center gap-3 pt-2">
                    <span className="text-emerald-400 font-bold">➜</span>
                    <span className="text-blue-400 font-bold">~</span>
                    <span className="w-2.5 h-5 bg-slate-400 animate-pulse block"></span>
                </div>
            </div>
            {/* Gradient Overlay for Depth */}
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-tr from-blue-500/5 via-transparent to-transparent"></div>
        </div>
    );
};

export default function HeroSection() {
    return (
        <section className="relative overflow-hidden bg-background py-20 lg:py-32 border-b border-border">
            <div className="mx-auto grid max-w-7xl grid-cols-1 gap-16 px-6 lg:grid-cols-2 lg:items-center">
                {/* Left Content */}
                <div className="flex flex-col gap-8 text-center lg:text-left">
                    {/* Version Badge */}
                    <div className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/5 px-3 py-1 w-fit mx-auto lg:mx-0">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                        </span>
                        <span className="text-xs font-semibold text-accent uppercase tracking-wider">v1.2.0 Stable Release</span>
                    </div>

                    <h1 className="text-5xl font-extrabold tracking-tight text-primary sm:text-6xl leading-[1.1]">
                        The Immutable, Rust-Based OS for <br className="hidden lg:block" />
                        <span className="text-accent underline decoration-4 underline-offset-4 decoration-accent/20">High-Performance</span> Developers
                    </h1>

                    <p className="text-lg leading-relaxed text-secondary max-w-xl mx-auto lg:mx-0">
                        Say goodbye to dependency hell. TIDE OS guarantees atomic updates, sub-second boot times, and a declarative system configuration. Built for reliability.
                    </p>

                    {/* Hard Specs List */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-3 gap-x-8 text-sm font-medium text-secondary pt-2">
                        {[
                            "Boot to TTY in <400ms",
                            "Full Wayland Compositor Support",
                            "450MB Minimal ISO Size",
                            "Signed OCI-compliant Updates"
                        ].map((spec, i) => (
                            <div key={i} className="flex items-center gap-2 justify-center lg:justify-start">
                                <Check className="h-4 w-4 text-emerald-500 flex-shrink-0" strokeWidth={3} />
                                {spec}
                            </div>
                        ))}
                    </div>

                    {/* GitHub / Commits Stats (Social Proof) */}
                    <div className="flex items-center justify-center lg:justify-start gap-6 pt-6 text-xs text-muted font-mono">
                        <div className="flex items-center gap-2">
                            <GitCommit className="h-4 w-4" />
                            <span>Last commit: 2h ago</span>
                        </div>
                        <div className="h-1 w-1 rounded-full bg-border"></div>
                        <div className="flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            <span>54 Contributors</span>
                        </div>
                        <div className="h-1 w-1 rounded-full bg-border"></div>
                        <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            <span>Uptime: 99.99%</span>
                        </div>
                    </div>
                </div>

                {/* Right Terminal Mock */}
                <div className="relative w-full max-w-lg lg:max-w-none mx-auto lg:translate-x-8">
                    <TerminalMock className="transform transition-transform hover:scale-[1.01] duration-500 shadow-xl" />

                    {/* Context Badge Floating */}
                    <div className="absolute -bottom-6 -left-6 z-10 hidden lg:flex items-center gap-3 rounded-lg border border-border bg-white px-4 py-3 shadow-lg animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-50">
                            <Image src="/next.svg" width={20} height={20} alt="Tech" className="opacity-80" />
                        </div>
                        <div>
                            <div className="text-xs font-semibold text-primary">Native Support</div>
                            <div className="text-[10px] text-muted">Next.js / Rust / Go / Docker</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
