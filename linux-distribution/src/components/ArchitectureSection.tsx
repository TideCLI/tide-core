import { ArrowRight, Cpu, Server, Database, Terminal, Layout } from "lucide-react";
import { cn } from "@/lib/utils";

const StackCard = ({ title, desc, icon: Icon }: { title: string, desc: string, icon: any }) => (
    <div className="group relative bg-white border border-border rounded-xl p-6 shadow-sm hover:border-accent hover:shadow-md transition-all duration-300 flex flex-col gap-4">
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
                <div className="flex-shrink-0 p-2.5 bg-section-bg rounded-lg text-secondary group-hover:text-accent group-hover:bg-accent/10 transition-colors">
                    <Icon className="h-6 w-6" />
                </div>
                <h4 className="text-lg font-bold text-primary">{title}</h4>
            </div>
            <div className="hidden sm:block text-xs font-mono text-muted bg-slate-50 px-2 py-1 rounded border border-border opacity-70 group-hover:opacity-100 transition-opacity">
                {Icon === Cpu ? "v6.8-rt" : Icon === Server ? "pid 1" : Icon === Database ? ".ostree/repo" : Icon === Terminal ? "Standard I/O" : "Direct Rendering"}
            </div>
        </div>

        <p className="text-sm text-secondary leading-relaxed">{desc}</p>

        <div className="mt-auto pt-4 flex items-center text-xs font-semibold text-accent opacity-0 group-hover:opacity-100 transition-opacity -translate-x-2 group-hover:translate-x-0 duration-300">
            Learn more <ArrowRight className="ml-1 h-3 w-3" />
        </div>
    </div>
);

export default function ArchitectureSection() {
    return (
        <section id="architecture" className="bg-section-bg py-24 border-b border-border">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">

                <div className="text-center mb-16">
                    <h2 className="text-base font-semibold text-accent uppercase tracking-wide">
                        Under the Hood
                    </h2>
                    <h3 className="mt-2 text-3xl font-bold tracking-tight text-primary sm:text-4xl">
                        The TIDE Technology Stack
                    </h3>
                    <p className="mt-4 text-lg text-secondary max-w-2xl mx-auto">
                        A modular, component-based architecture designed for isolation and predictability.
                        Explore the layers that make TIDE OS unique.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <StackCard
                        title="User Interface"
                        desc="Wayland Compositor (Sway/Hyprland) with custom GTK4 theming for a cohesive visual experience."
                        icon={Layout}
                    />

                    <StackCard
                        title="CLI Interface"
                        desc="Unified TIDE Command wrapper for all system operations. One tool for everything."
                        icon={Terminal}
                    />

                    <StackCard
                        title="Package Manager"
                        desc="Atomic updates via libostree backend mixed with a custom dependency resolver."
                        icon={Database}
                    />

                    <StackCard
                        title="Runtime Layer"
                        desc="Minimal init system (s6/runit) paired with musl libc for lightweight execution."
                        icon={Server}
                    />

                    <StackCard
                        title="Kernel Layer"
                        desc="Linux 6.8 LTS with real-time patches applied for low-latency audio and processing."
                        icon={Cpu}
                    />

                    <div className="relative bg-[#0f172a] border border-border rounded-xl p-6 shadow-sm flex flex-col justify-center items-center text-center overflow-hidden group hover:shadow-lg transition-shadow">
                        <div className="absolute inset-0 bg-gradient-to-br from-accent/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <h4 className="text-lg font-bold text-white z-10">Read the Docs</h4>
                        <p className="text-sm text-slate-400 mt-2 mb-4 z-10">
                            Deep dive into the architecture decisions.
                        </p>
                        <button className="z-10 bg-accent text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-600 transition-colors">
                            View Documentation
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}
