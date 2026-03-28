import { Link } from "react-router-dom";
import { Scale } from "lucide-react";

const AppFooter = () => {
  return (
    <footer className="py-8 px-6 border-t border-slate-200 bg-white" data-testid="app-footer">
      <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6 items-start">
        <div className="flex flex-col items-center md:items-start">
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-slate-700" />
            <span className="text-slate-900 text-sm font-semibold">Appeal Case Manager</span>
          </div>
          <span className="text-slate-600 text-xs mt-1">Founded by Debra King</span>
          <span className="text-slate-600 text-xs mt-0.5">Criminal Appeal Research Tool — Australian Law Only</span>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-2">Explore</p>
          <div className="grid gap-y-1 text-xs text-slate-700">
            <Link to="/how-it-works" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-how-it-works">How It Works</Link>
            <Link to="/how-to-use" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-how-to-use">How To Use</Link>
            <Link to="/professional-summary" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-professional-summary">For Legal Professionals</Link>
            <Link to="/legal-resources" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-legal-resources">Resources & Contacts</Link>
            <Link to="/forms" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-forms">Forms & Templates</Link>
            <Link to="/lawyers" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-lawyers">Lawyer Directory</Link>
            <Link to="/contact" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-contact">Contact</Link>
            <Link to="/success-stories" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-success-stories">Success Stories</Link>
          </div>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-2">Legal</p>
          <div className="grid gap-y-1 text-xs text-slate-700">
            <Link to="/appeal-statistics" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-appeal-statistics">Appeal Statistics</Link>
            <Link to="/legal-framework" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-legal-framework">Legal Framework</Link>
            <Link to="/glossary" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-glossary">Legal Glossary</Link>
            <Link to="/faq" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-faq">FAQ</Link>
            <Link to="/contact" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-contact-legal">Contact</Link>
            <Link to="/about" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-about">About</Link>
            <Link to="/terms" className="text-slate-700 hover:text-blue-700 visited:text-slate-700" data-testid="footer-terms">Terms & Privacy</Link>
          </div>
          <p className="text-xs text-red-600 font-medium mt-3">
            Australian Law Only - Not legal advice
          </p>
          <p className="text-xs text-slate-600 mt-1">
            All results must be verified by a qualified legal professional
          </p>
        </div>
      </div>
    </footer>
  );
};

export default AppFooter;
