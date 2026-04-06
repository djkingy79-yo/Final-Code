/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, ChevronDown, ChevronRight, Search, HelpCircle, FileText, Shield, CreditCard, Users, Gavel, BookOpen } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const faqs = [
  {
    category: "Getting Started",
    icon: HelpCircle,
    color: "blue",
    image: "/images/stock/office-desk.jpg",
    questions: [
      {
        q: "What is the Appeal Case Manager?",
        a: "The Appeal Case Manager is an AI-powered tool designed to help families and supporters of convicted individuals identify potential grounds for criminal appeal. It helps organise case documents, generate timelines, and create professional reports that can be shared with legal professionals."
      },
      {
        q: "Who is this tool for?",
        a: "This tool is primarily designed for family members, friends, and supporters of people who have been convicted of criminal offences in Australia. It's also useful for law students, paralegals, and anyone researching criminal appeals. It is NOT a substitute for qualified legal advice."
      },
      {
        q: "Do I need legal experience to use this?",
        a: "No. The tool is designed to be user-friendly and explains legal concepts in plain English. However, consulting with a qualified criminal lawyer before lodging any appeal is strongly recommended."
      },
      {
        q: "Which Australian states and territories are covered?",
        a: "All of them! The tool covers NSW, Victoria, Queensland, South Australia, Western Australia, Tasmania, Northern Territory, ACT, and Federal criminal law. Each jurisdiction has specific legislation and procedures that the AI takes into account."
      }
    ]
  },
  {
    category: "Appeals Process",
    icon: Gavel,
    color: "red",
    image: "/images/stock/scales-justice.jpg",
    questions: [
      {
        q: "What are the time limits for lodging an appeal?",
        a: "Time limits vary by state and type of appeal. Generally, appeals against conviction or sentence must be lodged within 28 days of the sentence being handed down. However, courts can grant extensions in certain circumstances. Always check with a lawyer about specific deadlines."
      },
      {
        q: "What are 'grounds for appeal'?",
        a: "Grounds for appeal are the legal reasons why you believe the conviction or sentence was wrong. Common grounds include: errors in the judge's directions to the jury, fresh evidence that wasn't available at trial, inadequate legal representation, and sentencing errors."
      },
      {
        q: "Can I appeal if there's new evidence?",
        a: "Yes, fresh evidence can be grounds for appeal, but it must meet strict criteria. The evidence must: (1) not have been available at the original trial, (2) be credible, and (3) be likely to have affected the outcome. The court will decide whether to admit fresh evidence."
      },
      {
        q: "What's the difference between appealing conviction vs sentence?",
        a: "An appeal against conviction argues the person should not have been found guilty at all. An appeal against sentence accepts the conviction but argues the sentence was too harsh or legally incorrect. You can appeal both, but different grounds apply to each."
      },
      {
        q: "What happens if the appeal is successful?",
        a: "If successful, the Court of Criminal Appeal may: (1) quash the conviction entirely, (2) order a new trial, (3) substitute a lesser verdict, or (4) reduce the sentence. The outcome depends on the nature of the error found."
      },
      {
        q: "Can the prosecution appeal too?",
        a: "Yes. The Crown (prosecution) can appeal against sentences they consider too lenient. They can also appeal acquittals in limited circumstances, particularly where there's been a question of law."
      }
    ]
  },
  {
    category: "Using the Tool",
    icon: FileText,
    color: "blue",
    image: "/images/stock/library-shelves.jpg",
    questions: [
      {
        q: "What documents should I upload?",
        a: "Upload everything related to the case: court transcripts, judge's sentencing remarks, witness statements, police evidence briefs, character references, medical reports, and any other relevant documents. The more information the AI has, the better the analysis."
      },
      {
        q: "How does the AI identify grounds for appeal?",
        a: "The AI analyses your uploaded documents looking for patterns that commonly indicate appealable errors: inconsistencies in evidence, procedural irregularities, potential misdirections by the judge, and gaps in the prosecution's case. It cross-references against Australian criminal law."
      },
      {
        q: "Are the AI-generated reports legally accurate?",
        a: "The reports provide a starting point for analysis and highlight potential issues. However, they are generated by AI and may contain errors or miss important nuances. Always have a qualified lawyer review any AI-generated analysis before taking legal action."
      },
      {
        q: "Can I edit the timeline and grounds?",
        a: "Yes. The AI generates initial suggestions, but you can add, edit, or remove timeline events and grounds of merit. You know your case best - use the AI as a starting point and refine from there."
      },
      {
        q: "What file formats are supported?",
        a: "You can upload PDF, DOCX, DOC, TXT, and image files (JPG, PNG). For scanned documents, the OCR technology extracts the text automatically. Maximum file size is 50MB per document."
      },
      {
        q: "How does the OCR (text extraction) work?",
        a: "OCR (Optical Character Recognition) automatically converts scanned documents and images into searchable text. This allows the AI to analyse documents that are photos or scans of paper documents."
      }
    ]
  },
  {
    category: "Reports & Analysis",
    icon: BookOpen,
    color: "purple",
    image: "/images/stock/handshake.jpg",
    questions: [
      {
        q: "What's included in a Quick Summary Report?",
        a: "The Quick Summary (FREE) has 7 sections: Case Snapshot, Primary Issues Identified, Top Potential Grounds (preview), Key Legislation & Similar Cases (preview), Sentencing Overview with comparison table, Appeal Outlook, and What the Paid Reports Add. It's 1,500-2,200 words of real analysis — perfect for initial assessment."
      },
      {
        q: "What's included in a Full Detailed Report?",
        a: "The Full Detailed Report ($150 AUD) has 15 sections: Executive Brief, Forensic Case Chronology, Document Evidence Digest, Grounds of Merit Portfolio (with Crown response and rebuttal strategy), Comparative Sentencing Table (8+ cases), Common Appeal Grounds, Outcome Options Matrix, Evidentiary Gaps & Remediation Checklist, Precedent Matrix (10-12 cases), Statutory Framework Map, Argument Strategy per Ground, Submissions Blueprint (written + oral), Filing Guide with Required Forms, Prioritised Action Plan, and Client Plain-English Brief. Target: 4,500-6,500 words."
      },
      {
        q: "What's included in an Extensive Log Report?",
        a: "The Extensive Log ($200 AUD) is the most comprehensive option with 20 sections. It includes everything in the Full Detailed Report plus 5 exclusive sections: Hearing Preparation Notes (anticipated bench questions and responses), Barrister Conference Pack (authorities shortlist, orders sought, case strengths/weaknesses), Court Pathway Operations Playbook (filing sequence per court level), Similar Case Search Options (tailored AustLII search strings), and Risk Assessment with Contingency Planning per ground. Features 300+ words per ground, 12+ sentencing comparisons, and 15+ precedent cases. Target: 7,000-10,000 words."
      },
      {
        q: "Can I share reports with my lawyer?",
        a: "Yes! Reports can be downloaded as PDF and shared with anyone. The professional formatting makes them suitable for review by barristers, solicitors, and legal aid services."
      }
    ]
  },
  {
    category: "Payments & Pricing",
    icon: CreditCard,
    color: "emerald",
    image: "/images/stock/calculator.jpg",
    questions: [
      {
        q: "What does the free version include?",
        a: "Free features include: unlimited document uploads, AI-generated timeline, Quick Summary reports, appeal progress checklist, and the legal glossary. You can manage your entire case without paying."
      },
      {
        q: "What are the paid features?",
        a: "Paid features include: Grounds of Merit Details ($99 AUD) for in-depth analysis of each appeal ground with legal citations, Full Detailed Reports ($150 AUD) with 15 sections covering grounds portfolio, sentencing tables, outcome options, submissions blueprint, and filing guide, and Extensive Log Reports ($200 AUD) with 20 sections including 5 exclusive sections for hearing prep, barrister conference pack, court playbook, search options, and risk assessment."
      },
      {
        q: "Is my payment secure?",
        a: "Yes. All payments are processed via PayID bank transfer — Australia's instant payment system. Funds go directly to the verified account."
      },
      {
        q: "Can I get a refund?",
        a: "Due to the nature of AI-generated content, refunds are generally not available once a report has been generated. If you experience technical issues preventing report delivery, please contact us."
      },
      {
        q: "Are there any hidden fees?",
        a: "No. You only pay for the specific reports or features you choose. There are no subscriptions, no monthly fees, and no hidden charges. Pay only for what you need."
      }
    ]
  },
  {
    category: "Privacy & Security",
    icon: Shield,
    color: "slate",
    image: "/images/stock/laptop-work.jpg",
    questions: [
      {
        q: "Is my case information confidential?",
        a: "Yes. Case data is stored securely and is only accessible to the account holder. Individual case information is not shared with anyone. Aggregated, anonymised statistics may be used to improve the service."
      },
      {
        q: "Who can see my documents?",
        a: "Only you can see your uploaded documents and case details. The system processes documents automatically - no humans review your files unless you specifically request support assistance."
      },
      {
        q: "Can I delete my data?",
        a: "Yes. Individual documents, notes, or entire cases can be deleted at any time. Deleted data is permanently removed from the systems within 30 days."
      },
      {
        q: "Where is my data stored?",
        a: "Data is stored on secure servers with industry-standard encryption. Data security is taken seriously and best practices are implemented to protect all information."
      }
    ]
  },
  {
    category: "Getting Legal Help",
    icon: Users,
    color: "orange",
    image: "/images/stock/legal-library.jpg",
    questions: [
      {
        q: "How do I find a criminal appeal lawyer?",
        a: "Check the Lawyer Directory page for links to criminal appeal specialists in each state. You can also contact your state's Legal Aid office, Law Society, or Bar Association for referrals."
      },
      {
        q: "What is Legal Aid and am I eligible?",
        a: "Legal Aid provides free or low-cost legal help to people who can't afford a private lawyer. Eligibility depends on your income, assets, and the nature of your case. Each state has different criteria - contact your local Legal Aid office for a means test."
      },
      {
        q: "What are Pro Bono services?",
        a: "Pro Bono means 'for the public good' - it's free legal work done by private lawyers and barristers. Many law firms and individual barristers take on appeal cases pro bono. Contact your state Bar Association or organisations like Justice Connect."
      },
      {
        q: "Can this tool replace a lawyer?",
        a: "No. This tool helps you organise information and identify potential issues, but it cannot replace qualified legal advice. Criminal appeals are complex and the consequences of errors are serious. Always consult a lawyer before taking any legal action."
      }
    ]
  },
  {
    category: "Forms & Filing",
    icon: FileText,
    color: "blue",
    image: "/images/stock/office-desk.jpg",
    questions: [
      {
        q: "How do I fill in a Notice of Intention to Appeal?",
        a: "A Notice of Intention to Appeal is the first document lodged to start the appeal process. It typically requires: the appellant's full name and custody details, the court where the conviction or sentence was handed down, the date of conviction and/or sentence, the offence(s) and the sentence imposed, and a brief indication of the ground(s) of appeal. Most states provide a standard form — check the Forms & Templates page for the correct form for your jurisdiction. File the completed form at the relevant court registry within the required time limit (usually 28 days)."
      },
      {
        q: "What details do I need to complete a Notice of Appeal?",
        a: "A Notice of Appeal (the formal appeal document, as distinct from the Notice of Intention) requires more detail. It must include: the appellant's full legal name and address, the indictment number or case reference, the date and place of trial, the name of the trial judge, the offence(s) of which the appellant was convicted, the sentence imposed, and — most importantly — the specific grounds of appeal set out in numbered paragraphs. Each ground should clearly state the alleged error (e.g., 'The learned trial judge erred in directing the jury that…'). The grounds should be concise but precise. Attach any supporting affidavits or additional evidence if required."
      },
      {
        q: "How do I request trial transcripts?",
        a: "To request trial transcripts, complete a Transcript Request Form (available on the Forms & Templates page or from the court registry). The form requires: the case name and number, the court and date of hearing, the specific portions of transcript required (e.g., judge's summing up, specific witness evidence, sentencing remarks), and the reason for the request (appeal purposes). Lodge the completed form with the court registry. Transcript fees apply — check current rates with the court. If the appellant cannot afford the fees, an application for fee waiver may be made on the grounds of financial hardship."
      },
      {
        q: "What is a Case Stated and how do I fill one in?",
        a: "A Case Stated is used when a specific question of law needs to be referred to a higher court for determination. The form requires: a clear and concise statement of the facts of the case, the specific question of law to be determined, the submissions of both parties on the question, and any relevant legislation or case law. Cases Stated are relatively rare and usually prepared by legal practitioners. It is strongly recommended to seek legal advice before attempting to file one."
      },
      {
        q: "How do I request access to exhibits from my trial?",
        a: "To access court exhibits, complete an Exhibit Access Request form (available on the Forms & Templates page). The form requires: the case name and number, the date of trial and the presiding judge, a list of the specific exhibits being sought (by exhibit number if known), and the reason for access (appeal preparation). Note that exhibits are court property and may only be viewed under supervision at the court registry. Some exhibits may have been destroyed after retention periods have expired. Photographs or copies may be permitted at the court's discretion."
      },
      {
        q: "What are the time limits for filing appeal forms?",
        a: "Time limits vary by jurisdiction but are strictly enforced. In most Australian states and territories, a Notice of Intention to Appeal must be filed within 28 days of the date of conviction or sentence. In some jurisdictions the period may differ — for example, the ACT allows 28 days, while Federal matters may have different timeframes. If the deadline has passed, an application for extension of time must be filed explaining the reasons for the delay. Courts will consider factors such as the length of the delay, the reasons for it, and the merits of the proposed appeal. Filing late without an extension application will result in the appeal being dismissed."
      },
      {
        q: "Can I file appeal forms online or do I need to go to the court?",
        a: "This depends on the jurisdiction. Some courts now accept electronic filing — for example, NSW and Victoria have online filing systems for certain documents. Others require physical filing at the court registry. Check the relevant court's website or contact the registry directly. When filing in person, bring the original and at least two copies (one for the court, one for the prosecution, and one for your own records). Some courts also require filing fees — enquire about current fees and any available fee waivers."
      },
      {
        q: "Do I need to serve documents on the prosecution?",
        a: "Yes. After filing appeal documents with the court, copies must be served on the Director of Public Prosecutions (DPP) or the relevant prosecuting authority. This is a mandatory step — failure to serve can result in the appeal being struck out. The method of service (personal, post, or electronic) varies by jurisdiction. Proof of service (usually an affidavit of service) must then be filed with the court registry. The Forms & Templates page includes a template Affidavit of Service."
      },
      {
        q: "What if I make a mistake on a form?",
        a: "Minor errors (such as a typo in an address) can usually be corrected by filing an amended form with the court registry. More significant errors in the grounds of appeal can be corrected by filing amended grounds, but this generally requires the court's leave (permission). It is better to take time to get the form right before filing. If unsure about any section, seek legal advice or contact the court registry — registry staff can advise on procedural requirements (though they cannot give legal advice about the content of your grounds)."
      }
    ]
  }
];

