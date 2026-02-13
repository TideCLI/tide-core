import Link from "next/link";
import { Github, Twitter, Linkedin, Terminal } from "lucide-react";

export default function Footer() {
    return (
        <footer className="border-t border-border bg-white" aria-labelledby="footer-heading">
            <h2 id="footer-heading" className="sr-only">
                Footer
            </h2>
            <div className="mx-auto max-w-7xl px-6 pb-8 pt-16 sm:pt-24 lg:px-8 lg:pt-32">
                <div className="xl:grid xl:grid-cols-3 xl:gap-8">
                    <div className="space-y-8">
                        <Link href="/" className="flex items-center gap-2 text-primary hover:opacity-90">
                            <Terminal className="h-6 w-6 text-accent" />
                            <span className="text-xl font-bold tracking-tight">Linux Distribution</span>
                        </Link>
                        <p className="text-sm leading-6 text-secondary max-w-xs">
                            The modern operating system for developers, built with safety and performance in mind.
                        </p>
                        <div className="flex flex-col space-y-4">
                            <Link href="https://github.com/tidecli" target="_blank" className="text-muted hover:text-accent w-fit">
                                <span className="sr-only">GitHub</span>
                                <Github className="h-6 w-6" aria-hidden="true" />
                            </Link>
                            <p className="text-base font-semibold text-primary">
                                Developed by <a href="https://github.com/SnoozeScript" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">Aadil Inamdar</a> & <a href="https://github.com/om-ghante" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">Om Ghante</a>.
                            </p>
                        </div>
                    </div>
                    <div className="mt-16 grid grid-cols-2 gap-8 xl:col-span-2 xl:mt-0">
                        <div className="md:grid md:grid-cols-2 md:gap-8">
                            <div>
                                <h3 className="text-sm font-semibold leading-6 text-primary">Product</h3>
                                <ul role="list" className="mt-6 space-y-4">
                                    {['Features', 'Security', 'Enterprise', 'Roadmap'].map((item) => (
                                        <li key={item}>
                                            <Link href="#" className="text-sm leading-6 text-secondary hover:text-primary transition-colors">
                                                {item}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="mt-10 md:mt-0">
                                <h3 className="text-sm font-semibold leading-6 text-primary">Support</h3>
                                <ul role="list" className="mt-6 space-y-4">
                                    {['Documentation', 'API Reference', 'System Status', 'Community'].map((item) => (
                                        <li key={item}>
                                            <Link href="#" className="text-sm leading-6 text-secondary hover:text-primary transition-colors">
                                                {item}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                        <div className="md:grid md:grid-cols-2 md:gap-8">
                            <div>
                                <h3 className="text-sm font-semibold leading-6 text-primary">Company</h3>
                                <ul role="list" className="mt-6 space-y-4">
                                    {['About', 'Blog', 'Careers', 'Press'].map((item) => (
                                        <li key={item}>
                                            <Link href="#" className="text-sm leading-6 text-secondary hover:text-primary transition-colors">
                                                {item}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="mt-10 md:mt-0">
                                <h3 className="text-sm font-semibold leading-6 text-primary">Legal</h3>
                                <ul role="list" className="mt-6 space-y-4">
                                    {['Privacy', 'Terms', 'License'].map((item) => (
                                        <li key={item}>
                                            <Link href="#" className="text-sm leading-6 text-secondary hover:text-primary transition-colors">
                                                {item}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="mt-16 border-t border-border pt-8 sm:mt-20 lg:mt-24">
                    <p className="text-xs leading-5 text-muted">
                        &copy; {new Date().getFullYear()} TIDE OS. All rights reserved. Developed by Aadil Inamdar & Om Ghante.
                    </p>
                </div>
            </div>
        </footer>
    );
}
