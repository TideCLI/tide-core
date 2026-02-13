import { Building, Code, School, Cpu, BookOpen, Lock } from "lucide-react";

export default function UseCasesSection() {
    const cases = [
        {
            icon: School,
            title: "Open Education",
            description: "An immutable OS base for computer labs ensuring a consistent environment after every reboot."
        },
        {
            icon: Code,
            title: "Development Pods",
            description: "Isolated workspaces for Python, Rust, and Go developers without host pollution."
        },
        {
            icon: Building,
            title: "Enterprise Deployments",
            description: "Standardized fleet management with rollback capabilities and central config."
        },
        {
            icon: Cpu,
            title: "Embedded & Edge",
            description: "Stripped down kernel profiles for running on constrained ARM devices."
        },
        {
            icon: Lock,
            title: "Secure Research",
            description: "Mandatory access controls (MAC) enabled by default for sensitive data handling."
        },
        {
            icon: BookOpen,
            title: "Scientific Computing",
            description: "High-performance numerics libraries pre-compiled with architecture optimizations."
        }
    ];

    return (
        <section id="use-cases" className="bg-section-bg py-24 sm:py-32 border-t border-border">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
                <div className="mx-auto max-w-2xl lg:max-w-none text-center mb-16">
                    <h2 className="text-base/7 font-semibold text-accent uppercase tracking-wide">
                        Versatility
                    </h2>
                    <p className="mt-2 text-balance text-4xl font-semibold tracking-tight text-primary sm:text-5xl">
                        Built for diverse environments
                    </p>
                </div>

                <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
                    <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
                        {cases.map((uc) => (
                            <div key={uc.title} className="flex flex-col border border-border bg-white rounded-xl p-6 hover:shadow-sm transition-shadow">
                                <dt className="flex items-center gap-x-3 text-lg font-semibold leading-7 text-primary mb-4">
                                    <uc.icon className="h-5 w-5 flex-none text-accent" aria-hidden="true" />
                                    {uc.title}
                                </dt>
                                <dd className="flex flex-auto flex-col text-base leading-7 text-secondary">
                                    <p className="flex-auto">{uc.description}</p>
                                </dd>
                            </div>
                        ))}
                    </dl>
                </div>
            </div>
        </section>
    );
}
