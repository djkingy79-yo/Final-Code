/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { Scale, ArrowLeft, ExternalLink, MapPin, Phone, Globe, Users, Building2, Gavel } from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Link } from "react-router-dom";
import { useState } from "react";
import { useTheme } from "../contexts/ThemeContext";

const lawyerResources = [
  {
    state: "New South Wales",
    code: "NSW",
    color: "bg-blue-600",
    legalAid: {
      name: "Legal Aid NSW",
      url: "https://www.legalaid.nsw.gov.au/",
      phone: "1300 888 529",
      description: "Free legal help for eligible people, including criminal appeals"
    },
    barAssociation: {
      name: "NSW Bar Association",
      url: "https://nswbar.asn.au/",
      description: "Find a barrister specialising in criminal appeals"
    },
    lawSociety: {
      name: "Law Society of NSW",
      url: "https://www.lawsociety.com.au/",
      description: "Find a solicitor - use 'Criminal Law' filter"
    },
    specialists: [
      { name: "Criminal Defence Lawyers Australia", url: "https://criminaldefencelawyers.com.au/", location: "Sydney CBD" },
      { name: "Sydney Criminal Lawyers", url: "https://www.sydneycriminallawyers.com.au/", location: "Sydney CBD" },
      { name: "LY Lawyers", url: "https://lylawyers.com.au/", location: "Parramatta" },
      { name: "MacDougall & Hydes", url: "https://www.macdougallhydes.com.au/", location: "Penrith" },
      { name: "Nyman Gibson Miralis", url: "https://www.nymangibsonmiralis.com.au/", location: "Sydney CBD" },
      { name: "Hugo Law Group", url: "https://hugolawgroup.com.au/", location: "Sydney CBD" }
    ]
  },
  {
    state: "Victoria",
    code: "VIC",
    color: "bg-purple-600",
    legalAid: {
      name: "Victoria Legal Aid",
      url: "https://www.legalaid.vic.gov.au/",
      phone: "1300 792 387",
      description: "Free legal help for eligible Victorians"
    },
    barAssociation: {
      name: "Victorian Bar",
      url: "https://www.vicbar.com.au/",
      description: "Find a barrister - search criminal law specialists"
    },
    lawSociety: {
      name: "Law Institute of Victoria",
      url: "https://www.liv.asn.au/",
      description: "Find a solicitor in your area"
    },
    specialists: [
      { name: "Stary Norton Halphen", url: "https://www.starylaw.com/", location: "Melbourne CBD" },
      { name: "Doogue + George", url: "https://www.criminal-lawyers.com.au/", location: "Melbourne CBD" },
      { name: "Dribbin & Brown", url: "https://www.criminalsolicitorsmelbourne.com.au/", location: "Melbourne CBD" },
      { name: "Galbally Parker", url: "https://galballyparker.com.au/", location: "Melbourne" },
      { name: "Leanne Warren & Associates", url: "https://leannewarren.com.au/", location: "Melbourne" },
      { name: "Slades & Parsons", url: "https://www.sladesparsons.com.au/", location: "Melbourne CBD" }
    ]
  },
  {
    state: "Queensland",
    code: "QLD",
    color: "bg-red-600",
    legalAid: {
      name: "Legal Aid Queensland",
      url: "https://www.legalaid.qld.gov.au/",
      phone: "1300 651 188",
      description: "Free legal services for eligible Queenslanders"
    },
    barAssociation: {
      name: "Bar Association of Queensland",
      url: "https://www.qldbar.asn.au/",
      description: "Find a barrister in Queensland"
    },
    lawSociety: {
      name: "Queensland Law Society",
      url: "https://www.qls.com.au/",
      description: "Find a solicitor - use referral service"
    },
    specialists: [
      { name: "Potts Lawyers", url: "https://www.pottslawyers.com.au/", location: "Brisbane & Gold Coast" },
      { name: "Robertson O'Gorman", url: "https://www.robertsonogorman.com.au/", location: "Brisbane CBD" },
      { name: "Gilshenan & Luton", url: "https://www.gnl.com.au/", location: "Brisbane CBD" },
      { name: "Fisher Dore Lawyers", url: "https://fisherdore.com.au/", location: "Brisbane" },
      { name: "Jacobson Mahony", url: "https://www.jacobsonmahony.com.au/", location: "Gold Coast" },
      { name: "Guest Lawyers", url: "https://guestlawyers.com.au/", location: "Brisbane" }
    ]
  },
  {
    state: "South Australia",
    code: "SA",
    color: "bg-red-600",
    legalAid: {
      name: "Legal Services Commission SA",
      url: "https://lsc.sa.gov.au/",
      phone: "1300 366 424",
      description: "Legal Aid services in South Australia"
    },
    barAssociation: {
      name: "South Australian Bar Association",
      url: "https://www.sabar.org.au/",
      description: "Find a barrister in SA"
    },
    lawSociety: {
      name: "Law Society of South Australia",
      url: "https://www.lawsocietysa.asn.au/",
      description: "Find a solicitor"
    },
    specialists: [
      { name: "Caldicott Lawyers", url: "https://www.caldicottlawyers.com.au/", location: "Adelaide CBD" },
      { name: "Mangan Ey & Associates", url: "https://manganey.com.au/", location: "Adelaide" },
      { name: "Johnston Withers", url: "https://johnstonwithers.com.au/", location: "Adelaide CBD" },
      { name: "Stanley Hill Elkins", url: "https://shelegal.com.au/", location: "Adelaide" }
    ]
  },
  {
    state: "Western Australia",
    code: "WA",
    color: "bg-emerald-600",
    legalAid: {
      name: "Legal Aid WA",
      url: "https://www.legalaid.wa.gov.au/",
      phone: "1300 650 579",
      description: "Free legal help for Western Australians"
    },
    barAssociation: {
      name: "WA Bar Association",
      url: "https://wabar.asn.au/",
      description: "Find a barrister in WA"
    },
    lawSociety: {
      name: "Law Society of Western Australia",
      url: "https://www.lawsocietywa.asn.au/",
      description: "Find a solicitor"
    },
    specialists: [
      { name: "Pattison Hardman", url: "https://www.pattisonhardman.com.au/", location: "Perth CBD" },
      { name: "James Jackson Criminal Defence", url: "https://www.jjacksoncriminaldefence.com.au/", location: "Perth" },
      { name: "Kate King Legal", url: "https://katekinglegal.com.au/", location: "Perth" },
      { name: "Curt Hofmann & Co", url: "https://perthcriminallawyer.com.au/", location: "Perth CBD" },
      { name: "WA Criminal Lawyers", url: "https://wacriminallawyersperth.com.au/", location: "Perth" }
    ]
  },
  {
    state: "Tasmania",
    code: "TAS",
    color: "bg-teal-600",
    legalAid: {
      name: "Legal Aid Commission of Tasmania",
      url: "https://www.legalaid.tas.gov.au/",
      phone: "1300 366 611",
      description: "Legal Aid services in Tasmania"
    },
    barAssociation: {
      name: "Tasmanian Bar",
      url: "https://www.tasbar.com.au/",
      description: "Find a barrister in Tasmania"
    },
    lawSociety: {
      name: "Law Society of Tasmania",
      url: "https://www.lst.org.au/",
      description: "Find a solicitor"
    },
    specialists: [
      { name: "Monk Lawyers", url: "https://www.monklawyers.com.au/", location: "Hobart" },
      { name: "Tierney Law", url: "https://tlaw.com.au/", location: "Hobart" },
      { name: "Brooke Winter Solicitors", url: "https://brookewintersolicitors.com.au/", location: "Hobart CBD" },
      { name: "Murdoch Clarke Lawyers", url: "https://murdochclarke.com.au/", location: "Hobart" }
    ]
  },
  {
    state: "Northern Territory",
    code: "NT",
    color: "bg-orange-600",
    legalAid: {
      name: "Northern Territory Legal Aid Commission",
      url: "https://www.legalaid.nt.gov.au/",
      phone: "1800 019 343",
      description: "Free legal help in the NT"
    },
    barAssociation: {
      name: "Northern Territory Bar Association",
      url: "https://ntbar.asn.au/",
      description: "Find a barrister in NT"
    },
    lawSociety: {
      name: "Law Society Northern Territory",
      url: "https://lawsocietynt.asn.au/",
      description: "Find a solicitor"
    },
    specialists: [
      { name: "Territory Criminal Lawyers", url: "https://www.territorycriminallawyers.com/", location: "Darwin" },
      { name: "Maleys Barristers & Solicitors", url: "https://www.maleyslegal.com/", location: "Darwin CBD" },
      { name: "Ward Keller Lawyers", url: "https://www.wardkeller.com.au/", location: "Darwin" },
      { name: "Grays Legal NT", url: "https://www.lawyerdarwin.au/", location: "Darwin" }
    ]
  },
  {
    state: "Australian Capital Territory",
    code: "ACT",
    color: "bg-indigo-600",
    legalAid: {
      name: "Legal Aid ACT",
      url: "https://www.legalaidact.org.au/",
      phone: "1300 654 314",
      description: "Legal Aid services in the ACT"
    },
    barAssociation: {
      name: "ACT Bar Association",
      url: "https://www.actbar.com.au/",
      description: "Find a barrister in ACT"
    },
    lawSociety: {
      name: "Law Society of the ACT",
      url: "https://www.actlawsociety.asn.au/",
      description: "Find a solicitor"
    },
    specialists: [
      { name: "O'Brien Criminal & Civil Solicitors", url: "https://obriensolicitors.com.au/", location: "Canberra" },
      { name: "Andrew Byrnes Law Group", url: "https://www.andrewbyrneslawgroup.com.au/", location: "Canberra City" },
      { name: "Hugo Law Group", url: "https://hugolawgroup.com.au/", location: "Canberra" },
      { name: "Lamont Law", url: "https://lamontlaw.com.au/", location: "Canberra" }
    ]
  }
];

