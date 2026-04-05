/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Heart, Users, Shield, Award, Menu, X, Quote, CheckCircle, AlertTriangle, Gavel, Send, Mail, User, MessageSquare } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Link } from "react-router-dom";
import axios from "axios";
import { API } from "../App";
import { toast } from "sonner";
import { useTheme } from "../contexts/ThemeContext";

const AboutPage = () => {

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [contactData, setContactData] = useState({ name: "", email: "", subject: "", message: "" });
  const [contactLoading, setContactLoading] = useState(false);
  const [contactSubmitted, setContactSubmitted] = useState(false);

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    if (!contactData.name || !contactData.email || !contactData.subject || !contactData.message) {
      toast.error("Please fill in all fields");
      return;
    }
    setContactLoading(true);
    try {
      await axios.post(`${API}/contact`, contactData);
      setContactSubmitted(true);
      toast.success("Message sent successfully!");
    } catch (error) {
      toast.error("Failed to send message. Please try again.");
    } finally {
      setContactLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="about-home-link">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center" data-testid="about-brand-icon">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight hidden sm:block" style={{ fontFamily: 'Crimson Pro, serif' }} data-testid="about-brand-text">
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/success-stories" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="about-nav-success-stories">Success Stories</Link>
            <Link to="/glossary" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="about-nav-legal-terms">Legal Terms</Link>
            <Link to="/faq" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="about-nav-faq">FAQ</Link>
<Link to="/" data-testid="about-back-link">
              <Button className="landing-cta-primary" data-testid="about-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-slate-900" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="about-mobile-menu-btn">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200 px-6 py-4 space-y-3">
            <Link to="/success-stories" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="about-mobile-success-stories">Success Stories</Link>
            <Link to="/glossary" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="about-mobile-legal-terms">Legal Terms</Link>
            <Link to="/faq" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="about-mobile-faq">FAQ</Link>
            <Link to="/" className="block py-2 text-blue-700 hover:text-blue-800" data-testid="about-mobile-back-home">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="relative py-16 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="/images/stock/scales-justice.jpg" 
            alt=""
            className="w-full h-full object-cover opacity-5"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-4xl mx-auto relative z-10 text-center">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-2xl bg-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30" data-testid="about-hero-icon">
              <Heart className="w-8 h-8 text-white" />
            </div>
          </div>
          <p className="text-red-600 font-semibold text-xs uppercase tracking-widest mb-3" data-testid="about-hero-eyebrow">My Story</p>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }} data-testid="about-hero-title">
            Why I Built This App
          </h1>
          <p className="text-slate-700 text-lg max-w-2xl mx-auto" data-testid="about-hero-subtitle">
            One woman's fight for justice — built from lived experience, driven by the belief that everyone deserves to know their rights.
          </p>
        </div>
      </section>

      {/* Business Info */}
      <section className="py-8 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Deb's Personal Bio */}
          <div className="bg-white border border-slate-200 rounded-2xl p-8 mb-6 text-center" data-testid="about-deb-bio">
            <h2 className="text-2xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
              About Deb
            </h2>
            <p className="text-slate-700 text-base leading-relaxed max-w-2xl mx-auto">
              A proud single mother of four and grandmother to one, Deb King grew up in Western Sydney, Colyton 
              and has never been afraid of hard work. From TAB Limited to human resources, workplace safety, 
              training and assessment, civil construction plant operations, and painting and decorating — 
              Deb has built a career across industries that demanded resilience and grit. A 3rd Dan black 
              belt in Taekwondo, ten-year undefeated champion, and proud representative of Australia at 
              multiple World Championships — that same determination now drives her mission to help others 
              navigate the justice system.
            </p>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center" data-testid="about-business-info">
            <h2 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Criminal Law Appeal Case Management
            </h2>
            <p className="text-blue-700 font-medium">Founded by Debra King</p>
            <p className="text-slate-700 text-sm mt-2">Glenmore Park, NSW, Australia</p>
            
            <div className="mt-6 inline-block bg-blue-600 rounded-xl px-6 py-3">
              <p className="text-white text-sm font-bold">
                AUSTRALIAN LAW ONLY — Covers all States & Territories
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* My Story */}
      <section className="py-12 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center">
              <Quote className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
              My Journey
            </h2>
          </div>

          <div className="space-y-6 text-slate-700 leading-relaxed">
            <p>
              I'm not a lawyer — I'm someone who knows firsthand how isolating and confusing the justice system can be.
              <strong className="text-slate-900"> I served a considerable amount of time in prison.</strong> During that time, 
              I accepted my situation, believing I had no options. What I didn't know then was that I had appellant rights 
              — rights that were never properly explained to me.
            </p>
            
            <p>
              Legal Aid failed to help me. Like so many others, I fell through the cracks of an overburdened system 
              that offers little support once you're sentenced. I served my time not knowing what could have been challenged.
            </p>

            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
              <p className="text-emerald-800 font-medium">
                <CheckCircle className="w-5 h-5 inline mr-2 -mt-0.5" />
                <strong>It's now been eight years since I've been free from trouble.</strong>
              </p>
              <p className="text-emerald-700 mt-2 text-sm">
                In that time, I've invested years of hard work, research, and determination into building this application. 
                Every hour spent learning criminal law, every late night developing this tool — it was all driven by one goal: 
                to ensure others don't have to go through what I went through.
              </p>
            </div>

            <p>
              The reality is: from manifest injustice to denial of procedural fairness, from critical elements missed 
              at sentencing, to failures by defence counsel, errors by the judge, or simply unsafe verdicts — there are 
              <em> many</em> potential grounds that can arise in criminal matters. Unless you're a legal expert or have 
              thousands of dollars for advice, these issues often go unnoticed.
            </p>
          </div>
        </div>
      </section>

      {/* Joshua Homann's Story */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center">
              <Gavel className="w-6 h-6 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Joshua Homann — The Reason This App Exists
            </h2>
          </div>

          {/* Case Details Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 mb-8" data-testid="about-joshua-card">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
              <div>
                <h3 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  R v Joshua Homann
                </h3>
                <p className="text-slate-700 text-sm">Supreme Court of New South Wales</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-blue-700 text-white rounded-lg text-xs font-semibold">Trial 2018</span>
                <span className="px-3 py-1 bg-red-600 text-white rounded-lg text-xs font-semibold">Murder</span>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6 text-sm">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-600">Sentence:</span>
                  <span className="text-slate-900 font-semibold">30 years imprisonment</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Non-Parole Period:</span>
                  <span className="text-slate-900 font-semibold">22 years 6 months</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Time Served:</span>
                  <span className="text-blue-700 font-semibold">10+ years</span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-600">Initial Advice:</span>
                  <span className="text-red-700 font-semibold">"No appellant rights"</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Grounds Identified:</span>
                  <span className="text-red-700 font-semibold">"No grounds of merit"</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Current Status:</span>
                  <span className="text-emerald-700 font-semibold">APPEAL IN PROGRESS</span>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6 text-slate-700 leading-relaxed">
            <p>
              <strong className="text-slate-900">Josh is my best mate.</strong> He was convicted in 2018 and sentenced to 
              30 years imprisonment with a non-parole period of 22 years and 6 months. For 10 years, he was told he had 
              no appellant rights. No grounds of merit. No options. He believed it — and so did I, at first.
            </p>

            <p>
              I've dedicated the last <strong className="text-slate-900">five years</strong> to researching, analysing, and 
              reporting on Josh's case. Five years of reading transcripts, studying legislation, examining evidence, and 
              learning criminal law from the ground up. Blood, sweat, and tears went into understanding every aspect of 
              what happened to him. I've become so knowledgeable on Murder, Manslaughter, and Mens Rea that I'm confident 
              I could represent Josh myself and succeed. That's not arrogance — that's the result of years of relentless 
              dedication to finding the truth.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <p className="text-blue-800 font-medium mb-3">
                <AlertTriangle className="w-5 h-5 inline mr-2 -mt-0.5" />
                <strong>Then I built this app.</strong>
              </p>
              <p className="text-blue-700 text-sm">
                Using this very application, we analysed every document, every transcript, every piece of evidence. 
                What we found was shocking — Josh had been severely let down by the system.
              </p>
            </div>

            <p>
              The grounds we identified are severe and deny him natural justice. He was denied a judge alone trial — his 
              right to elect trial by judge alone was not properly afforded to him. There were multiple failures in 
              procedural fairness throughout the trial process. Fundamental rights that every accused person is entitled 
              to were simply not upheld. These aren't minor technicalities — these are serious breaches that go to the 
              heart of whether he received a fair trial.
            </p>

            <p>
              This app was born from that journey. But it's not just for people like Josh — it's designed to be a powerful 
              tool for <strong className="text-slate-900">lawyers and legal professionals</strong> too. When solicitors and 
              barristers are overloaded with cases, when Legal Aid is stretched beyond capacity, when there simply aren't 
              enough hours in the day to give every case the attention it deserves — this app can help. It organises, 
              analyses, and identifies issues that might otherwise be missed. What took me five years to learn, this app 
              can help accomplish in a fraction of the time.
            </p>

            <div className="bg-emerald-50 border-2 border-emerald-400 rounded-xl p-6 mt-8">
              <p className="text-emerald-800 font-bold text-lg mb-2">
                <CheckCircle className="w-6 h-6 inline mr-2 -mt-0.5" />
                Josh now has a full appeal in progress
              </p>
              <p className="text-emerald-700">
                After 10 years of being told he had no options, Josh is currently in the process of a <strong>full case appeal 
                for both conviction and sentence</strong>. From being denied a judge alone trial to failures in procedural 
                fairness — the grounds identified are severe and deny him natural justice. This app made it possible to 
                identify what the legal system failed to tell him for a decade.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Brad Fletcher's Story */}
      <section className="py-12 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Brad Fletcher — Best Mate for Life
            </h2>
          </div>

          {/* Case Details Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 mb-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Brad Fletcher
                </h3>
                <p className="text-slate-700 text-sm">Matter Pending</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-blue-700 text-white rounded-lg text-xs font-semibold">On Remand</span>
                <span className="px-3 py-1 bg-blue-700 text-white rounded-lg text-xs font-semibold">2+ Years</span>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-slate-700">Charge:</span>
                <span className="text-slate-900 font-semibold ml-2">Murder</span>
              </div>
              <div>
                <span className="text-slate-700">Status:</span>
                <span className="text-red-600 font-semibold ml-2">Awaiting Trial</span>
              </div>
            </div>
          </div>

          <div className="space-y-6 text-slate-700 leading-relaxed">
            <p>
              <strong className="text-slate-900">Brad is my best mate for life.</strong> He's been on remand for over 
              two years now, still waiting for his matter to be finalised. Two years of his life in limbo.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <p className="text-blue-800 font-medium mb-2">
                <AlertTriangle className="w-5 h-5 inline mr-2 -mt-0.5" />
                <strong>Even before trial, we've already identified strong issues.</strong>
              </p>
              <p className="text-blue-700 text-sm">
                During the proceedings, using this app to analyse the available materials, we've already found significant 
                issues that are apparent. Problems that need to be documented and tracked from day one.
              </p>
            </div>

            <p>
              Once Brad's matter is finalised, this app will be there to help him too — just like it helped Josh. 
              Every document, every inconsistency, every potential ground will be captured and analysed.
            </p>
          </div>
        </div>
      </section>

      {/* The Mission */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Why This Matters
            </h2>
          </div>

          <div className="space-y-6 text-slate-700 leading-relaxed">
            <p>
              <strong className="text-slate-900">Josh and Brad inspired me to build this.</strong> Watching them — and 
              so many others — struggle through a system that offers little help once you're sentenced or charged, 
              I knew something had to change.
            </p>

            <p>
              The legal system is complex. Appeals are complicated. And unless you have money for lawyers or get lucky 
              with Legal Aid, you're on your own. That's not justice. That's a lottery.
            </p>

            <p>
              This app exists because <strong className="text-slate-900">everyone deserves to know their rights</strong>. 
              Everyone deserves the chance to identify if something went wrong in their case. Everyone deserves access 
              to the same tools that expensive law firms use.
            </p>
          </div>

          <div className="bg-white border border-blue-200 rounded-2xl p-8 text-center mt-8" data-testid="about-mission-quote">
            <Award className="w-12 h-12 text-blue-700 mx-auto mb-4" />
            <p className="text-slate-900 text-xl font-semibold mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
              "If this tool helps even one person discover grounds they didn't know existed, my goal is accomplished."
            </p>
            <p className="text-slate-700 text-sm">
              People can change. I'm living proof of that — and I created this app to prove it.
            </p>
          </div>
        </div>
      </section>

      {/* Quote */}
      <section className="py-16 px-6 bg-white">
        <div className="max-w-3xl mx-auto text-center">
          <Quote className="w-12 h-12 text-blue-500/30 mx-auto mb-4" />
          <blockquote className="text-xl text-slate-700 italic leading-relaxed">
            "I just wanted to create something that could help others without them spending years working it out themselves. 
            Josh spent 10 years being told he had no options. Ten years. This app found multiple severe grounds in weeks. 
            That's why this exists."
          </blockquote>
          <p className="text-slate-900 font-semibold mt-4">— Debra King</p>
          <p className="text-slate-700 text-sm mt-1">Founder, Appeal Case Manager</p>
        </div>
      </section>

      {/* Contact Deb Section */}
      <section className="py-12 px-6 bg-slate-50" data-testid="about-contact-section">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                <MessageSquare className="w-7 h-7 text-white" />
              </div>
            </div>
            <p className="text-red-600 font-semibold text-xs uppercase tracking-widest mb-2">Get in Touch</p>
            <h2 className="text-3xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Contact Deb
            </h2>
            <p className="text-slate-600">
              Have a question or need help? Send a message and I'll get back to you as soon as possible.
            </p>
          </div>

          {contactSubmitted ? (
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8 text-center">
              <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-emerald-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>Message Sent!</h3>
              <p className="text-slate-600">Thanks for reaching out. Deb will get back to you as soon as possible.</p>
            </div>
          ) : (
            <form onSubmit={handleContactSubmit} className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8 space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-slate-900 mb-2">
                    <User className="w-4 h-4 text-red-600" />
                    Your Name
                  </label>
                  <Input type="text" value={contactData.name} onChange={(e) => setContactData({...contactData, name: e.target.value})} placeholder="Enter your name" className="w-full rounded-xl" data-testid="about-contact-name" />
                </div>
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-slate-900 mb-2">
                    <Mail className="w-4 h-4 text-red-600" />
                    Your Email
                  </label>
                  <Input type="email" value={contactData.email} onChange={(e) => setContactData({...contactData, email: e.target.value})} placeholder="Enter your email" className="w-full rounded-xl" data-testid="about-contact-email" />
                </div>
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-slate-900 mb-2">
                  <MessageSquare className="w-4 h-4 text-red-600" />
                  Subject
                </label>
                <Input type="text" value={contactData.subject} onChange={(e) => setContactData({...contactData, subject: e.target.value})} placeholder="What's this about?" className="w-full rounded-xl" data-testid="about-contact-subject" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-900 mb-2">Message</label>
                <Textarea value={contactData.message} onChange={(e) => setContactData({...contactData, message: e.target.value})} placeholder="Type your message here..." rows={6} className="w-full rounded-xl" data-testid="about-contact-message" />
              </div>
              <Button type="submit" disabled={contactLoading} className="w-full bg-blue-600 text-white hover:bg-blue-700 rounded-xl py-5 font-semibold" data-testid="about-contact-submit">
                {contactLoading ? (
                  <span className="flex items-center justify-center gap-2"><div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>Sending...</span>
                ) : (
                  <span className="flex items-center justify-center gap-2"><Send className="w-5 h-5" />Send Message</span>
                )}
              </Button>
            </form>
          )}

          <div className="mt-6 bg-white rounded-2xl border border-slate-200 p-5 text-center">
            <p className="text-slate-600 mb-1">You can also reach Deb directly at</p>
            <a href="mailto:djkingy79@gmail.com" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold text-lg">
              <Mail className="w-5 h-5" />
              djkingy79@gmail.com
            </a>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-12 px-6 bg-white" data-testid="about-cta-section">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Ready to Explore Your Options?
          </h2>
          <p className="text-slate-700 mb-8">
            Whether you're helping yourself, a family member, or a client — this tool is here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/" data-testid="about-cta-get-started-link">
              <Button className="landing-cta-primary" data-testid="about-cta-get-started-btn">
                Get Started Free
              </Button>
            </Link>
            <Link to="/success-stories" data-testid="about-cta-success-stories-link">
              <Button variant="outline" className="landing-cta-secondary" data-testid="about-cta-success-stories-btn">
                Read Success Stories
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Acknowledgement */}
      <section className="px-6 pb-10 bg-white" data-testid="about-acknowledgement-section">
        <div className="max-w-4xl mx-auto">
          <div className="max-w-3xl mx-auto border border-blue-800 rounded-2xl bg-blue-700 px-5 py-6 text-center shadow-lg shadow-blue-700/20" data-testid="about-acknowledgement-quote-card">
            <Quote className="w-8 h-8 text-white mx-auto mb-3" />
            <h3 className="text-base sm:text-lg font-bold uppercase tracking-[0.18em] text-white mb-3" data-testid="about-acknowledgement-heading">
              Acknowledgment
            </h3>
            <blockquote className="text-sm sm:text-base font-semibold text-white leading-relaxed" style={{ fontFamily: 'Crimson Pro, serif' }} data-testid="about-acknowledgement-quote">
              “This journey wouldn't have been possible without your support, motivation and encouragement ~ To my dear friends Renee Yates & Nigel Willett.”
            </blockquote>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