const FAQPage = () => {

  const [searchQuery, setSearchQuery] = useState("");
  const [openItems, setOpenItems] = useState({});
  const [activeCategory, setActiveCategory] = useState("all");

  const toggleItem = (categoryIndex, questionIndex) => {
    const key = `${categoryIndex}-${questionIndex}`;
    setOpenItems(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const getFilteredFaqs = () => {
    let filtered = faqs;
    
    if (activeCategory !== "all") {
      filtered = faqs.filter(cat => cat.category === activeCategory);
    }
    
    if (searchQuery) {
      filtered = filtered.map(category => ({
        ...category,
        questions: category.questions.filter(
          q => q.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
               q.a.toLowerCase().includes(searchQuery.toLowerCase())
        )
      })).filter(category => category.questions.length > 0);
    }
    
    return filtered;
  };

  const filteredFaqs = getFilteredFaqs();
  const totalQuestions = faqs.reduce((sum, cat) => sum + cat.questions.length, 0);

  const colorClasses = {
    blue_mapped: "bg-blue-700 text-white",
    red: "bg-red-600 text-white",
    blue: "bg-blue-700 text-white",
    purple: "bg-purple-700 text-white",
    emerald: "bg-emerald-700 text-white",
    slate: "bg-slate-700 text-white",
    orange: "bg-orange-600 text-white",
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center" data-testid="faq-brand-icon">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight" style={{ fontFamily: 'Crimson Pro, serif' }} data-testid="faq-brand-text">
              Appeal Case Manager
            </span>
          </div>
          <div className="flex items-center gap-3">
<Link to="/" data-testid="faq-back-link">
              <Button className="landing-cta-primary" data-testid="faq-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero with Image */}
      <section className="relative py-16 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="/images/stock/scales-justice.jpg" 
            alt="Lady Justice"
            className="w-full h-full object-cover opacity-10"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="w-20 h-20 rounded-2xl bg-blue-700 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-500/30" data-testid="faq-hero-icon">
            <HelpCircle className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }} data-testid="faq-hero-title">
            Frequently Asked Questions
          </h1>
          <p className="text-sm text-slate-700 max-w-2xl mx-auto mb-2" data-testid="faq-hero-subtitle">
            Find answers to common questions about criminal appeals and using the Appeal Case Manager.
          </p>
          <p className="text-sm text-slate-700" data-testid="faq-hero-count">
            <strong>{totalQuestions} answers</strong> across {faqs.length} categories
          </p>
          
          {/* Search */}
          <div className="max-w-xl mx-auto mt-8 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-700" />
            <Input
              type="text"
              placeholder="Search for any question..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 py-4 text-sm rounded-xl border-2 focus:border-blue-500"
              data-testid="faq-search"
            />
          </div>
        </div>
      </section>

      {/* Category Filter */}
      <section className="px-6 pb-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-wrap justify-center gap-3">
            <button
              onClick={() => setActiveCategory("all")}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeCategory === "all"
                  ? "bg-blue-700 text-white shadow-lg"
                  : "bg-white border border-slate-200 text-slate-700 hover:border-blue-500"
              }`}
              data-testid="faq-filter-all"
            >
              All Questions ({totalQuestions})
            </button>
            {faqs.map(cat => (
              <button
                key={cat.category}
                onClick={() => setActiveCategory(cat.category)}
                data-testid={`faq-filter-${cat.category.toLowerCase().replace(/\s+/g, '-')}`}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                  activeCategory === cat.category
                    ? "bg-blue-700 text-white shadow-lg"
                    : "bg-white border border-slate-200 text-slate-700 hover:border-blue-500"
                }`}
              >
                <cat.icon className="w-4 h-4" />
                {cat.category}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Content */}
      <main className="max-w-5xl mx-auto px-6 pb-16">
        <section className="mb-6" data-testid="faq-content-intro">
          <p className="text-xs uppercase tracking-widest text-blue-700 font-semibold mb-1">Quick Answers</p>
          <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Browse by category or expand individual questions
          </h2>
        </section>

        {filteredFaqs.length === 0 ? (
          <Card className="p-12 text-center">
            <Search className="w-12 h-12 text-slate-700 mx-auto mb-4" />
            <p className="text-slate-900 font-semibold">No questions found matching "{searchQuery}"</p>
            <p className="text-slate-700 text-sm mt-2">Try a different search term</p>
          </Card>
        ) : (
          <div className="space-y-6">
            {filteredFaqs.map((category, categoryIndex) => (
              <div key={categoryIndex}>
                {/* Category Heading — clearly visible */}
                <div className="flex items-center gap-3 mb-4 mt-2 pb-3 border-b-2 border-blue-600" data-testid={`faq-category-header-${category.category.toLowerCase().replace(/\s+/g, '-')}`}>
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    category.color === 'blue' ? 'bg-blue-100' :
                    category.color === 'red' ? 'bg-red-100' :
                    category.color === 'purple' ? 'bg-purple-100' :
                    category.color === 'emerald' ? 'bg-emerald-100' :
                    category.color === 'orange' ? 'bg-amber-100' :
                    category.color === 'teal' ? 'bg-teal-100' :
                    'bg-slate-100'
                  }`} data-testid={`faq-category-icon-${category.category.toLowerCase().replace(/\s+/g, '-')}`}>
                    <category.icon className={`w-5 h-5 ${
                      category.color === 'blue' ? 'text-blue-700' :
                      category.color === 'red' ? 'text-red-700' :
                      category.color === 'purple' ? 'text-purple-700' :
                      category.color === 'emerald' ? 'text-emerald-700' :
                      category.color === 'orange' ? 'text-amber-700' :
                      category.color === 'teal' ? 'text-teal-700' :
                      'text-slate-700'
                    }`} />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                      {category.category}
                    </h2>
                    <p className="text-slate-500 text-xs">
                      {category.questions.length} questions
                    </p>
                  </div>
                </div>
                
                {/* Questions */}
                <div className="space-y-3">
                  {category.questions.map((item, questionIndex) => {
                    const isOpen = openItems[`${categoryIndex}-${questionIndex}`];
                    return (
                      <div 
                        key={questionIndex}
                        className="bg-white border border-slate-200 rounded-xl overflow-hidden hover:shadow-lg hover:border-blue-500/30 transition-all"
                      >
                        <button
                          onClick={() => toggleItem(categoryIndex, questionIndex)}
                          className="w-full px-5 py-4 flex items-center justify-between text-left"
                          data-testid={`faq-${categoryIndex}-${questionIndex}`}
                        >
                          <span className="font-medium text-sm text-slate-900 pr-4">{item.q}</span>
                          <div className={`p-2 rounded-lg transition-colors flex-shrink-0 ${isOpen ? 'bg-blue-100' : 'bg-white border border-slate-200'}`}>
                            {isOpen ? (
                              <ChevronDown className="w-5 h-5 text-red-600" />
                            ) : (
                              <ChevronRight className="w-5 h-5 text-slate-700" />
                            )}
                          </div>
                        </button>
                        {isOpen && (
                          <div className="px-5 pb-4">
                            <div className="bg-white border border-slate-200/50 rounded-xl p-4 border-l-4 border-blue-500">
                              <p className="text-slate-700 text-xs leading-relaxed">{item.a}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Still have questions */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
          <h3 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Still have questions?
          </h3>
          <p className="text-base text-slate-700 mb-3">
            Can't find what you're looking for? The Legal Glossary may help.
          </p>
          <div className="flex flex-wrap gap-2 justify-center">
            <Link to="/contact" data-testid="faq-contact-link">
              <Button className="bg-blue-700 text-white hover:bg-blue-800 text-xs px-4 py-2" data-testid="faq-contact-btn">
                Contact Us
              </Button>
            </Link>
            <Link to="/glossary" data-testid="faq-glossary-link">
              <Button variant="outline" className="text-xs px-4 py-2 border-blue-300 text-blue-700 hover:bg-blue-100" data-testid="faq-glossary-btn">
                Legal Glossary
              </Button>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default FAQPage;
