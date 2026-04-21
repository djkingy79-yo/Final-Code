/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, createContext, useContext } from "react";

import { Scale, ArrowLeft, Building, Users, Phone, Globe, ExternalLink, MapPin, Menu, X, Shield, Gavel, FileText, AlertTriangle, Lightbulb } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";
import PageLogo from "../components/PageLogo";

const DirectoryFilterContext = createContext({ stateFilter: "all" });

const LegalResourcesPage = () => {

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [stateFilter, setStateFilter] = useState("all");

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const tabs = [
    { id: "options", label: "You Have Options", icon: Lightbulb },
    { id: "legal-aid", label: "Legal Aid", icon: Users },
    { id: "law-societies", label: "Law Societies", icon: Scale },
    { id: "complaints", label: "Complaints & OLCR", icon: AlertTriangle },
    { id: "courts", label: "Courts", icon: Gavel },
    { id: "community", label: "Community Legal", icon: Building },
    { id: "pro-bono", label: "Pro Bono", icon: Shield },
    { id: "government", label: "Government Bodies", icon: Building },
    { id: "profession", label: "Profession Bodies", icon: Scale },
    { id: "specialist", label: "Specialist Services", icon: Users },
    { id: "regulatory", label: "Regulatory Agencies", icon: Shield },
  ];

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="legal-resources-home-link">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center" data-testid="legal-resources-brand-icon">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight hidden sm:block" style={{ fontFamily: "'Times New Roman', Times, serif" }} data-testid="legal-resources-brand-text">
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/glossary" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="legal-resources-nav-legal-terms">Legal Terms</Link>
            <Link to="/faq" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="legal-resources-nav-faq">FAQ</Link>
<Link to="/" data-testid="legal-resources-back-link">
              <Button className="landing-cta-primary" data-testid="legal-resources-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-slate-900" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="legal-resources-mobile-menu-btn">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200 px-6 py-4 space-y-3">
            <Link to="/glossary" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="legal-resources-mobile-legal-terms">Legal Terms</Link>
            <Link to="/faq" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="legal-resources-mobile-faq">FAQ</Link>
            <Link to="/" className="block py-2 text-blue-700 hover:text-blue-800" data-testid="legal-resources-mobile-back">Back to Home</Link>
          </div>
        )}
      </header>

      <PageLogo />

      {/* Hero */}
      <section className="py-6 px-6 bg-white">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl font-bold mb-3 text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }} data-testid="legal-resources-hero-title">
            Legal Resources & Contacts
          </h1>
          <p className="text-base text-slate-700 max-w-xl mx-auto" data-testid="legal-resources-hero-description">
            Merged directory for legal resources and contacts across all Australian states and territories.
          </p>
        </div>
      </section>

      <section className="sticky top-[72px] z-30 bg-white backdrop-blur border-b border-slate-200" data-testid="legal-resources-quick-nav-wrapper">
        <div className="max-w-5xl mx-auto px-6 py-2">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <label className="text-[10px] font-semibold text-slate-700 uppercase tracking-wide" htmlFor="state-filter-select">
              Filter by state
            </label>
            <select
              id="state-filter-select"
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="h-7 rounded-md border border-slate-200 bg-white px-2 text-xs text-slate-900"
              data-testid="legal-resources-state-filter"
            >
              <option value="all">All states & national</option>
              <option value="NATIONAL">National / Multi-state</option>
              <option value="NSW">NSW</option>
              <option value="VIC">VIC</option>
              <option value="QLD">QLD</option>
              <option value="SA">SA</option>
              <option value="WA">WA</option>
              <option value="TAS">TAS</option>
              <option value="NT">NT</option>
              <option value="ACT">ACT</option>
            </select>
          </div>

          <div className="flex gap-1.5 overflow-x-auto pb-1" data-testid="legal-resources-quick-nav">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => scrollToSection(tab.id)}
                  className="inline-flex items-center gap-1 whitespace-nowrap px-2 py-1.5 rounded-md border border-slate-200 bg-white hover:border-blue-500 hover:bg-blue-50 text-xs text-slate-900 transition-colors"
                  data-testid={`legal-resource-tab-${tab.id}`}
                >
                  <Icon className="w-3 h-3 text-blue-700" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      <DirectoryFilterContext.Provider value={{ stateFilter }}>
      <main className="max-w-5xl mx-auto px-6 py-8 space-y-12" data-state-condensed={stateFilter !== "all"}>

        {/* ============ SECTION: You Have Options ============ */}
        <div id="options" className="space-y-6">
          <div className="bg-blue-600 border border-blue-700 rounded-xl p-6">
            <h2 className="text-2xl font-bold text-white mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Legal Help You May Not Know About
            </h2>
            <p className="text-blue-50">
              For most people, Legal Aid is the only affordable option — but private firms are often out of reach. 
              What many don't realise is that there are other avenues for help. <strong className="text-white">When you think you have no options, 
              there definitely are options.</strong>
            </p>
          </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Legal Aid Overview */}
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                  <Scale className="w-6 h-6 text-blue-700" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Legal Aid</h3>
                <p className="text-slate-700 text-xs mb-2">
                  Government-funded legal assistance available in every state. While overburdened, they can provide 
                  representation for serious criminal matters and appeals if you meet the eligibility criteria.
                </p>
                <button 
                  onClick={() => scrollToSection("legal-aid")}
                  className="text-blue-700 hover:underline text-sm font-medium"
                >
                  View all Legal Aid services →
                </button>
              </div>

              {/* Pro Bono Overview */}
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-emerald-700" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Pro Bono Legal Services</h3>
                <p className="text-slate-700 text-xs mb-2">
                  Many law firms and barristers provide free legal services (pro bono) for those who cannot afford representation. 
                  This is not widely advertised but is a genuine option.
                </p>
                <button 
                  onClick={() => scrollToSection("pro-bono")}
                  className="text-emerald-700 hover:underline text-sm font-medium"
                >
                  Find pro bono services →
                </button>
              </div>

              {/* Community Legal Centres */}
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                  <MapPin className="w-6 h-6 text-purple-700" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Community Legal Centres</h3>
                <p className="text-slate-700 text-xs mb-2">
                  Independent, non-profit organisations providing free legal advice and assistance. They often help with 
                  matters Legal Aid cannot cover and can refer you to specialist services.
                </p>
                <button 
                  onClick={() => scrollToSection("community")}
                  className="text-purple-700 hover:underline text-sm font-medium"
                >
                  Find community legal centres →
                </button>
              </div>

              {/* Grants & Funding */}
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                  <FileText className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-sm font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Grants & Special Funding</h3>
                <p className="text-slate-700 text-[10px] mb-3">
                  Various grants and funding programmes exist specifically to support criminal appeals and wrongful conviction cases. 
                  These are rarely advertised but can cover legal costs.
                </p>
                <ul className="text-[10px] text-slate-600 space-y-1 mb-3">
                  <li>• <a href="https://www.lawfoundation.net.au" target="_blank" rel="noopener noreferrer" className="text-blue-700 hover:underline text-[10px]">Law Foundation Grants</a></li>
                  <li>• State-based legal assistance funding</li>
                  <li>• Innocence projects (for wrongful convictions)</li>
                  <li>• University law clinics</li>
                </ul>
              </div>
            </div>

            {/* Key Message */}
            <div className="bg-blue-600 border border-blue-700 rounded-2xl p-6 text-center" data-testid="legal-resources-dont-give-up">
              <h3 className="text-white text-2xl font-bold mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Don't Give Up</h3>
              <p className="text-blue-50 text-base font-semibold">
                The legal system is complex, but help exists. Start with Legal Aid, then explore pro bono services 
                and community legal centres. Many people have found help when they thought there was none.
              </p>
            </div>
          </div>

        {/* Legal Aid Tab */}
        
          <div id="legal-aid" className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Legal Aid Services
              </h2>
              <p className="text-slate-700 text-xs">
                Government-funded legal assistance available in every state and territory. While overburdened, 
                they can provide representation for serious criminal matters and appeals if you meet eligibility criteria.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Legal Aid NSW"
                state="NSW"
                phone="1300 888 529"
                website="https://www.legalaid.nsw.gov.au"
                description="Criminal law, family law, civil law services for eligible NSW residents."
                color="blue"
              />
              <ResourceCard
                title="Victoria Legal Aid"
                state="VIC"
                phone="1300 792 387"
                website="https://www.legalaid.vic.gov.au"
                description="Free legal information, advice and representation in Victoria."
                color="purple"
              />
              <ResourceCard
                title="Legal Aid Queensland"
                state="QLD"
                phone="1300 651 188"
                website="https://www.legalaid.qld.gov.au"
                description="Legal help for Queenslanders who can't afford a lawyer."
                color="red"
              />
              <ResourceCard
                title="Legal Services Commission SA"
                state="SA"
                phone="1300 366 424"
                website="https://lsc.sa.gov.au"
                description="Legal aid services for South Australians."
                color="blue"
              />
              <ResourceCard
                title="Legal Aid WA"
                state="WA"
                phone="1300 650 579"
                website="https://www.legalaid.wa.gov.au"
                description="Legal assistance for Western Australians."
                color="emerald"
              />
              <ResourceCard
                title="Legal Aid Commission of Tasmania"
                state="TAS"
                phone="1300 366 611"
                website="https://www.legalaid.tas.gov.au"
                description="Legal assistance for Tasmanians."
                color="teal"
              />
              <ResourceCard
                title="Northern Territory Legal Aid Commission"
                state="NT"
                phone="1800 019 343"
                website="https://www.legalaid.nt.gov.au"
                description="Legal aid services in the Northern Territory."
                color="orange"
              />
              <ResourceCard
                title="Legal Aid ACT"
                state="ACT"
                phone="1300 654 314"
                website="https://www.legalaidact.org.au"
                description="Legal aid for ACT residents."
                color="indigo"
              />
            </div>
          </div>

        {/* Law Societies Tab */}
        
          <div id="law-societies" className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Law Societies
              </h2>
              <p className="text-slate-700 text-xs">
                Professional bodies representing solicitors in each state. They offer referral services to help you find a lawyer, 
                and can assist with complaints about legal practitioners.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Law Society of NSW"
                state="NSW"
                phone="(02) 9926 0333"
                website="https://www.lawsociety.com.au"
                description="Solicitor referral service, complaints handling, legal information."
                color="blue"
              />
              <ResourceCard
                title="Law Institute of Victoria"
                state="VIC"
                phone="(03) 9607 9311"
                website="https://www.liv.asn.au"
                description="Find a lawyer service, legal resources for Victorians."
                color="purple"
              />
              <ResourceCard
                title="Queensland Law Society"
                state="QLD"
                phone="1300 367 757"
                website="https://www.qls.com.au"
                description="Solicitor referral, legal information for Queenslanders."
                color="red"
              />
              <ResourceCard
                title="Law Society of South Australia"
                state="SA"
                phone="(08) 8229 0200"
                website="https://www.lawsocietysa.asn.au"
                description="Legal referral service for South Australians."
                color="blue"
              />
              <ResourceCard
                title="Law Society of Western Australia"
                state="WA"
                phone="(08) 9324 8600"
                website="https://www.lawsocietywa.asn.au"
                description="Lawyer referral and legal services for WA."
                color="emerald"
              />
              <ResourceCard
                title="Law Society of Tasmania"
                state="TAS"
                phone="(03) 6234 4133"
                website="https://www.lst.org.au"
                description="Find a lawyer service in Tasmania."
                color="teal"
              />
              <ResourceCard
                title="Law Society Northern Territory"
                state="NT"
                phone="(08) 8981 5104"
                website="https://www.lawsocietynt.asn.au"
                description="Legal services in the Northern Territory."
                color="orange"
              />
              <ResourceCard
                title="ACT Law Society"
                state="ACT"
                phone="(02) 6274 0300"
                website="https://www.actlawsociety.asn.au"
                description="Lawyer referral for ACT residents."
                color="indigo"
              />
            </div>

            {/* Bar Associations */}
            <div className="mt-8">
              <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Bar Associations (Barristers)
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <ResourceCard
                  title="NSW Bar Association"
                  state="NSW"
                  phone="(02) 9232 4055"
                  website="https://www.nswbar.asn.au"
                  description="Find a barrister, direct access scheme."
                  color="slate"
                />
                <ResourceCard
                  title="Victorian Bar"
                  state="VIC"
                  phone="(03) 9225 7111"
                  website="https://www.vicbar.com.au"
                  description="Barrister referral service for Victoria."
                  color="slate"
                />
                <ResourceCard
                  title="Queensland Bar"
                  state="QLD"
                  phone="(07) 3238 5100"
                  website="https://www.qldbar.asn.au"
                  description="Find a barrister in Queensland."
                  color="slate"
                />
              </div>
            </div>
          </div>

        {/* Complaints & OLCR Tab */}
        
          <div id="complaints" className="space-y-6">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Complaints Bodies & Legal Services Commissioners
              </h2>
              <p className="text-slate-700 text-xs">
                If you have a complaint about a lawyer's conduct, fees, or service, these independent bodies can investigate 
                and take action. The OLCR (Office of the Legal Services Commissioner) in NSW handles complaints about lawyers.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Office of the Legal Services Commissioner (OLCR)"
                state="NSW"
                phone="(02) 9377 1800"
                website="https://www.olsc.nsw.gov.au"
                description="Handles complaints about lawyers in NSW. Investigates professional misconduct, overcharging, and poor service."
                color="red"
                highlight={true}
              />
              <ResourceCard
                title="Victorian Legal Services Board + Commissioner"
                state="VIC"
                phone="1300 796 344"
                website="https://lsbc.vic.gov.au"
                description="Regulates lawyers in Victoria. Handles complaints about professional conduct."
                color="purple"
              />
              <ResourceCard
                title="Legal Services Commission Queensland"
                state="QLD"
                phone="(07) 3564 7726"
                website="https://www.lsc.qld.gov.au"
                description="Independent statutory body handling legal profession complaints in QLD."
                color="red"
              />
              <ResourceCard
                title="Legal Profession Conduct Commissioner SA"
                state="SA"
                phone="(08) 8111 5555"
                website="https://www.lpcc.sa.gov.au"
                description="Investigates complaints against lawyers in South Australia."
                color="blue"
              />
              <ResourceCard
                title="Legal Services and Complaints Committee WA"
                state="WA"
                phone="(08) 9461 2299"
                website="https://www.lsc.wa.gov.au"
                description="Handles complaints about legal practitioners in WA."
                color="emerald"
              />
              <ResourceCard
                title="Legal Profession Board of Tasmania"
                state="TAS"
                phone="(03) 6226 3000"
                website="https://www.lpbt.com.au"
                description="Regulates legal profession and handles complaints in Tasmania."
                color="teal"
              />
            </div>

            {/* What you can complain about */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 mt-6">
              <h3 className="font-bold text-slate-900 mb-4">What Can You Complain About?</h3>
              <div className="grid md:grid-cols-2 gap-3 text-xs">
                <div>
                  <h4 className="font-semibold text-slate-900 mb-2">Professional Misconduct</h4>
                  <ul className="text-slate-700 space-y-1">
                    <li>• Dishonesty or fraud</li>
                    <li>• Conflict of interest</li>
                    <li>• Breach of confidentiality</li>
                    <li>• Incompetence or negligence</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-2">Service Issues</h4>
                  <ul className="text-slate-700 space-y-1">
                    <li>• Overcharging / excessive fees</li>
                    <li>• Poor communication</li>
                    <li>• Delays without explanation</li>
                    <li>• Not following instructions</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

        {/* Courts Tab */}
        
          <div id="courts" className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Courts of Australia
              </h2>
              <p className="text-slate-700 text-xs">
                Direct links to court websites for each state and territory, plus federal courts. 
                Find court locations, forms, fees, and case information.
              </p>
            </div>

            {/* Federal Courts */}
            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                <Scale className="w-5 h-5 text-red-600" />
                Federal Courts
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <ResourceCard
                  title="High Court of Australia"
                  state="Federal"
                  phone="(02) 6270 6811"
                  website="https://www.hcourt.gov.au"
                  description="Australia's highest court. Hears constitutional matters and appeals of national importance."
                  color="slate"
                />
                <ResourceCard
                  title="Federal Court of Australia"
                  state="Federal"
                  phone="1300 720 980"
                  website="https://www.fedcourt.gov.au"
                  description="Handles federal law matters including some criminal appeals."
                  color="slate"
                />
              </div>
            </div>

            {/* State/Territory Courts */}
            <div className="mt-8">
              <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                State & Territory Courts
              </h3>
              
              {/* NSW */}
              <div className="mb-6">
                <h4 className="font-semibold text-blue-700 mb-3 flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">NSW</div>
                  New South Wales
                </h4>
                <div className="grid md:grid-cols-3 gap-3">
                  <SmallResourceCard title="Supreme Court NSW" website="https://www.supremecourt.justice.nsw.gov.au" />
                  <SmallResourceCard title="Court of Criminal Appeal" website="https://www.supremecourt.justice.nsw.gov.au/Pages/sco2_criminalappeal/sco2_criminalappeal.aspx" />
                  <SmallResourceCard title="District Court NSW" website="https://www.districtcourt.justice.nsw.gov.au" />
                  <SmallResourceCard title="Local Court NSW" website="https://www.localcourt.justice.nsw.gov.au" />
                  <SmallResourceCard title="Children's Court NSW" website="https://www.childrenscourt.justice.nsw.gov.au" />
                </div>
              </div>

              {/* VIC */}
              <div className="mb-6">
                <h4 className="font-semibold text-purple-700 mb-3 flex items-center gap-2">
                  <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">VIC</div>
                  Victoria
                </h4>
                <div className="grid md:grid-cols-3 gap-3">
                  <SmallResourceCard title="Supreme Court VIC" website="https://www.supremecourt.vic.gov.au" />
                  <SmallResourceCard title="Court of Appeal VIC" website="https://www.supremecourt.vic.gov.au/court-of-appeal" />
                  <SmallResourceCard title="County Court VIC" website="https://www.countycourt.vic.gov.au" />
                  <SmallResourceCard title="Magistrates' Court VIC" website="https://www.mcv.vic.gov.au" />
                  <SmallResourceCard title="Children's Court VIC" website="https://www.childrenscourt.vic.gov.au" />
                </div>
              </div>

              {/* QLD */}
              <div className="mb-6">
                <h4 className="font-semibold text-red-600 mb-3 flex items-center gap-2">
                  <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">QLD</div>
                  Queensland
                </h4>
                <div className="grid md:grid-cols-3 gap-3">
                  <SmallResourceCard title="Supreme Court QLD" website="https://www.courts.qld.gov.au/" />
                  <SmallResourceCard title="Court of Appeal QLD" website="https://www.courts.qld.gov.au/" />
                  <SmallResourceCard title="District Court QLD" website="https://www.courts.qld.gov.au/" />
                  <SmallResourceCard title="Magistrates Courts QLD" website="https://www.courts.qld.gov.au/" />
                </div>
              </div>

              {/* SA */}
              <div className="mb-6">
                <h4 className="font-semibold text-red-600 mb-3 flex items-center gap-2">
                  <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">SA</div>
                  South Australia
                </h4>
                <div className="grid md:grid-cols-3 gap-3">
                  <SmallResourceCard title="Supreme Court SA" website="https://www.courts.sa.gov.au/" />
                  <SmallResourceCard title="District Court SA" website="https://www.courts.sa.gov.au/" />
                  <SmallResourceCard title="Magistrates Court SA" website="https://www.courts.sa.gov.au/" />
                </div>
              </div>

              {/* WA */}
              <div className="mb-6">
                <h4 className="font-semibold text-emerald-700 mb-3 flex items-center gap-2">
                  <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">WA</div>
                  Western Australia
                </h4>
                <div className="grid md:grid-cols-3 gap-3">
                  <SmallResourceCard title="Supreme Court WA" website="https://www.wa.gov.au/organisation/department-of-justice/supreme-court-of-western-australia" />
                  <SmallResourceCard title="Court of Appeal WA" website="https://www.wa.gov.au/organisation/department-of-justice/supreme-court-of-western-australia" />
                  <SmallResourceCard title="District Court WA" website="https://www.districtcourt.wa.gov.au" />
                  <SmallResourceCard title="Magistrates Court WA" website="https://www.magistratescourt.wa.gov.au" />
                </div>
              </div>

              {/* TAS, NT, ACT */}
              <div className="mb-6">
                <h4 className="font-semibold text-slate-900 mb-3">Tasmania, NT & ACT</h4>
                <div className="grid md:grid-cols-3 gap-3">
                  <SmallResourceCard title="Supreme Court TAS" website="https://www.supremecourt.tas.gov.au" />
                  <SmallResourceCard title="Magistrates Court TAS" website="https://www.magistratescourt.tas.gov.au" />
                  <SmallResourceCard title="Supreme Court NT" website="https://supremecourt.nt.gov.au" />
                  <SmallResourceCard title="Local Court NT" website="https://localcourt.nt.gov.au" />
                  <SmallResourceCard title="Supreme Court ACT" website="https://www.courts.act.gov.au/supreme" />
                  <SmallResourceCard title="Magistrates Court ACT" website="https://www.courts.act.gov.au/magistrates" />
                </div>
              </div>
            </div>
          </div>

        {/* Community Legal Tab */}
        
          <div id="community" className="space-y-6">
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Community Legal Centres
              </h2>
              <p className="text-slate-700 text-xs">
                Independent, non-profit organisations providing free legal advice and assistance. 
                They often help with matters Legal Aid cannot cover and can refer you to specialist services.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Community Legal Centres Australia"
                state="National"
                phone="N/A"
                website="https://clcs.org.au"
                description="National network of community legal centres. Find your local CLC."
                color="purple"
                highlight={true}
              />
              <ResourceCard
                title="Community Legal Centres NSW"
                state="NSW"
                phone="(02) 9212 7333"
                website="https://www.clcnsw.org.au"
                description="Network of community legal centres across NSW."
                color="blue"
              />
              <ResourceCard
                title="Federation of Community Legal Centres VIC"
                state="VIC"
                phone="(03) 9652 1500"
                website="https://www.fclc.org.au"
                description="Peak body for community legal centres in Victoria."
                color="purple"
              />
              <ResourceCard
                title="Community Legal Centres Queensland"
                state="QLD"
                phone="(07) 3392 0092"
                website="https://communitylegalqld.org.au"
                description="Network of community legal centres in Queensland."
                color="red"
              />
            </div>

            {/* Specialist Services */}
            <div className="mt-8">
              <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Specialist Legal Services
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <ResourceCard
                  title="Aboriginal Legal Service NSW/ACT"
                  state="NSW/ACT"
                  phone="1800 765 767"
                  website="https://www.alsnswact.org.au"
                  description="Legal services for Aboriginal and Torres Strait Islander peoples."
                  color="blue"
                />
                <ResourceCard
                  title="Victorian Aboriginal Legal Service"
                  state="VIC"
                  phone="1800 064 865"
                  website="https://www.vals.org.au"
                  description="Legal assistance for Aboriginal Victorians."
                  color="blue"
                />
                <ResourceCard
                  title="Prisoners Legal Service QLD"
                  state="QLD"
                  phone="(07) 3846 5074"
                  website="https://www.plsqld.com"
                  description="Free legal help for prisoners and their families in Queensland."
                  color="slate"
                />
                <ResourceCard
                  title="Women's Legal Service NSW"
                  state="NSW"
                  phone="1800 801 501"
                  website="https://www.wlsnsw.org.au"
                  description="Free legal services for women in NSW."
                  color="pink"
                />
              </div>
            </div>
          </div>

        {/* Pro Bono Tab */}
        
          <div id="pro-bono" className="space-y-6">
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Pro Bono Legal Services
              </h2>
              <p className="text-slate-700 text-xs">
                Many law firms and barristers provide free legal services (pro bono) for those who cannot afford representation. 
                This is not widely advertised but is a genuine option for serious matters.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Australian Pro Bono Centre"
                state="National"
                phone="(02) 9385 7381"
                website="https://www.probonocentre.org.au"
                description="Promotes and supports pro bono legal services across Australia."
                color="emerald"
                highlight={true}
              />
              <ResourceCard
                title="Justice Connect"
                state="VIC/NSW"
                phone="(03) 8636 4400"
                website="https://www.justiceconnect.org.au"
                description="Connects people with pro bono legal help. Covers Victoria and NSW."
                color="emerald"
              />
              <ResourceCard
                title="Law Access NSW"
                state="NSW"
                phone="1300 888 529"
                website="https://www.lawaccess.nsw.gov.au"
                description="Free legal information, referrals and some pro bono assistance."
                color="blue"
              />
              <ResourceCard
                title="LawRight (formerly QPILCH)"
                state="QLD"
                phone="(07) 3846 6317"
                website="https://lawright.org.au"
                description="LawRight - pro bono legal referrals and assistance in Queensland."
                color="red"
              />
            </div>

            {/* Innocence Projects */}
            <div className="mt-8">
              <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Innocence & Wrongful Conviction Projects
              </h3>
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <p className="text-slate-700 text-xs mb-4">
                  For cases involving potential wrongful convictions, these organisations may be able to assist:
                </p>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-white border border-slate-200 rounded-lg p-4">
                    <h4 className="font-semibold text-slate-900 text-sm mb-1">University Law Clinics</h4>
                    <p className="text-[11px] text-slate-700">
                      Many university law schools run clinics that take on appeals and wrongful conviction cases. 
                      Contact your local university's law faculty.
                    </p>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-lg p-4">
                    <h4 className="font-semibold text-slate-900 text-sm mb-1">Innocence Projects</h4>
                    <p className="text-[11px] text-slate-700">
                      Some Australian universities have innocence projects that investigate potential wrongful convictions.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

        {/* ============ NEW SECTION: Government & Regulatory Bodies ============ */}
        <div id="government" className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Building className="w-7 h-7 text-blue-600" />
            Government & Regulatory Bodies
          </h2>
          <p className="text-slate-700">
            Key government departments, ombudsmen, and regulatory agencies that oversee the justice system.
          </p>

          {/* Attorneys-General */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Attorneys-General Departments
            </h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
              <a href="https://www.ag.gov.au" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 p-3 bg-white rounded-lg hover:shadow-md transition-shadow">
                <span className="w-8 h-8 bg-blue-600 rounded text-white text-xs font-bold flex items-center justify-center">CTH</span>
                <div className="min-w-0">
                  <p className="font-semibold text-sm text-slate-900 truncate">Commonwealth Attorney-General</p>
                  <p className="text-[11px] text-slate-700">ag.gov.au</p>
                </div>
                <ExternalLink className="w-4 h-4 text-slate-700 ml-auto shrink-0" />
              </a>
              <a href="https://www.justice.nsw.gov.au" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 p-3 bg-white rounded-lg hover:shadow-md transition-shadow">
                <span className="w-8 h-8 bg-blue-500 rounded text-white text-xs font-bold flex items-center justify-center">NSW</span>
                <div className="min-w-0">
                  <p className="font-semibold text-sm text-slate-900 truncate">NSW Department of Justice</p>
                  <p className="text-[11px] text-slate-700">justice.nsw.gov.au</p>
                </div>
                <ExternalLink className="w-4 h-4 text-slate-700 ml-auto shrink-0" />
              </a>
              <a href="https://www.justice.vic.gov.au" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 p-3 bg-white rounded-lg hover:shadow-md transition-shadow">
                <span className="w-8 h-8 bg-indigo-600 rounded text-white text-xs font-bold flex items-center justify-center">VIC</span>
                <div className="min-w-0">
                  <p className="font-semibold text-sm text-slate-900 truncate">VIC Dept of Justice</p>
                  <p className="text-[11px] text-slate-700">justice.vic.gov.au</p>
                </div>
                <ExternalLink className="w-4 h-4 text-slate-700 ml-auto shrink-0" />
              </a>
              <a href="https://www.justice.qld.gov.au" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 p-3 bg-white rounded-lg hover:shadow-md transition-shadow">
                <span className="w-8 h-8 bg-red-600 rounded text-white text-xs font-bold flex items-center justify-center">QLD</span>
                <div className="min-w-0">
                  <p className="font-semibold text-sm text-slate-900 truncate">QLD Dept of Justice</p>
                  <p className="text-[11px] text-slate-700">justice.qld.gov.au</p>
                </div>
                <ExternalLink className="w-4 h-4 text-slate-700 ml-auto shrink-0" />
              </a>
              <a href="https://www.justice.wa.gov.au" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 p-3 bg-white rounded-lg hover:shadow-md transition-shadow">
                <span className="w-8 h-8 bg-red-600 rounded text-white text-xs font-bold flex items-center justify-center">WA</span>
                <div className="min-w-0">
                  <p className="font-semibold text-sm text-slate-900 truncate">WA Dept of Justice</p>
                  <p className="text-[11px] text-slate-700">justice.wa.gov.au</p>
                </div>
                <ExternalLink className="w-4 h-4 text-slate-700 ml-auto shrink-0" />
              </a>
              <a href="https://www.agd.sa.gov.au" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 p-3 bg-white rounded-lg hover:shadow-md transition-shadow">
                <span className="w-8 h-8 bg-purple-600 rounded text-white text-xs font-bold flex items-center justify-center">SA</span>
                <div className="min-w-0">
                  <p className="font-semibold text-sm text-slate-900 truncate">SA Attorney-General's Dept</p>
                  <p className="text-[11px] text-slate-700">agd.sa.gov.au</p>
                </div>
                <ExternalLink className="w-4 h-4 text-slate-700 ml-auto shrink-0" />
              </a>
            </div>
          </div>

          {/* Ombudsmen */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Ombudsmen & Integrity Bodies
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Commonwealth Ombudsman"
                state="National"
                phone="1300 362 072"
                website="https://www.ombudsman.gov.au"
                description="Investigates complaints about Commonwealth government agencies and services."
                color="blue"
                highlight={true}
              />
              <ResourceCard
                title="NACC - National Anti-Corruption Commission"
                state="National"
                phone="1800 060 077"
                website="https://www.nacc.gov.au"
                description="National Anti-Corruption Commission - investigates serious or systemic corruption across the Commonwealth public sector."
                color="emerald"
              />
              <ResourceCard
                title="NSW Ombudsman"
                state="NSW"
                phone="1800 451 524"
                website="https://www.ombo.nsw.gov.au"
                description="Independent watchdog for NSW public sector agencies."
                color="blue"
              />
              <ResourceCard
                title="Victorian Ombudsman"
                state="VIC"
                phone="(03) 9613 6222"
                website="https://www.ombudsman.vic.gov.au"
                description="Investigates complaints about Victorian government and public bodies."
                color="indigo"
              />
              <ResourceCard
                title="QLD Ombudsman"
                state="QLD"
                phone="(07) 3005 7000"
                website="https://www.ombudsman.qld.gov.au"
                description="Queensland Ombudsman - investigates administrative actions of QLD agencies."
                color="red"
              />
              <ResourceCard
                title="WA Ombudsman"
                state="WA"
                phone="(08) 9220 7555"
                website="https://www.ombudsman.wa.gov.au"
                description="Investigates WA state government and local government agencies."
                color="blue"
              />
            </div>
          </div>

          {/* Human Rights & Discrimination */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Human Rights Commissions
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Australian Human Rights Commission"
                state="National"
                phone="1300 369 711"
                website="https://humanrights.gov.au"
                description="National body that handles discrimination complaints and promotes human rights."
                color="emerald"
                highlight={true}
              />
              <ResourceCard
                title="Anti-Discrimination NSW"
                state="NSW"
                phone="1800 670 812"
                website="https://www.antidiscrimination.nsw.gov.au"
                description="Handles discrimination complaints in NSW."
                color="blue"
              />
              <ResourceCard
                title="Victorian Equal Opportunity Commission"
                state="VIC"
                phone="1300 292 153"
                website="https://www.humanrights.vic.gov.au"
                description="Promotes and protects human rights in Victoria."
                color="indigo"
              />
            </div>
          </div>
        </div>

        {/* ============ NEW SECTION: Legal Profession Bodies ============ */}
        <div id="profession" className="space-y-6">
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Gavel className="w-6 h-6 text-red-600" />
            Legal Profession Bodies
          </h2>
          <p className="text-slate-700 text-xs">
            Law societies, bar associations, and professional conduct bodies that regulate the legal profession.
          </p>

          {/* Law Councils & Societies */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Law Councils & Societies
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Law Council of Australia"
                state="National"
                phone="(02) 6246 3788"
                website="https://www.lawcouncil.asn.au"
                description="Peak national body representing the Australian legal profession."
                color="blue"
                highlight={true}
              />
              <ResourceCard
                title="Law Society of SA"
                state="SA"
                phone="(08) 8229 0200"
                website="https://www.lawsocietysa.asn.au"
                description="Represents solicitors in South Australia."
                color="purple"
              />
              <ResourceCard
                title="Law Society of WA"
                state="WA"
                phone="(08) 9324 8600"
                website="https://www.lawsocietywa.asn.au"
                description="Peak body for lawyers in Western Australia."
                color="blue"
              />
            </div>
          </div>

          {/* Bar Associations */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Bar Associations (Barristers)
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Australian Bar Association"
                state="National"
                phone="(02) 9232 4055"
                website="https://www.australianbar.asn.au"
                description="National body representing barristers. Can help find specialist criminal barristers."
                color="slate"
                highlight={true}
              />
            </div>
          </div>

          {/* Legal Practice Boards & Conduct */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Legal Practice Boards & Professional Conduct
            </h3>
            <p className="text-slate-700 text-xs mb-3">
              If you have a complaint about a lawyer's conduct, these bodies can investigate:
            </p>
            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Legal Services Council"
                state="National"
                phone="N/A"
                website="https://www.legalservicescouncil.org.au"
                description="National body overseeing regulation of the legal profession."
                color="slate"
              />
              <ResourceCard
                title="Legal Services Commissioner NSW"
                state="NSW"
                phone="(02) 9377 1800"
                website="https://www.olsc.nsw.gov.au"
                description="Handles complaints about NSW lawyers. Also known as OLSC."
                color="blue"
              />
              <ResourceCard
                title="Legal Services Board VIC"
                state="VIC"
                phone="(03) 9679 8001"
                website="https://www.lsbc.vic.gov.au"
                description="Regulates lawyers in Victoria and handles complaints."
                color="indigo"
              />
              <ResourceCard
                title="Legal Practice Board WA"
                state="WA"
                phone="(08) 9461 2299"
                website="https://www.lpbwa.org.au"
                description="Regulates legal practitioners in Western Australia."
                color="blue"
              />
              <ResourceCard
                title="Legal Services Commission QLD"
                state="QLD"
                phone="(07) 3564 7726"
                website="https://www.lsc.qld.gov.au"
                description="Handles complaints about Queensland lawyers."
                color="red"
              />
            </div>
          </div>

          {/* Law Reform */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Law Reform & Research Bodies
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <ResourceCard
                title="Australian Law Reform Commission"
                state="National"
                phone="(02) 8238 6333"
                website="https://www.alrc.gov.au"
                description="Reviews and recommends changes to Australian laws. Publishes important reports."
                color="blue"
              />
              <ResourceCard
                title="Law and Justice Foundation of NSW"
                state="NSW"
                phone="(02) 8227 3200"
                website="https://www.lawfoundation.net.au"
                description="Research and grants to improve access to justice in NSW."
                color="blue"
              />
              <ResourceCard
                title="NSW Law Reform Commission"
                state="NSW"
                phone="(02) 8061 9270"
                website="https://www.lawreform.justice.nsw.gov.au"
                description="Reviews and recommends changes to NSW laws."
                color="blue"
              />
              <ResourceCard
                title="Victorian Law Reform Commission"
                state="VIC"
                phone="(03) 8608 7800"
                website="https://www.lawreform.vic.gov.au"
                description="Reviews and reports on areas of Victorian law."
                color="indigo"
              />
            </div>
          </div>
        </div>

        {/* ============ NEW SECTION: Specialist Legal Services ============ */}
        <div id="specialist" className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Users className="w-7 h-7 text-purple-600" />
            Specialist Legal Services
          </h2>
          <p className="text-slate-700">
            Services for specific groups including prisoners, Aboriginal and Torres Strait Islander peoples, and vulnerable communities.
          </p>

          <div className="grid md:grid-cols-2 gap-4">
            <ResourceCard
              title="Prisoners' Legal Service QLD"
              state="QLD"
              phone="(07) 3846 5074"
              website="https://www.plsqld.com"
              description="Free legal advice and representation for Queensland prisoners."
              color="red"
              highlight={true}
            />
            <ResourceCard
              title="Prisoners Aid NSW"
              state="NSW"
              phone="(02) 9666 5927"
              website="https://www.prisonersaidnsw.org"
              description="Support services for NSW prisoners and their families."
              color="blue"
            />
            <ResourceCard
              title="Aboriginal Legal Service WA"
              state="WA"
              phone="(08) 9265 6666"
              website="https://www.als.org.au"
              description="Legal services for Aboriginal and Torres Strait Islander peoples in WA."
              color="blue"
            />
            <ResourceCard
              title="North Australian Aboriginal Justice Agency"
              state="NT"
              phone="1800 898 251"
              website="https://www.naaja.org.au"
              description="Legal services for Aboriginal peoples in the Northern Territory."
              color="orange"
            />
            <ResourceCard
              title="Redfern Legal Centre"
              state="NSW"
              phone="(02) 9698 7277"
              website="https://rlc.org.au"
              description="Free community legal centre in inner Sydney. Specialises in many areas."
              color="emerald"
            />
            <ResourceCard
              title="Kingsford Legal Centre"
              state="NSW"
              phone="(02) 9385 9566"
              website="https://www.klc.unsw.edu.au"
              description="UNSW community legal centre providing free legal advice."
              color="blue"
            />
          </div>
        </div>

        {/* ============ NEW SECTION: Regulatory Agencies ============ */}
        <div id="regulatory" className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Shield className="w-7 h-7 text-red-600" />
            Other Regulatory Agencies
          </h2>
          <p className="text-slate-700">
            Government agencies that may be relevant depending on your case circumstances.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ResourceCard
              title="ACCC"
              state="National"
              phone="1300 302 502"
              website="https://www.accc.gov.au"
              description="Australian Competition and Consumer Commission - consumer protection."
              color="blue"
            />
            <ResourceCard
              title="ASIC"
              state="National"
              phone="1300 300 630"
              website="https://www.asic.gov.au"
              description="Australian Securities and Investments Commission - corporate regulation."
              color="blue"
            />
            <ResourceCard
              title="AFP"
              state="National"
              phone="(02) 5126 0000"
              website="https://www.afp.gov.au"
              description="Australian Federal Police - federal law enforcement."
              color="slate"
            />
            <ResourceCard
              title="AustLII"
              state="National"
              phone="N/A"
              website="https://www.austlii.edu.au"
              description="Free access to Australian legal information - cases, legislation, treaties."
              color="emerald"
              highlight={true}
            />
            <ResourceCard
              title="Australasian Legal Information Institute"
              state="National"
              phone="N/A"
              website="https://www.alii.org"
              description="Legal information from Australian and international sources."
              color="emerald"
            />
            <ResourceCard
              title="Australian Public Law"
              state="National"
              phone="N/A"
              website="https://www.auspublaw.org"
              description="Academic resource for Australian public law commentary and analysis."
              color="blue"
            />
          </div>
        </div>

      </main>
      </DirectoryFilterContext.Provider>

      {stateFilter !== "all" && (
        <style>{`
          [data-state-condensed="true"] section > h2,
          [data-state-condensed="true"] section > p {
            display: none;
          }
          [data-state-condensed="true"] section {
            margin-bottom: 0.5rem;
          }
        `}</style>
      )}
    </div>
  );
};

// Resource Card Component
/* Tailwind safelist: bg-blue-600 bg-purple-600 bg-red-600 bg-emerald-600 bg-teal-600 bg-orange-600 bg-indigo-600 bg-slate-700 bg-pink-600 */

const ResourceCard = ({ title, state, phone, website, description, color, highlight }) => {
  const { stateFilter } = useContext(DirectoryFilterContext);

  const normaliseState = (value) => {
    const raw = (value || "").toUpperCase();
    if (!raw || raw === "VARIOUS" || raw === "MULTI-STATE" || raw === "NATIONAL") return "NATIONAL";
    if (raw.includes("NSW")) return "NSW";
    if (raw.includes("VIC")) return "VIC";
    if (raw.includes("QLD")) return "QLD";
    if (raw.includes("SA")) return "SA";
    if (raw.includes("WA")) return "WA";
    if (raw.includes("TAS")) return "TAS";
    if (raw.includes("NT")) return "NT";
    if (raw.includes("ACT")) return "ACT";
    return "NATIONAL";
  };

  const stateOrder = {
    NATIONAL: 0,
    NSW: 1,
    VIC: 2,
    QLD: 3,
    SA: 4,
    WA: 5,
    TAS: 6,
    NT: 7,
    ACT: 8,
  };

  const normalisedState = normaliseState(state);
  if (stateFilter === "NATIONAL") {
    if (normalisedState !== "NATIONAL") {
      return null;
    }
  } else if (stateFilter !== "all" && normalisedState !== stateFilter && normalisedState !== "NATIONAL") {
    return null;
  }

  const colorHex = {
    blue: "#2563eb",
    purple: "#9333ea",
    red: "#dc2626",
    emerald: "#059669",
    teal: "#0d9488",
    orange: "#ea580c",
    indigo: "#4f46e5",
    slate: "#334155",
    pink: "#db2777",
  };

  return (
    <div
      className={`bg-white border ${highlight ? 'border-blue-400 border-2' : 'border-slate-200'} rounded-xl p-4 hover:shadow-md transition-shadow`}
      style={{ order: stateOrder[normalisedState] ?? 99 }}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-md flex items-center justify-center text-white text-[10px] font-bold shrink-0"
            style={{ backgroundColor: colorHex[color] || "#334155" }}
          >
            {state.slice(0, 3)}
          </div>
          <h3 className="font-bold text-slate-900 text-xs leading-tight">{title}</h3>
        </div>
      </div>
      <p className="text-slate-500 text-[10px] uppercase tracking-wide mb-1">How they can help</p>
      <p className="text-slate-700 text-[11px] mb-2 leading-relaxed">{description}</p>
      <div className="space-y-1.5 text-xs">
        {phone && phone !== "N/A" && (
          <a href={`tel:${phone.replace(/[^0-9]/g, '')}`} className="flex items-center gap-2 text-slate-700 hover:text-slate-900" data-testid={`legal-resource-phone-${title.toLowerCase().replace(/\s+/g, '-')}`}>
            <Phone className="w-3 h-3 text-emerald-600" />
            <span className="text-[11px]">{phone}</span>
          </a>
        )}
        {website && (
          <a href={website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-blue-700 hover:underline" data-testid={`legal-resource-website-${title.toLowerCase().replace(/\s+/g, '-')}`}>
            <Globe className="w-4 h-4" />
            <span className="text-xs truncate">Visit Website</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
};

// Small Resource Card for Courts
const SmallResourceCard = ({ title, website }) => (
  <a 
    href={website} 
    target="_blank" 
    rel="noopener noreferrer"
    className="flex items-center gap-2 p-3 bg-white border border-slate-200 hover:border-blue-300 hover:bg-slate-50 rounded-lg text-sm transition-colors group"
    data-testid={`legal-resources-court-${title.toLowerCase().replace(/\s+/g, '-')}`}
  >
    <Gavel className="w-4 h-4 text-slate-700 group-hover:text-blue-700 shrink-0" />
    <span className="text-slate-900 truncate">{title}</span>
    <ExternalLink className="w-3 h-3 text-slate-700 ml-auto shrink-0" />
  </a>
);

export default LegalResourcesPage;
