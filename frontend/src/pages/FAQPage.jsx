/* DO NOT UNDO — FAQPage section. All features in this file are approved and must be preserved. */
import { useState } from "react";
import { Scale, ArrowLeft, ChevronDown, ChevronRight, Search, HelpCircle, FileText, Clock, Shield, CreditCard, Users, Gavel, Moon, Sun, MessageCircle, BookOpen } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent } from "../components/ui/card";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const faqs = [
  {
    category: "Getting Started",
    icon: HelpCircle,
    color: "blue",
    image: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=150&fit=crop",
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
        a: "No. The tool is designed to be user-friendly and explains legal concepts in plain English. However, we strongly recommend consulting with a qualified criminal lawyer before lodging any appeal."
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
    image: "https://images.unsplash.com/photo-1589578527966-fdac0f44566c?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=150&fit=crop",
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
    image: "https://images.unsplash.com/photo-1568667256549-094345857637?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=150&fit=crop",
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
        a: "You can upload PDF, DOCX, DOC, TXT, and image files (JPG, PNG). For scanned documents, our OCR technology extracts the text automatically. Maximum file size is 50MB per document."
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
    image: "https://images.unsplash.com/photo-1619771914272-e3c1e5e4e5e3?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=150&fit=crop",
    questions: [
      {
        q: "What's included in a Quick Summary Report?",
        a: "The Quick Summary (FREE) includes: case overview, key timeline events, number of potential grounds identified, overall case strength assessment, and next steps recommendations. It's perfect for initial assessment."
      },
      {
        q: "What's included in a Full Detailed Report?",
        a: "The Full Detailed Report ($29) includes everything in Quick Summary PLUS: in-depth analysis of each ground, relevant case law citations, applicable legislation references, similar successful appeals, and detailed recommendations for legal professionals."
      },
      {
        q: "What's included in an Extensive Log Report?",
        a: "The Extensive Log ($39) is the most comprehensive option. It includes: complete document index, full timeline with source references, evidence matrix, detailed grounds analysis with supporting documents, procedural checklist, and professional formatting suitable for legal submissions."
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
    image: "https://images.unsplash.com/photo-1554224155-6726b3ff858f?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=150&fit=crop",
    questions: [
      {
        q: "What does the free version include?",
        a: "Free features include: unlimited document uploads, AI-generated timeline, Quick Summary reports, appeal progress checklist, and the legal glossary. You can manage your entire case without paying."
      },
      {
        q: "What are the paid features?",
        a: "Paid features include: Full Detailed Reports ($29 AUD) which provide comprehensive legal analysis with case citations, Extensive Log Reports ($39 AUD) for exhaustive documentation, and Grounds of Merit Details ($50 AUD) for in-depth analysis of each appeal ground."
      },
      {
        q: "Is my payment secure?",
        a: "Yes. All payments are processed through PayPal's secure payment system. We never see or store your credit card details."
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
    image: "https://images.unsplash.com/photo-1563986768609-322da13575f3?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=150&fit=crop",
    questions: [
      {
        q: "Is my case information confidential?",
        a: "Yes. Your case data is stored securely and is only accessible to you. We do not share individual case information with anyone. Aggregated, anonymised statistics may be used to improve the service."
      },
      {
        q: "Who can see my documents?",
        a: "Only you can see your uploaded documents and case details. Our system processes documents automatically - no humans review your files unless you specifically request support assistance."
      },
      {
        q: "Can I delete my data?",
        a: "Yes. You can delete individual documents, notes, or entire cases at any time. Deleted data is permanently removed from our systems within 30 days."
      },
      {
        q: "Where is my data stored?",
        a: "Your data is stored on secure servers with industry-standard encryption. We take data security seriously and implement best practices to protect your information."
      }
    ]
  },
  {
    category: "Getting Legal Help",
    icon: Users,
    color: "orange",
    image: "https://images.unsplash.com/photo-1521791055366-0d553872125f?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=150&fit=crop",
    questions: [
      {
        q: "How do I find a criminal appeal lawyer?",
        a: "Check our Lawyer Directory page for links to criminal appeal specialists in each state. You can also contact your state's Legal Aid office, Law Society, or Bar Association for referrals."
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
  }
];

const FAQPage = () => {
  const { theme, toggleTheme } = useTheme();
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
    blue_mapped: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400",
    red: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400",
    blue: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400",
    purple: "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400",
    emerald: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400",
    slate: "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300",
    orange: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400",
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-slate-900 dark:bg-slate-950 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Appeal Case Manager
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <Link to="/">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg">
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
            src="https://images.unsplash.com/photo-1589578527966-fdac0f44566c?crop=entropy&cs=srgb&fm=jpg&q=85&w=1920" 
            alt="Lady Justice"
            className="w-full h-full object-cover opacity-10 dark:opacity-5"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-500/30">
            <HelpCircle className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Frequently Asked Questions
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-2">
            Find answers to common questions about criminal appeals and using the Appeal Case Manager.
          </p>
          <p className="text-sm text-muted-foreground">
            <strong>{totalQuestions} answers</strong> across {faqs.length} categories
          </p>
          
          {/* Search */}
          <div className="max-w-xl mx-auto mt-8 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search for any question..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 py-6 text-base rounded-xl border-2 focus:border-blue-500"
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
                  ? "bg-red-600 text-white shadow-lg"
                  : "bg-card border border-border text-muted-foreground hover:border-blue-500"
              }`}
            >
              All Questions ({totalQuestions})
            </button>
            {faqs.map(cat => (
              <button
                key={cat.category}
                onClick={() => setActiveCategory(cat.category)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                  activeCategory === cat.category
                    ? "bg-red-600 text-white shadow-lg"
                    : "bg-card border border-border text-muted-foreground hover:border-blue-500"
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
          <p className="text-xs uppercase tracking-widest text-red-600 dark:text-blue-500 font-semibold mb-1">Quick Answers</p>
          <h2 className="text-xl font-bold text-foreground" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Browse by category or expand individual questions
          </h2>
        </section>

        {filteredFaqs.length === 0 ? (
          <Card className="p-12 text-center">
            <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-foreground font-semibold">No questions found matching "{searchQuery}"</p>
            <p className="text-muted-foreground text-sm mt-2">Try a different search term</p>
          </Card>
        ) : (
          <div className="space-y-8">
            {filteredFaqs.map((category, categoryIndex) => (
              <div key={categoryIndex}>
                {/* Category Header with Image */}
                <div className="rounded-2xl overflow-hidden mb-6 relative h-32">
                  <img 
                    src={category.image}
                    alt={category.category}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-slate-900/90 to-slate-900/50 flex items-center px-6">
                    <div className="flex items-center gap-4">
                      <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${colorClasses[category.color]}`}>
                        <category.icon className="w-7 h-7" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-white" style={{ fontFamily: 'Crimson Pro, serif' }}>
                          {category.category}
                        </h2>
                        <p className="text-slate-300 text-sm">
                          {category.questions.length} questions
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Questions */}
                <div className="space-y-3">
                  {category.questions.map((item, questionIndex) => {
                    const isOpen = openItems[`${categoryIndex}-${questionIndex}`];
                    return (
                      <div 
                        key={questionIndex}
                        className="bg-card border border-border rounded-xl overflow-hidden hover:shadow-lg hover:border-blue-500/30 transition-all"
                      >
                        <button
                          onClick={() => toggleItem(categoryIndex, questionIndex)}
                          className="w-full px-5 py-4 flex items-center justify-between text-left"
                          data-testid={`faq-${categoryIndex}-${questionIndex}`}
                        >
                          <span className="font-medium text-foreground pr-4">{item.q}</span>
                          <div className={`p-2 rounded-lg transition-colors flex-shrink-0 ${isOpen ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-muted'}`}>
                            {isOpen ? (
                              <ChevronDown className="w-5 h-5 text-red-600" />
                            ) : (
                              <ChevronRight className="w-5 h-5 text-muted-foreground" />
                            )}
                          </div>
                        </button>
                        {isOpen && (
                          <div className="px-5 pb-4">
                            <div className="bg-muted/50 rounded-xl p-4 border-l-4 border-blue-500">
                              <p className="text-muted-foreground text-sm leading-relaxed">{item.a}</p>
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
        <div className="mt-16 rounded-2xl overflow-hidden relative">
          <img 
            src="https://images.unsplash.com/photo-1521791055366-0d553872125f?crop=entropy&cs=srgb&fm=jpg&q=85&w=800&h=200&fit=crop"
            alt="Legal Help"
            className="w-full h-48 object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900/95 to-slate-900/80 flex items-center justify-center">
            <div className="text-center px-6">
              <MessageCircle className="w-12 h-12 text-blue-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-white mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Still have questions?
              </h3>
              <p className="text-slate-300 mb-6 max-w-md mx-auto">
                Can't find what you're looking for? We're here to help.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link to="/contact">
                  <Button className="bg-red-600 text-white hover:bg-blue-700 rounded-xl px-6">
                    Contact Us
                  </Button>
                </Link>
                <Link to="/glossary">
                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10 rounded-xl px-6">
                    Legal Glossary
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default FAQPage;
