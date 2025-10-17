import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import indianFlag from "@/assets/indian-flag-hero.jpg";
import lawgptLogo from "@/assets/lawgpt-logo.png";
import courtroom from "@/assets/courtroom.jpg";
import legalDocs from "@/assets/legal-docs.jpg";
import aiTech from "@/assets/ai-tech.jpg";

const Index = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const aboutRef = useRef<HTMLElement>(null);
  const featuresRef = useRef<HTMLElement>(null);
  const heroRef = useRef<HTMLElement>(null);

  const scrollToSection = (ref: React.RefObject<HTMLElement>) => {
    ref.current?.scrollIntoView({ behavior: "smooth" });
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-cream">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-primary/95 backdrop-blur-sm shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src={lawgptLogo} alt="LawGPT Logo" className="w-10 h-10" />
              <span className="text-xl font-bold text-gold">LawGPT</span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-6">
              <button
                onClick={() => scrollToSection(heroRef)}
                className="text-white hover:text-gold transition-smooth"
              >
                Home
              </button>
              <button
                onClick={() => scrollToSection(aboutRef)}
                className="text-white hover:text-gold transition-smooth"
              >
                About Us
              </button>
              <button
                onClick={() => scrollToSection(featuresRef)}
                className="text-white hover:text-gold transition-smooth"
              >
                Features
              </button>
              <Button
                onClick={() => navigate("/login")}
                variant="outline"
                className="bg-gold text-primary border-gold hover:bg-gold/90 hover:text-primary"
              >
                Get Started
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden text-white"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden mt-4 pb-4 flex flex-col gap-4 animate-slide-up">
              <button
                onClick={() => scrollToSection(heroRef)}
                className="text-white hover:text-gold transition-smooth text-left"
              >
                Home
              </button>
              <button
                onClick={() => scrollToSection(aboutRef)}
                className="text-white hover:text-gold transition-smooth text-left"
              >
                About Us
              </button>
              <button
                onClick={() => scrollToSection(featuresRef)}
                className="text-white hover:text-gold transition-smooth text-left"
              >
                Features
              </button>
              <Button
                onClick={() => navigate("/login")}
                className="bg-gold text-primary hover:bg-gold/90"
              >
                Get Started
              </Button>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section
        ref={heroRef}
        className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden"
        style={{
          backgroundImage: `linear-gradient(rgba(4, 42, 97, 0.3), rgba(4, 42, 97, 0.3)), url(${indianFlag})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      >
        <div className="container mx-auto px-4 text-center z-10 animate-fade-in">
          <img
            src={lawgptLogo}
            alt="LawGPT Logo"
            className="w-32 h-32 mx-auto mb-8 animate-scale-in"
          />
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 drop-shadow-lg">
            LawGPT
          </h1>
          <p className="text-2xl md:text-3xl text-white mb-4 font-semibold drop-shadow-md">
            Free Chatbot for All Legal Queries
          </p>
          <p className="text-xl md:text-2xl text-white/90 mb-12 drop-shadow-md">
            Instant answers and transparent perspectives for everyone
          </p>
          <Button
            onClick={() => navigate("/login")}
            size="lg"
            className="bg-gold text-primary hover:bg-gold/90 text-lg px-12 py-6 shadow-gold animate-scale-in"
          >
            Get Started
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section ref={featuresRef} className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-center text-primary mb-4">
            Key Features
          </h2>
          <div className="w-24 h-1 bg-gold mx-auto mb-16"></div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-8 rounded-xl bg-cream hover:shadow-lg transition-smooth">
              <div className="w-16 h-16 bg-gold rounded-full flex items-center justify-center mx-auto mb-6">
                <svg
                  className="w-8 h-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-primary mb-4">Instant Answers</h3>
              <p className="text-muted-foreground">
                Get immediate responses to your legal questions powered by advanced AI
              </p>
            </div>

            <div className="text-center p-8 rounded-xl bg-cream hover:shadow-lg transition-smooth">
              <div className="w-16 h-16 bg-gold rounded-full flex items-center justify-center mx-auto mb-6">
                <svg
                  className="w-8 h-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-primary mb-4">
                Multi-Model Responses
              </h3>
              <p className="text-muted-foreground">
                Compare answers from multiple AI models for comprehensive insights
              </p>
            </div>

            <div className="text-center p-8 rounded-xl bg-cream hover:shadow-lg transition-smooth">
              <div className="w-16 h-16 bg-gold rounded-full flex items-center justify-center mx-auto mb-6">
                <svg
                  className="w-8 h-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-primary mb-4">Privacy First</h3>
              <p className="text-muted-foreground">
                Your legal queries remain private and secure with end-to-end encryption
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section with Alternating Grid */}
      <section ref={aboutRef} className="py-20 bg-secondary">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-center text-primary mb-4">
            About LawGPT
          </h2>
          <div className="w-24 h-1 bg-gold mx-auto mb-16"></div>

          {/* Row 1: Left Images, Right Text */}
          <div className="grid md:grid-cols-2 gap-12 items-center mb-20">
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg overflow-hidden shadow-lg transform hover:scale-105 transition-smooth">
                <img src={lawgptLogo} alt="LawGPT Logo" className="w-full h-48 object-cover" />
              </div>
              <div className="rounded-lg overflow-hidden shadow-lg transform hover:scale-105 transition-smooth row-span-2">
                <img src={courtroom} alt="Courtroom" className="w-full h-full object-cover" />
              </div>
              <div className="rounded-lg overflow-hidden shadow-lg transform hover:scale-105 transition-smooth">
                <img src={legalDocs} alt="Legal Documents" className="w-full h-48 object-cover" />
              </div>
            </div>

            <div className="space-y-6">
              <h3 className="text-3xl font-bold text-primary">What is LawGPT?</h3>
              <p className="text-lg text-muted-foreground leading-relaxed">
                LawGPT is an advanced AI-powered legal assistant designed to provide instant,
                accurate, and transparent legal information to everyone. Our platform leverages
                cutting-edge artificial intelligence to democratize access to legal knowledge.
              </p>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Built with Indian legal context in mind, LawGPT understands the nuances of the
                Indian legal system and provides relevant, contextual answers to your queries.
              </p>
            </div>
          </div>

          {/* Row 2: Left Text, Right Images */}
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6 order-2 md:order-1">
              <h3 className="text-3xl font-bold text-primary">Powered by AI</h3>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Our platform uses multiple AI models including open-source solutions, our
                fine-tuned LawGPT model, and proprietary systems to ensure you receive the most
                comprehensive and accurate legal information.
              </p>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Each query is processed through multiple AI models, allowing you to compare
                responses and gain deeper insights into your legal questions.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 order-1 md:order-2">
              <div className="rounded-lg overflow-hidden shadow-lg transform hover:scale-105 transition-smooth row-span-2">
                <img src={aiTech} alt="AI Technology" className="w-full h-full object-cover" />
              </div>
              <div className="rounded-lg overflow-hidden shadow-lg transform hover:scale-105 transition-smooth">
                <img src={legalDocs} alt="Documents" className="w-full h-48 object-cover" />
              </div>
              <div className="rounded-lg overflow-hidden shadow-lg transform hover:scale-105 transition-smooth">
                <img src={courtroom} alt="Justice" className="w-full h-48 object-cover" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <div className="flex justify-center gap-8 mb-4">
            <a href="#" className="hover:text-gold transition-smooth">
              Privacy
            </a>
            <a href="#" className="hover:text-gold transition-smooth">
              Terms
            </a>
            <a href="#" className="hover:text-gold transition-smooth">
              Help
            </a>
          </div>
          <p className="text-white/80">
            © 2025 LawGPT. All rights reserved. Built for the people of India.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