const nationalResources = [
  {
    name: "National Association of Community Legal Centres",
    url: "https://www.naclc.org.au/",
    description: "Find free community legal centres across Australia"
  },
  {
    name: "Law Council of Australia",
    url: "https://www.lawcouncil.asn.au/",
    description: "Peak body for the legal profession"
  },
  {
    name: "Australian Pro Bono Centre",
    url: "https://www.probonocentre.org.au/",
    description: "Information about pro bono legal services"
  },
  {
    name: "Justice Connect",
    url: "https://justiceconnect.org.au/",
    description: "Connecting people with free legal help"
  }
];

const LawyerDirectory = () => {

  const [selectedState, setSelectedState] = useState("all");
  
  const filteredResources = selectedState === "all" 
    ? lawyerResources 
    : lawyerResources.filter(r => r.code.toLowerCase() === selectedState.toLowerCase());

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center" data-testid="lawyer-directory-brand-icon">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight" style={{ fontFamily: "'Times New Roman', Times, serif" }} data-testid="lawyer-directory-brand-text">
              Appeal Case Manager
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/" data-testid="lawyer-directory-back-link">
              <Button className="landing-cta-primary" data-testid="lawyer-directory-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero with Image */}
      <section className="relative py-8 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="/images/stock/legal-library.jpg" 
            alt="Legal Professionals"
            className="w-full h-full object-cover opacity-10"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-500/30">
            <Users className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Find a Criminal Appeal Lawyer
          </h1>
          <p className="text-lg text-slate-700 max-w-2xl mx-auto mb-2">
            Connect with qualified criminal law specialists, Legal Aid services, and pro bono resources across Australia.
          </p>
          <p className="text-sm text-slate-700">
            <strong>{lawyerResources.length} states</strong> + National resources
          </p>
        </div>
      </section>

      {/* State Filter */}
      <section className="px-6 pb-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-wrap justify-center gap-2">
            <button
              onClick={() => setSelectedState("all")}
              className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                selectedState === "all"
                  ? "bg-red-600 text-white shadow-lg"
                  : "bg-white border border-slate-200 text-slate-700 hover:border-blue-500"
              }`}
            >
              All States
            </button>
            {lawyerResources.map(resource => (
              <button
                key={resource.code}
                onClick={() => setSelectedState(resource.code.toLowerCase())}
                className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  selectedState === resource.code.toLowerCase()
                    ? `${resource.color} text-white shadow-lg`
                    : "bg-white border border-slate-200 text-slate-700 hover:border-blue-500"
                }`}
              >
                {resource.code}
              </button>
            ))}
          </div>
        </div>
      </section>

      <main className="max-w-6xl mx-auto px-6 pb-16">
        {/* Important Notice */}
        <div className="mb-10 p-5 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
              <Gavel className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h3 className="font-semibold text-blue-900 text-xs mb-1">Important</h3>
              <p className="text-blue-800 text-[11px]">
                This directory provides links to legal resources for informational purposes only. 
                This directory does not endorse any specific lawyer or firm.
              </p>
            </div>
          </div>
        </div>

        {/* National Resources */}
        <div className="mb-8">
          <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 mb-4 flex items-center gap-3">
            <Globe className="w-5 h-5 text-blue-700" />
            <div>
              <h2 className="text-sm font-bold text-blue-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                National Resources
              </h2>
              <p className="text-blue-700 text-[10px]">Australia-wide legal services</p>
            </div>
          </div>
          
          <div className="grid md:grid-cols-2 gap-3">
            {nationalResources.map((resource, index) => (
              <a key={index} href={resource.url} target="_blank" rel="noopener noreferrer" className="block">
                <div className="bg-white border border-slate-200 rounded-lg p-3 h-full hover:shadow-md hover:border-blue-300 transition-all group">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-900 text-xs group-hover:text-blue-600">{resource.name}</h3>
                      <p className="text-[11px] text-slate-700 mt-1">{resource.description}</p>
                    </div>
                    <ExternalLink className="w-3 h-3 text-slate-500 group-hover:text-blue-600 flex-shrink-0" />
                  </div>
                </div>
              </a>
            ))}
          </div>
        </div>

        {/* State Resources */}
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3 mb-4 flex items-center gap-3">
          <MapPin className="w-5 h-5 text-emerald-700" />
          <div>
            <h2 className="text-sm font-bold text-emerald-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Resources by State
            </h2>
            <p className="text-emerald-700 text-[10px]">State-specific legal services and specialists</p>
          </div>
        </div>
        
        <div className="space-y-6">
          {filteredResources.map((state, index) => (
            <div className={`bg-white border border-slate-200 rounded-xl overflow-hidden hover:shadow-md transition-all`}>
              <div className={`${state.color} text-white px-4 py-2`}>
                <h3 className="text-sm font-bold flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  <Badge variant="outline" className="bg-white/20 border-white/40 text-white text-[10px] px-2 py-0">
                    {state.code}
                  </Badge>
                  {state.state}
                </h3>
              </div>
              <div className="p-4">
                <div className="grid md:grid-cols-3 gap-4">
                  {/* Legal Aid */}
                  <div className="bg-slate-50 p-3 rounded-lg">
                    <h4 className="font-semibold text-slate-900 text-xs mb-2 flex items-center gap-1.5">
                      <Building2 className="w-3 h-3 text-blue-700" />
                      Legal Aid
                    </h4>
                    <a
                      href={state.legalAid.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-700 hover:underline text-xs font-medium flex items-center gap-1"
                    >
                      {state.legalAid.name}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                    <p className="text-[10px] text-slate-700 mt-1">{state.legalAid.description}</p>
                    {state.legalAid.phone && (
                      <p className="text-xs text-slate-900 mt-3 flex items-center gap-2 font-medium">
                        <Phone className="w-3 h-3 text-emerald-600" />
                        {state.legalAid.phone}
                      </p>
                    )}
                  </div>

                  {/* Bar Association */}
                  <div className="bg-slate-50 p-3 rounded-lg">
                    <h4 className="font-semibold text-slate-900 text-xs mb-2 flex items-center gap-1.5">
                      <Gavel className="w-3 h-3 text-purple-700" />
                      Find a Barrister
                    </h4>
                    <a
                      href={state.barAssociation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-700 hover:underline text-xs font-medium flex items-center gap-1"
                    >
                      {state.barAssociation.name}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                    <p className="text-[10px] text-slate-700 mt-1">{state.barAssociation.description}</p>
                  </div>

                  {/* Law Society */}
                  <div className="bg-slate-50 p-3 rounded-lg">
                    <h4 className="font-semibold text-slate-900 text-xs mb-2 flex items-center gap-1.5">
                      <Users className="w-3 h-3 text-emerald-700" />
                      Find a Solicitor
                    </h4>
                    <a
                      href={state.lawSociety.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-700 hover:underline text-xs font-medium flex items-center gap-1"
                    >
                      {state.lawSociety.name}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                    <p className="text-[10px] text-slate-700 mt-1">{state.lawSociety.description}</p>
                  </div>
                </div>

                {/* Specialists */}
                {state.specialists.length > 0 && (
                  <div className="mt-6 pt-4 border-t border-slate-200">
                    <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">
                      Criminal Law Specialists
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {state.specialists.map((specialist, idx) => (
                        <a
                          key={idx}
                          href={specialist.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs bg-white border border-slate-200 hover:border-blue-300 hover:bg-slate-50 text-slate-900 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
                        >
                          {specialist.name}
                          {specialist.location && (
                            <span className="text-[10px] text-slate-500 ml-1">({specialist.location})</span>
                          )}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* CTA with Image */}
      </main>
    </div>
  );
};

export default LawyerDirectory;
