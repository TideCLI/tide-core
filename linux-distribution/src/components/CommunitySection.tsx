import { Github, Users, Calendar, Shield, Activity, GitBranch } from "lucide-react";
import Image from "next/image";

export default function CommunitySection() {
    return (
        <section id="community" className="bg-white py-24 border-b border-border">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-base font-semibold text-accent uppercase tracking-wide">
                        Ecosystem
                    </h2>
                    <h3 className="mt-2 text-3xl font-bold tracking-tight text-primary sm:text-4xl">
                        Built in the Open. Powered by Engineers.
                    </h3>
                    <p className="mt-4 text-lg text-secondary max-w-2xl mx-auto">
                        TIDE OS is fully open source. All development happens on GitHub.
                        We prioritize transparency, reproducible builds, and community governance.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {/* 1. Stats Card */}
                    <div className="bg-section-bg border border-border rounded-xl p-6 shadow-sm flex flex-col items-center justify-center text-center">
                        <div className="flex items-center gap-2 mb-2">
                            <Github className="h-6 w-6 text-primary" />
                            <span className="font-bold text-2xl text-primary">1.2k</span>
                        </div>
                        <div className="text-sm font-medium text-secondary">Stars on GitHub</div>
                        <div className="w-full h-px bg-border my-4"></div>
                        <div className="flex justify-between w-full text-xs text-muted font-mono">
                            <span>Fork: 142</span>
                            <span>Issues: 12</span>
                            <span>PRs: 4</span>
                        </div>
                    </div>

                    {/* 2. Contributors Column (Split into 2 cards) */}
                    <div className="flex flex-col gap-4">
                        <a href="https://github.com/SnoozeScript" target="_blank" rel="noopener noreferrer" className="bg-white border border-border rounded-xl p-4 shadow-sm flex items-center gap-4 hover:border-accent hover:shadow-md transition-all group flex-1">
                            <img src="https://github.com/SnoozeScript.png" alt="Aadil Inamdar" className="h-12 w-12 rounded-full border-2 border-slate-100 group-hover:border-accent transition-colors" />
                            <div className="text-left">
                                <div className="text-xs font-bold text-accent uppercase tracking-wider mb-0.5">Core Developer</div>
                                <div className="font-bold text-base text-primary group-hover:text-accent transition-colors">Aadil Inamdar</div>
                            </div>
                        </a>

                        <a href="https://github.com/om-ghante" target="_blank" rel="noopener noreferrer" className="bg-white border border-border rounded-xl p-4 shadow-sm flex items-center gap-4 hover:border-accent hover:shadow-md transition-all group flex-1">
                            <img src="https://github.com/om-ghante.png" alt="Om Ghante" className="h-12 w-12 rounded-full border-2 border-slate-100 group-hover:border-accent transition-colors" />
                            <div className="text-left">
                                <div className="text-xs font-bold text-accent uppercase tracking-wider mb-0.5">Core Developer</div>
                                <div className="font-bold text-base text-primary group-hover:text-accent transition-colors">Om Ghante</div>
                            </div>
                        </a>
                    </div>

                    {/* 3. Security Card */}
                    <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-6 shadow-sm flex flex-col items-center justify-center text-center">
                        <Shield className="h-8 w-8 text-emerald-600 mb-2" />
                        <div className="font-bold text-lg text-emerald-800">100% Reprodicble</div>
                        <div className="text-xs text-emerald-700 mt-1 max-w-xs leading-tight">
                            Every ISO build is cryptographically verifiable against the source code.
                        </div>
                        <button className="mt-4 text-xs font-bold text-emerald-700 bg-white border border-emerald-200 px-3 py-1.5 rounded-md hover:bg-emerald-100 transition-colors">
                            View SBOM Report
                        </button>
                    </div>
                </div>

                {/* Roadmap Timeline */}
                <div className="mt-20 border-t border-border pt-16">
                    <h4 className="text-xl font-bold text-primary mb-8 text-center flex items-center justify-center gap-2">
                        <Activity className="h-5 w-5 text-accent" /> Project Roadmap
                    </h4>

                    <div className="relative">
                        {/* Line */}
                        <div className="absolute left-1/2 xs:left-6 transform -translate-x-1/2 h-full w-0.5 bg-border z-0"></div>

                        <div className="space-y-12 relative z-10">
                            {/* Item 1 (Done) */}
                            <div className="flex flex-col xs:flex-row items-center xs:items-start gap-6 w-full max-w-3xl mx-auto">
                                <div className="flex-shrink-0 w-32 text-right text-sm font-mono text-muted xs:block hidden">Q4 2025</div>
                                <div className="h-4 w-4 rounded-full bg-emerald-500 border-4 border-white shadow-sm ring-1 ring-border"></div>
                                <div className="bg-white border border-border p-4 rounded-lg shadow-sm flex-1 w-full max-w-md">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="font-bold text-primary">v1.0 Initial Release</span>
                                        <span className="text-[10px] bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded font-bold uppercase">Shipped</span>
                                    </div>
                                    <p className="text-sm text-secondary">Core immutable root, TIDE CLI beta, standard kernel.</p>
                                </div>
                            </div>

                            {/* Item 2 (Current) */}
                            <div className="flex flex-col xs:flex-row items-center xs:items-start gap-6 w-full max-w-3xl mx-auto">
                                <div className="flex-shrink-0 w-32 text-right text-sm font-mono text-primary font-bold xs:block hidden">Q1 2026</div>
                                <div className="h-4 w-4 rounded-full bg-accent border-4 border-white shadow-sm ring-1 ring-accent animate-pulse"></div>
                                <div className="bg-white border border-accent p-4 rounded-lg shadow-md flex-1 w-full max-w-md">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="font-bold text-primary">v1.2 Stable Release</span>
                                        <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded font-bold uppercase">Live Now</span>
                                    </div>
                                    <p className="text-sm text-secondary">RT-Kernel patches, Wayland default, ARM64 support.</p>
                                </div>
                            </div>

                            {/* Item 3 (Future) */}
                            <div className="flex flex-col xs:flex-row items-center xs:items-start gap-6 w-full max-w-3xl mx-auto opacity-60">
                                <div className="flex-shrink-0 w-32 text-right text-sm font-mono text-muted xs:block hidden">Q3 2026</div>
                                <div className="h-4 w-4 rounded-full bg-slate-200 border-4 border-white shadow-sm ring-1 ring-border"></div>
                                <div className="bg-white border border-border border-dashed p-4 rounded-lg flex-1 w-full max-w-md">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="font-bold text-primary">v2.0 TIDE Cloud</span>
                                        <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded font-bold uppercase">Planned</span>
                                    </div>
                                    <p className="text-sm text-secondary">Remote fleet management, cloud sync for dotfiles.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
