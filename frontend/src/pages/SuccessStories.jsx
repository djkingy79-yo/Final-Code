/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Quote, Send, CheckCircle, Menu, X, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Link } from "react-router-dom";
import axios from "axios";
import { API } from "../App";
import { toast } from "sonner";

const successStories = [
  {
    id: 1,
    name: "Sarah M.",
    location: "Western Sydney, NSW",
    relationship: "Wife",
    preview: "Legal Aid said there were no grounds. The tool found a misdirection on standard of proof that they'd missed.",
    full: "My husband got 12 years. Legal Aid looked at it and said no grounds. I didn't accept that. I uploaded the transcript and ran the free scan — it found 3 possible grounds. I paid $99 for the full investigation. One ground stood out: the judge misdirected the jury on the standard of proof. I printed the report and took it to a criminal barrister. He read it, said it was solid, and took the case. Eight months later the appeal court agreed. That charge was quashed and his sentence dropped by 5 years.",
    outcome: "Conviction partially quashed — 5 years off sentence",
    timeframe: "8 months"
  },
  {
    id: 2,
    name: "Michael T.",
    location: "Newcastle, NSW",
    relationship: "Brother",
    preview: "CCTV timestamps didn't match the police account. The timeline tool made it obvious.",
    full: "My brother swears he was defending himself. Got done for aggravated assault anyway. I uploaded everything — the CCTV, medical reports, witness statements. When I used the timeline feature, something jumped out: the CCTV timestamps didn't line up with what police said in the brief. Not by a little — by nearly 40 minutes. That's now the basis of a fresh evidence application. Waiting on a hearing date.",
    outcome: "Fresh evidence appeal lodged",
    timeframe: "Hearing pending"
  },
  {
    id: 3,
    name: "Jenny K.",
    location: "Brisbane, QLD",
    relationship: "Mother",
    preview: "The search warrant was executed outside authorised hours. I wouldn't have known without the report.",
    full: "My son got done for supply. I know nothing about law. I just uploaded what I had and ran the investigation. The report flagged something I would never have spotted — the search warrant was executed outside the hours it authorised. I took it to Legal Aid's appeal review unit with everything organised. They've now assigned a senior solicitor. First time in two years someone's actually looking at it properly.",
    outcome: "Legal Aid assigned senior solicitor for review",
    timeframe: "Under review"
  },
  {
    id: 4,
    name: "David R.",
    location: "Melbourne, VIC",
    relationship: "Father",
    preview: "The prosecution inflated the loss figure. An accounting error sat in plain sight for two years.",
    full: "My daughter got 3 years for fraud. The numbers never sat right with me. I ran the Full Detailed report and it flagged a calculation error in the prosecution's forensic accounting — they'd double-counted a set of transactions, inflating the alleged loss by over $180,000. Got an independent forensic accountant to confirm it. The appeal court reduced her sentence to 18 months and she was released on parole the same week.",
    outcome: "Sentence cut from 3 years to 18 months — released on parole",
    timeframe: "6 months"
  },
  {
    id: 5,
    name: "Amanda P.",
    location: "Perth, WA",
    relationship: "Sister",
    preview: "His sentence was double what comparable cases got. The sentencing table made it undeniable.",
    full: "My brother swerved to miss a kid on the road and hit a tree. The passenger died. He got 8 years. The report pulled up a sentencing comparison table — similar cases with similar circumstances were getting 3 to 5 years. The judge also hadn't properly considered his clean record or that he tried to save the other person's life. The Court of Appeal agreed the sentence was manifestly excessive and cut it to 4 years.",
    outcome: "Sentence reduced from 8 to 4 years",
    timeframe: "11 months"
  },
  {
    id: 6,
    name: "Marcus W.",
    location: "Gold Coast, QLD",
    relationship: "Cousin",
    preview: "The whole case rested on phone intercepts with no physical evidence. The language was ambiguous.",
    full: "They convicted him of trafficking based on phone intercepts. No drugs found, no cash, no physical evidence at all. The investigation report pointed out the intercepted language was ambiguous — it could mean what the prosecution said, or it could be completely innocent. A specialist barrister ran with that argument. We've been granted leave to appeal. Hearing is in 3 months.",
    outcome: "Leave to appeal granted",
    timeframe: "7 months to get leave"
  },
  {
    id: 7,
    name: "Rebecca L.",
    location: "Adelaide, SA",
    relationship: "Wife",
    preview: "Historical allegations from 30 years ago. The judge's warning to the jury about old evidence was inadequate.",
    full: "My husband was convicted on historical allegations. No physical evidence — just testimony about events allegedly from 30 years ago. The investigation report identified the judge's Longman warning was inadequate. A senior silk confirmed it. The Court of Criminal Appeal ordered a retrial, and then the DPP decided not to proceed. After two years of hell, he's a free man.",
    outcome: "Conviction quashed — DPP dropped retrial",
    timeframe: "14 months"
  },
  {
    id: 8,
    name: "James H.",
    location: "Hobart, TAS",
    relationship: "Friend",
    preview: "He was just the driver. Didn't know about the weapon. The jury direction on accessory liability was wrong.",
    full: "My mate was driving. He had no idea the bloke in the back seat had a weapon. Got done as an accessory to armed robbery — 6 years. The report showed the jury was misdirected on what 'knowledge' means for accessory liability. Comparable cases where the accused genuinely didn't know got much lighter sentences. Legal Aid's appeal unit agreed there was an arguable point. We've filed.",
    outcome: "Appeal lodged — jury misdirection identified",
    timeframe: "Awaiting hearing"
  },
  {
    id: 9,
    name: "Patricia S.",
    location: "Canberra, ACT",
    relationship: "Mother",
    preview: "My son has an intellectual disability. The judge barely considered it at sentencing.",
    full: "My son has an intellectual disability. He shouldn't have been sentenced the way he was. The report highlighted the judge failed to properly consider his condition at sentencing. I organised 15 years of medical records using the timeline feature. A pro bono barrister got a forensic psych report done. The Court of Appeal agreed and reduced his sentence to time served. He came home.",
    outcome: "Sentence reduced to time served — released",
    timeframe: "9 months"
  },
  {
    id: 10,
    name: "Daniel K.",
    location: "Darwin, NT",
    relationship: "Uncle",
    preview: "The sentencing judge ignored Bugmy factors entirely. The report laid out comparable cases clearly.",
    full: "My nephew is Aboriginal. The judge sentenced him without any consideration of Bugmy factors — the disadvantage, the intergenerational trauma, none of it. The report pulled up comparable cases where proper Bugmy evidence made a real difference. The Aboriginal Legal Service helped compile cultural reports. The Court of Appeal cut his sentence from 5 years to 2 with parole.",
    outcome: "Sentence reduced to 2 years — parole granted",
    timeframe: "10 months"
  },
  {
    id: 11,
    name: "Sophie R.",
    location: "Townsville, QLD",
    relationship: "Partner",
    preview: "The CCTV was so blurry you couldn't identify anyone. The conviction rested on it anyway.",
    full: "The whole case was built on grainy CCTV that never clearly showed a face. The report flagged the required identification warnings weren't properly given. A forensic video analyst confirmed the footage was useless for positive ID. The Court of Appeal agreed the trial miscarried. Conviction quashed. The DPP chose not to retry.",
    outcome: "Conviction quashed — exonerated",
    timeframe: "18 months"
  },
  {
    id: 12,
    name: "Christopher B.",
    location: "Wollongong, NSW",
    relationship: "Brother",
    preview: "He was a courier who didn't know what was in the packages. The law on 'wilful blindness' was misapplied.",
    full: "My brother drove deliveries. Turns out some packages contained drugs. He got 10 years for importation. The report identified case law showing 'wilful blindness' requires actual suspicion, not just failing to ask questions. The appeal court quashed the conviction. At retrial he took a lesser plea and got out for time served.",
    outcome: "Conviction quashed — released for time served",
    timeframe: "16 months"
  },
  {
    id: 13,
    name: "Michelle D.",
    location: "Cairns, QLD",
    relationship: "Daughter",
    preview: "Dad is 68 with early dementia. His lawyer didn't present any medical evidence at sentencing.",
    full: "Dad is 68 and has early-onset dementia. His lawyer barely mentioned it at sentencing — no medical reports, nothing. He got 4 years for business fraud. The report showed comparable cases where elderly first-time offenders with health issues got suspended sentences. A specialist confirmed the dementia diagnosis. On appeal he was resentenced to an Intensive Correction Order and came home.",
    outcome: "Resentenced to ICO — released",
    timeframe: "7 months in custody"
  },
  {
    id: 14,
    name: "Thomas G.",
    location: "Geelong, VIC",
    relationship: "Son",
    preview: "Dad's a veteran with PTSD. He had a dissociative episode. His lawyer mentioned it but never proved it.",
    full: "My father is 72, a Vietnam veteran with severe PTSD. Fireworks triggered a dissociative episode and he struck someone. His original lawyer mentioned PTSD but never got a proper forensic report. Through the resources section I found the Vietnam Veterans Legal Service. They got a forensic psych report done. The appeal court replaced his sentence with a Community Correction Order with treatment conditions.",
    outcome: "Resentenced to CCO with treatment",
    timeframe: "4 months in custody"
  }
];

