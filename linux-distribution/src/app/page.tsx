import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import TideCliSection from "@/components/TideCliSection";
import ArchitectureSection from "@/components/ArchitectureSection";
import CommunitySection from "@/components/CommunitySection";
import CTASection from "@/components/CTASection";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col bg-background">
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <TideCliSection />
      <ArchitectureSection />
      <CommunitySection />
      <CTASection />
      <Footer />
    </main>
  );
}
