import { ArrowRight, Check, Minus } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function CTASection() {
    return (
        <section className="relative isolate overflow-hidden bg-[#0f172a] py-24 sm:py-32">
            <div className="mx-auto max-w-7xl px-6 lg:px-8 text-center">
                <div className="mx-auto max-w-2xl">
                    <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl lg:text-5xl">
                        <span className="text-white">Stop configuring.</span> <br /><span className="text-emerald-400">Start engineering.</span>
                    </h2>
                    <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-slate-300">
                        Join the wave. Experience the speed of TIDE OS today.
                    </p>

                    <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-6">
                        <Link
                            href="/download"
                            className="rounded-xl bg-accent px-8 py-3.5 text-sm font-semibold text-white shadow-lg hover:bg-blue-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent flex items-center gap-2 group transition-all w-full sm:w-auto justify-center"
                        >
                            Download TIDE v1.2.0
                            <span className="text-blue-200 font-normal opacity-80 border-l border-blue-400/30 pl-2 ml-1 text-xs">450MB ISO</span>
                        </Link>
                        <Link
                            href="#"
                            className="text-sm font-semibold leading-6 text-white flex items-center gap-1 group w-full sm:w-auto justify-center hover:text-emerald-400 transition-colors"
                        >
                            View Source Code <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                        </Link>
                    </div>
                </div>

                {/* Competitive Table */}
                <div className="mt-20 overflow-hidden rounded-xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur-sm max-w-4xl mx-auto">
                    <table className="w-full text-left text-sm text-slate-300">
                        <thead className="border-b border-white/10 bg-white/5 text-xs uppercase font-bold tracking-wider text-slate-400">
                            <tr>
                                <th scope="col" className="p-4 sm:pl-6">Feature</th>
                                <th scope="col" className="p-4 text-emerald-400 bg-emerald-500/10 border-x border-emerald-500/20">TIDE OS</th>
                                <th scope="col" className="p-4 hidden sm:table-cell">NixOS</th>
                                <th scope="col" className="p-4 hidden sm:table-cell">Arch Linux</th>
                                <th scope="col" className="p-4 hidden md:table-cell">Ubuntu</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {[
                                { feat: "Immutable Root", tide: true, nix: true, arch: false, ubu: false },
                                { feat: "Atomic Updates", tide: true, nix: true, arch: false, ubu: false },
                                { feat: "Declarative Config", tide: true, nix: true, arch: false, ubu: false },
                                { feat: "Single Binary CLI", tide: true, nix: false, arch: false, ubu: false },
                                { feat: "Sub-400ms Boot", tide: true, nix: false, arch: true, ubu: false },
                                { feat: "Stable ABI", tide: true, nix: false, arch: false, ubu: true },
                            ].map((row, i) => (
                                <tr key={row.feat} className="hover:bg-white/5 transition-colors">
                                    <td className="p-4 font-medium text-white sm:pl-6">{row.feat}</td>
                                    <td className="p-4 text-emerald-400 bg-emerald-500/5 border-x border-emerald-500/20 font-bold">
                                        {row.tide ? <Check className="h-5 w-5 mx-auto lg:mx-0" /> : <Minus className="h-4 w-4 text-slate-600" />}
                                    </td>
                                    <td className="p-4 hidden sm:table-cell">{row.nix ? <Check className="h-4 w-4 text-slate-400" /> : <Minus className="h-4 w-4 text-slate-600" />}</td>
                                    <td className="p-4 hidden sm:table-cell">{row.arch ? <Check className="h-4 w-4 text-slate-400" /> : <Minus className="h-4 w-4 text-slate-600" />}</td>
                                    <td className="p-4 hidden md:table-cell">{row.ubu ? <Check className="h-4 w-4 text-slate-400" /> : <Minus className="h-4 w-4 text-slate-600" />}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

            </div>

            {/* Background Mesh (Subtle) */}
            <div className="absolute inset-0 -z-10 h-full w-full bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
            <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-accent opacity-20 blur-[100px]"></div>
        </section>
    );
}