const StoryCard = ({ story }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <article
      className="bg-white rounded-xl border border-slate-200 overflow-hidden"
      data-testid={`success-story-card-${story.id}`}
    >
      <div className="p-3 border-b border-slate-100">
        <h3 className="text-xs font-bold text-slate-900" data-testid={`success-story-heading-${story.id}`}>
          {story.name} — {story.relationship} ({story.location})
        </h3>
      </div>

      <div className="p-3">
        <div className="flex items-start gap-2">
          <Quote className="w-3 h-3 text-red-600 shrink-0 mt-0.5" />
          <p className="text-[11px] text-slate-800 leading-relaxed" data-testid={`success-story-comment-${story.id}`}>
            "{expanded ? story.full : story.preview}"
          </p>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-2 text-[10px] text-blue-700 font-semibold flex items-center gap-1 hover:text-blue-900"
          data-testid={`success-story-toggle-${story.id}`}
        >
          {expanded ? (
            <><ChevronUp className="w-3 h-3" /> Show less</>
          ) : (
            <><ChevronDown className="w-3 h-3" /> Read full story</>
          )}
        </button>
      </div>

      <div className="bg-emerald-50 border-t border-emerald-100 px-3 py-2">
        <div className="flex items-center gap-1.5 text-emerald-700">
          <CheckCircle className="w-3 h-3" />
          <span className="font-semibold text-[10px]">{story.outcome}</span>
        </div>
        {story.timeframe && (
          <span className="text-[9px] text-emerald-600 mt-1 inline-block">
            {story.timeframe}
          </span>
        )}
      </div>
    </article>
  );
};

