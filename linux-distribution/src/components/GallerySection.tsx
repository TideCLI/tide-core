import Image from "next/image";
import { Monitor, Smartphone, Terminal, Layout } from "lucide-react";

const IMAGES = [
    { src: "/images/dashboard.svg", alt: "Modern Dashboard", icon: Monitor },
    { src: "/images/terminal.svg", alt: "Powerful Terminal", icon: Terminal },
    { src: "/images/preview-1.svg", alt: "Code Editor", icon: Layout },
    { src: "/images/preview-2.svg", alt: "System Settings", icon: Smartphone },
    { src: "/images/preview-3.svg", alt: "File Browser", icon: Layout },
];

export default function GallerySection() {
    return (
        <section id="gallery" className="bg-white py-24 sm:py-32 border-t border-border">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
                <div className="mx-auto max-w-2xl text-center mb-16">
                    <h2 className="text-base/7 font-semibold text-accent uppercase tracking-wide">
                        Visual Preview
                    </h2>
                    <p className="mt-2 text-4xl font-semibold tracking-tight text-primary sm:text-5xl">
                        A Glimpse of Productivity
                    </p>
                    <p className="mt-6 text-lg text-secondary">
                        Designed for focus. Every pixel serves a purpose.
                    </p>
                </div>

                <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3 auto-rows-[300px]">
                    {IMAGES.map((item, i) => (
                        <div
                            key={item.src}
                            className={`relative group overflow-hidden rounded-xl border border-border bg-section-bg transition-all hover:border-accent/40 ${i === 0 || i === 3 ? "lg:col-span-2" : ""}`}
                        >
                            <div className="absolute inset-x-0 bottom-0 z-10 bg-gradient-to-t from-primary/80 via-primary/40 to-transparent p-6 opacity-0 transition-opacity duration-300 group-hover:opacity-100 flex items-end">
                                <div className="flex items-center gap-3 text-white">
                                    <item.icon className="h-5 w-5" />
                                    <span className="font-semibold text-sm">{item.alt}</span>
                                </div>
                            </div>
                            <Image
                                src={item.src}
                                alt={item.alt}
                                fill
                                className="object-cover transition-transform duration-500 group-hover:scale-105"
                                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                            />
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
