/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, Send, ArrowLeft, CheckCircle, Mail, User, MessageSquare, Moon, Sun, Menu, X } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Link } from "react-router-dom";
import axios from "axios";
import { API } from "../App";
import { toast } from "sonner";
import { useTheme } from "../contexts/ThemeContext";

const ContactPage = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.subject || !formData.message) {
      toast.error("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/contact`, formData);
      setSubmitted(true);
      toast.success("Message sent successfully!");
    } catch (error) {
      toast.error("Failed to send message. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-card rounded-2xl shadow-xl border border-border p-8 text-center">
          <div className="w-20 h-20 bg-emerald-100 dark:bg-emerald-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h2 className="text-3xl font-bold text-foreground mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Message Sent!
          </h2>
          <p className="text-muted-foreground mb-8">
            Thanks for reaching out. Deb will get back to you as soon as possible.
          </p>
          <Link to="/">
            <Button className="bg-gradient-to-r from-red-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 rounded-xl px-8 py-5 font-semibold shadow-lg shadow-red-600/20">
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-slate-900 dark:bg-slate-950 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight hidden sm:block" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/glossary" className="text-slate-400 hover:text-white text-sm transition-colors">Legal Terms</Link>
            <Link to="/faq" className="text-slate-400 hover:text-white text-sm transition-colors">FAQ</Link>
            <Link to="/forms" className="text-slate-400 hover:text-white text-sm transition-colors">Forms</Link>
<Link to="/">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-slate-800 border-t border-slate-700 px-6 py-4 space-y-3">
            <Link to="/glossary" className="block py-2 text-slate-300 hover:text-white">Legal Terms</Link>
            <Link to="/faq" className="block py-2 text-slate-300 hover:text-white">FAQ</Link>
            <Link to="/forms" className="block py-2 text-slate-300 hover:text-white">Forms</Link>
            <Link to="/" className="block py-2 text-blue-500 hover:text-blue-400">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="relative py-16 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1423666639041-f56000c27a9a?crop=entropy&cs=srgb&fm=jpg&q=85&w=1920" 
            alt=""
            className="w-full h-full object-cover opacity-5 dark:opacity-[0.02]"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-2xl mx-auto relative z-10 text-center">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <MessageSquare className="w-8 h-8 text-white" />
            </div>
          </div>
          <p className="text-red-600 dark:text-blue-500 font-semibold text-xs uppercase tracking-widest mb-3">Get in Touch</p>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Contact Deb
          </h1>
          <p className="text-muted-foreground text-lg max-w-lg mx-auto">
            Have a question or need help? Send a message and I'll get back to you as soon as possible.
          </p>
          <Link
            to="/legal-resources"
            className="inline-flex items-center mt-4 text-sm font-semibold text-red-600 hover:text-blue-700"
            data-testid="contact-page-directory-link"
          >
            Looking for legal organisations instead? Open Legal Resources & Contacts Directory
          </Link>
        </div>
      </section>

      {/* Content */}
      <main className="max-w-2xl mx-auto px-6 pb-16">
        <form onSubmit={handleSubmit} className="bg-card rounded-2xl shadow-xl border border-border p-8 space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-foreground mb-2">
                <User className="w-4 h-4 text-red-600" />
                Your Name
              </label>
              <Input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="Enter your name"
                className="w-full rounded-xl"
                data-testid="contact-name"
              />
            </div>

            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-foreground mb-2">
                <Mail className="w-4 h-4 text-red-600" />
                Your Email
              </label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                placeholder="Enter your email"
                className="w-full rounded-xl"
                data-testid="contact-email"
              />
            </div>
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-foreground mb-2">
              <MessageSquare className="w-4 h-4 text-red-600" />
              Subject
            </label>
            <Input
              type="text"
              value={formData.subject}
              onChange={(e) => setFormData({...formData, subject: e.target.value})}
              placeholder="What's this about?"
              className="w-full rounded-xl"
              data-testid="contact-subject"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Message</label>
            <Textarea
              value={formData.message}
              onChange={(e) => setFormData({...formData, message: e.target.value})}
              placeholder="Type your message here..."
              rows={6}
              className="w-full rounded-xl"
              data-testid="contact-message"
            />
          </div>

          <Button 
            type="submit" 
            disabled={loading}
            className="w-full bg-gradient-to-r from-red-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 rounded-xl py-5 font-semibold shadow-lg shadow-red-600/20"
            data-testid="contact-submit"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Sending...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <Send className="w-5 h-5" />
                Send Message
              </span>
            )}
          </Button>
        </form>

        {/* Direct Contact Card */}
        <div className="mt-8 bg-muted/50 dark:bg-muted/20 rounded-2xl border border-border p-6 text-center">
          <p className="text-muted-foreground mb-2">
            You can also reach Deb directly at
          </p>
          <a 
            href="mailto:djkingy79@gmail.com" 
            className="inline-flex items-center gap-2 text-red-600 hover:text-blue-700 font-semibold text-lg transition-colors"
          >
            <Mail className="w-5 h-5" />
            djkingy79@gmail.com
          </a>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 dark:bg-slate-950 px-6 py-8 border-t border-slate-800">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-slate-400 text-sm">
            © 2025 Appeal Case Manager. All rights reserved.
          </p>
          <p className="text-slate-500 text-xs mt-2">
            Created by Debra King — Glenmore Park, NSW
          </p>
        </div>
      </footer>
    </div>
  );
};

export default ContactPage;
