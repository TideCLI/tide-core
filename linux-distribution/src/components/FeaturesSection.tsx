import { Terminal, Database, Cpu, Layers, HardDrive, Package, Plus, Minus, ArrowRight, Check } from "lucide-react";
import { cn } from "@/lib/utils";

const BenchmarkBar = ({ label, value, max, color }: { label: string, value: string, max: number, color: string }) => {
    const width = parseFloat(value) / max * 100;

    return (
        <div className="w-full">
            <div className="flex justify-between text-xs font-mono mb-1">
                <span>{label}</span>
                <span className="font-bold">{value}s</span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                <div
                    className={cn("h-full rounded-full transition-all duration-1000", color)}
                    style={{ width: `${width}%` }}
                ></div>
            </div>
        </div>
    );
};

export default function FeaturesSection() {
    return (
        <section id="features" className="bg-section-bg py-24 border-y border-border">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">

                {/* Header */}
                <div className="mb-16 md:flex md:items-end justify-between">
                    <div className="max-w-2xl">
                        <h2 className="text-base font-semibold text-accent uppercase tracking-wide">
                            System Architecture
                        </h2>
                        <h3 className="mt-2 text-3xl font-bold tracking-tight text-primary sm:text-4xl">
                            Benchmarks & Specifications
                        </h3>
                    </div>
                    <div className="hidden md:block text-right">
                        <div className="text-sm font-medium text-muted">Latest Test: Build 2481 (x86_64)</div>
                        <div className="text-xs text-muted/80 font-mono">Verified on Intel i9-13900K</div>
                    </div>
                </div>

                {/* Bento Grid Layout */}
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 auto-rows-[minmax(180px,auto)]">

                    {/* 1. Large Benchmark Card (Span 2 col, 2 row on desktop) */}
                    <div className="md:col-span-2 md:row-span-2 bg-white border border-border rounded-2xl p-8 flex flex-col justify-between shadow-sm">
                        <div>
                            <div className="flex items-center justify-between mb-6">
                                <div className="p-2 bg-blue-50 rounded-lg text-accent"><Cpu className="h-6 w-6" /></div>
                                <span className="text-xs font-mono text-muted bg-slate-100 px-2 py-1 rounded">cold_boot_time</span>
                            </div>
                            <h4 className="text-2xl font-bold text-primary mb-2">Market Leading Performance</h4>
                            <p className="text-secondary text-sm mb-8">
                                TIDE OS strips away legacy init processes, resulting in boot times up to 4x faster than traditional distributions.
                            </p>
                        </div>

                        <div className="space-y-6">
                            <BenchmarkBar label="TIDE OS (v1.2)" value="0.4" max={5} color="bg-accent" />
                            <BenchmarkBar label="Alpine Linux" value="0.8" max={5} color="bg-slate-300" />
                            <BenchmarkBar label="Fedora Workstation" value="2.1" max={5} color="bg-slate-200" />
                            <BenchmarkBar label="Ubuntu 24.04" value="4.2" max={5} color="bg-slate-200" />
                        </div>
                    </div>

                    {/* 2. Immutable Root Card */}
                    <div className="md:col-span-1 bg-white border border-border rounded-xl p-6 shadow-sm hover:border-accent/40 transition-colors group">
                        <div className="mb-4 text-emerald-500 bg-emerald-50 w-fit p-2 rounded-lg flex items-center justify-center group-hover:bg-emerald-100 transition-colors">
                            <Database className="h-5 w-5" />
                        </div>
                        <h4 className="font-bold text-lg text-primary mb-2">Immutable Root</h4>
                        <p className="text-xs text-secondary leading-relaxed">
                            By default, the root filesystem is read-only. Updates are applied atomically via OSTree commits. No more broken upgrades.
                        </p>
                    </div>

                    {/* 3. Small ISO Size Stat */}
                    <div className="md:col-span-1 bg-[#0f172a] text-white border border-slate-700/50 rounded-xl p-6 flex flex-col justify-center items-center text-center shadow-lg relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <HardDrive className="h-24 w-24" />
                        </div>
                        <div className="text-4xl font-mono font-bold tracking-tighter mb-1">450<span className="text-base text-slate-400">MB</span></div>
                        <div className="text-xs text-slate-400 uppercase tracking-widest font-semibold">Base Image Size</div>
                    </div>

                    {/* 4. Package Repo Stat */}
                    <div className="md:col-span-1 bg-white border border-border rounded-xl p-6 shadow-sm flex flex-col justify-center items-center text-center">
                        <div className="text-3xl font-mono font-bold text-primary mb-1">24k+</div>
                        <div className="text-xs text-muted uppercase tracking-widest font-semibold">Binary Packages</div>
                        <div className="mt-3 text-[10px] text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full flex items-center gap-1">
                            <Check className="h-3 w-3" /> Reproducible
                        </div>
                    </div>

                    {/* 5. Kernel Version */}
                    <div className="md:col-span-1 bg-white border border-border rounded-xl p-6 shadow-sm relative group overflow-hidden">
                        <div className="absolute -right-4 -bottom-4 w-20 h-20 bg-accent/5 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                        <div className="flex justify-between items-start mb-2">
                            <h4 className="font-bold text-primary">Kernel</h4>
                            <Layers className="h-5 w-5 text-muted" />
                        </div>
                        <div className="text-xl font-mono text-primary font-bold">Linux 6.8</div>
                        <div className="text-xs text-secondary mt-1">+ RT-Preempt Patches</div>
                    </div>

                    {/* 6. Integration Card (Wide) */}
                    <div className="md:col-span-2 bg-gradient-to-br from-white to-slate-50 border border-border rounded-xl p-8 flex items-center justify-between shadow-sm">
                        <div>
                            <h4 className="font-bold text-lg text-primary mb-2">Declarative Configuration</h4>
                            <p className="text-xs text-secondary max-w-sm mb-4">
                                Define your entire system state in a single TOML file. Replicate your setup across 100 machines instantly.
                            </p>
                            <div className="flex items-center gap-2 text-xs font-mono text-accent cursor-pointer hover:underline">
                                View config spec <ArrowRight className="h-3 w-3" />
                            </div>
                        </div>
                        {/* Mini Config Preview */}
                        <div className="hidden lg:block bg-[#1e293b] rounded-lg p-3 text-[10px] text-slate-300 font-mono shadow-inner w-48 rotate-1 opacity-90 hover:rotate-0 transition-transform">
                            <div>[system]</div>
                            <div>hostname = <span className="text-green-400">"dev-node-01"</span></div>
                            <div>timezone = <span className="text-green-400">"UTC"</span></div>
                            <div className="mt-1">[packages]</div>
                            <div>neovim = <span className="text-yellow-400">"latest"</span></div>
                            <div>docker = <span className="text-yellow-400">"24.0"</span></div>
                        </div>
                    </div>

                </div>
            </div>
        </section>
    );
}