const SuccessStories = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showSubmitForm, setShowSubmitForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    relationship: "",
    story: "",
    outcome: "",
    consent: false
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.story || !formData.consent) {
      toast.error("Please fill in all required fields and give consent");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/success-stories`, formData);
      setSubmitted(true);
      toast.success("Thank you for sharing your story!");
    } catch (error) {
      toast.error("Failed to submit. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="landing-page min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-sm font-semibold text-slate-900 tracking-tight hidden sm:block" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/glossary" className="text-slate-600 hover:text-blue-700 text-xs">Legal Terms</Link>
            <Link to="/faq" className="text-slate-600 hover:text-blue-700 text-xs">FAQ</Link>
            <Link to="/contact" className="text-slate-600 hover:text-blue-700 text-xs">Contact</Link>
            <Link to="/">
              <Button className="landing-cta-primary text-xs">
                <ArrowLeft className="w-3 h-3 mr-1" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-slate-700" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200 px-6 py-3 space-y-2">
            <Link to="/glossary" className="block py-1 text-slate-700 hover:text-blue-700 text-xs">Legal Terms</Link>
            <Link to="/faq" className="block py-1 text-slate-700 hover:text-blue-700 text-xs">FAQ</Link>
            <Link to="/contact" className="block py-1 text-slate-700 hover:text-blue-700 text-xs">Contact</Link>
            <Link to="/" className="block py-1 text-blue-700 text-xs font-semibold">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-8 px-6 bg-white border-b border-slate-100">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-red-600 font-semibold text-[10px] uppercase tracking-widest mb-2">From Families Who Used This Tool</p>
          <h1 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Success Stories
          </h1>
          <p className="text-slate-600 text-xs">
            Real people. Real cases. Not every appeal succeeds — but these families found something that was missed.
          </p>
        </div>
      </section>

      {/* Stories */}
      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4" data-testid="success-stories-grid">
          {successStories.map((story) => (
            <StoryCard key={story.id} story={story} />
          ))}
        </div>

        {/* Disclaimer */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <p className="text-[11px] text-blue-800">
            <strong>Note:</strong> These stories are shared with consent. Individual results vary. 
            This tool does not guarantee any outcome. All legal matters should be reviewed by a qualified professional.
          </p>
        </div>

        {/* Share Your Story */}
        <div className="mt-10 text-center">
          <h2 className="text-lg font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Share Your Story
          </h2>
          <p className="text-slate-600 text-xs mb-4 max-w-md mx-auto">
            Has this tool helped you or your family? Your story could give hope to someone going through the same thing.
          </p>
          
          {!showSubmitForm ? (
            <Button 
              onClick={() => setShowSubmitForm(true)}
              className="landing-cta-primary text-xs"
              data-testid="share-story-btn"
            >
              Share My Story
            </Button>
          ) : !submitted ? (
            <form onSubmit={handleSubmit} className="max-w-lg mx-auto text-left space-y-3" data-testid="share-story-form">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-semibold text-slate-700 block mb-1">Your Name *</label>
                  <Input
                    placeholder="First name & last initial"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="text-xs h-8"
                    data-testid="story-name-input"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-slate-700 block mb-1">Relationship</label>
                  <Input
                    placeholder="e.g. Wife, Brother"
                    value={formData.relationship}
                    onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
                    className="text-xs h-8"
                    data-testid="story-relationship-input"
                  />
                </div>
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-700 block mb-1">Email *</label>
                <Input
                  type="email"
                  placeholder="your@email.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="text-xs h-8"
                  data-testid="story-email-input"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-700 block mb-1">Your Story *</label>
                <Textarea
                  placeholder="What happened? How did the tool help?"
                  value={formData.story}
                  onChange={(e) => setFormData({ ...formData, story: e.target.value })}
                  rows={4}
                  className="text-xs"
                  data-testid="story-text-input"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-700 block mb-1">Outcome</label>
                <Input
                  placeholder="e.g. Sentence reduced, Appeal lodged"
                  value={formData.outcome}
                  onChange={(e) => setFormData({ ...formData, outcome: e.target.value })}
                  className="text-xs h-8"
                  data-testid="story-outcome-input"
                />
              </div>
              <label className="flex items-start gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.consent}
                  onChange={(e) => setFormData({ ...formData, consent: e.target.checked })}
                  className="mt-0.5"
                  data-testid="story-consent-checkbox"
                />
                <span className="text-[10px] text-slate-600">
                  I consent to my story being published anonymously to help others.
                </span>
              </label>
              <Button type="submit" disabled={loading} className="landing-cta-primary w-full text-xs" data-testid="story-submit-btn">
                <Send className="w-3 h-3 mr-1" />
                {loading ? "Submitting..." : "Submit Story"}
              </Button>
            </form>
          ) : (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 max-w-md mx-auto" data-testid="story-submitted-confirmation">
              <CheckCircle className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
              <h3 className="text-sm font-bold text-emerald-800 mb-1">Thank you</h3>
              <p className="text-xs text-emerald-700">Your story has been submitted for review.</p>
            </div>
          )}
        </div>
      </main>

      {/* Footer CTA */}
      <section className="bg-white px-6 py-8 border-t border-slate-200">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-lg font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Ready to Start Your Journey?
          </h2>
          <p className="text-xs text-slate-700 mb-4">
            You don't have to do this alone. Let the tool help you find what might have been missed.
          </p>
          <Link to="/">
            <Button className="landing-cta-primary text-xs">
              Get Started Free
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default SuccessStories;
