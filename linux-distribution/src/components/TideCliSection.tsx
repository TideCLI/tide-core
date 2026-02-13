import { Terminal, ArrowRight, Play, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const TerminalWindow = ({ type, title, children, className }: { type: 'standard' | 'tide', title: string, children: React.ReactNode, className?: string }) => (
    <div className={cn("overflow-hidden rounded-xl border font-mono text-sm leading-relaxed shadow-lg h-full", className, type === 'tide' ? 'border-accent/40 bg-[#0f172a]' : 'border-border bg-white')}>
        {/* Header */}
        <div className={cn("flex items-center justify-between border-b px-4 py-3", type === 'tide' ? 'border-white/10 bg-white/5 text-slate-400' : 'border-border bg-section-bg text-secondary')}>
            <div className="flex items-center gap-2">
                <div className={cn("h-3 w-3 rounded-full", type === 'tide' ? 'bg-red-500/80' : 'bg-slate-300')}></div>
                <div className={cn("h-3 w-3 rounded-full", type === 'tide' ? 'bg-yellow-500/80' : 'bg-slate-300')}></div>
                <div className={cn("h-3 w-3 rounded-full", type === 'tide' ? 'bg-green-500/80' : 'bg-slate-300')}></div>
            </div>
            <div className="text-xs font-semibold tracking-wide">{title}</div>
            <div className="w-12"></div>
        </div>
        {/* Body */}
        <div className={cn("p-6 space-y-4", type === 'tide' ? 'text-slate-300' : 'text-slate-600')}>
            {children}
        </div>
    </div>
);

export default function TideCliSection() {
    return (
        <section id="tide-cli" className="w-full bg-white py-24 sm:py-32 border-b border-border">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">

                <div className="mx-auto max-w-4xl text-center mb-16">
                    <div className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/5 px-3 py-1 w-fit mb-6">
                        <span className="text-xs font-semibold text-accent uppercase tracking-wider">Comparative Analysis</span>
                    </div>
                    <h2 className="text-4xl font-bold tracking-tight text-primary sm:text-5xl">
                        Why We Rebuilt the CLI
                    </h2>
                    <p className="mt-4 text-lg text-secondary max-w-2xl mx-auto">
                        Standard package managers are slow, imperative, and prone to breaking. TIDE CLI is declarative, atomic, and absurdly fast.
                    </p>
                </div>

                <div className="relative isolate">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">

                        {/* Left: Standard (Bad) */}
                        <div className="relative group rounded-xl bg-slate-50 border border-slate-200 p-1 shadow-sm opacity-90 hover:opacity-100 transition-opacity">
                            <div className="absolute -top-3 left-4 z-10 bg-red-100 text-red-700 px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider shadow-sm border border-red-200">
                                Legacy (apt/dnf)
                            </div>
                            <TerminalWindow type="standard" title="user@ubuntu: ~" className="shadow-none border-none">
                                {/* Command */}
                                <div className="flex gap-2 text-slate-800 font-bold border-b border-slate-200 pb-2 mb-4">
                                    <span className="text-green-600">$</span>
                                    <span>sudo apt install neovim</span>
                                </div>

                                {/* Output Stream (Simulated mess) */}
                                <div className="space-y-1 text-xs opacity-70 font-mono">
                                    <div>Reading package lists... Done</div>
                                    <div>Building dependency tree... Done</div>
                                    <div>Reading state information... Done</div>
                                    <div className="text-yellow-600 truncate">The following additional packages will be installed:</div>
                                    <div className="pl-2 text-slate-500 truncate">liblua5.1-0 libmsgpackc2 libtermkey1...</div>
                                    <div>Need to get 4,210 kB of archives.</div>
                                    <div>After this operation, 18.4 MB disk space used.</div>
                                    <div>Do you want to continue? [Y/n] Y</div>
                                    <div className="truncate text-slate-500">Get:1 http://us.archive.ubuntu.com/ubuntu...</div>
                                    <div className="animate-pulse text-red-500 font-bold mt-2">Waiting for headers... (45s)</div>
                                </div>
                            </TerminalWindow>
                            <div className="bg-red-50 p-3 text-center rounded-b-lg border-t border-red-100 mt-2">
                                <p className="text-xs text-red-600 font-bold">
                                    Avg Install Time: 45s • Root Required
                                </p>
                            </div>
                        </div>

                        {/* Right: TIDE (Good) */}
                        <div className="relative transform lg:-translate-y-6 lg:scale-105 z-10">
                            <div className="absolute -top-3 right-4 z-20 bg-emerald-100 text-emerald-700 px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider shadow-sm border border-emerald-200 flex items-center gap-1">
                                <CheckCircle className="h-3 w-3" /> Recommended
                            </div>
                            <TerminalWindow type="tide" title="user@tide-os: ~" className="shadow-2xl ring-1 ring-accent/20">
                                {/* Command */}
                                <div className="flex gap-2 font-bold mb-6 pt-2">
                                    <span className="text-emerald-400">➜</span>
                                    <span className="text-blue-400">~</span>
                                    <span className="text-white">tide install neovim</span>
                                </div>

                                {/* Output Stream (Clean, Parallel) */}
                                <div className="space-y-3 text-xs">
                                    <div className="flex justify-between items-center text-slate-400 border-b border-white/5 pb-2">
                                        <span>Resolving dependency graph...</span>
                                        <span className="text-emerald-400 font-bold">12ms</span>
                                    </div>

                                    {/* Parallel Downloads Viz */}
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-[11px] text-blue-300">
                                            <span>neovim-0.9.5-x86_64.pkg</span>
                                            <span>[###################] 100%</span>
                                        </div>
                                        <div className="flex justify-between text-[11px] text-blue-300">
                                            <span>libvterm-0.3.3.pkg</span>
                                            <span>[###################] 100%</span>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 text-emerald-400 font-bold pt-2">
                                        <CheckCircle className="h-4 w-4" />
                                        <span>Committed in 1.2s</span>
                                    </div>
                                </div>

                                {/* Active Prompt */}
                                <div className="flex gap-2 font-bold mt-6 pt-2 border-t border-white/5">
                                    <span className="text-emerald-400">➜</span>
                                    <span className="text-blue-400">~</span>
                                    <span className="w-2.5 h-5 bg-slate-400 animate-pulse block"></span>
                                </div>
                            </TerminalWindow>
                            <div className="absolute -bottom-10 left-0 right-0 text-center">
                                <p className="text-sm text-emerald-600 font-bold bg-emerald-50 inline-block px-4 py-1 rounded-full border border-emerald-100 shadow-sm">
                                    Atomic • Declarative • 1.2s
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mt-20 text-center">
                    <button className="inline-flex items-center gap-2 text-sm font-semibold text-primary hover:text-accent transition-colors group">
                        Read the Architecture Whitepaper
                        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </button>
                </div>
            </div>
        </section>
    );
}
