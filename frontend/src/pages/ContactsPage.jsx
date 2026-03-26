/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import PageCTA from "../components/PageCTA";
import { Scale, ArrowLeft, Moon, Sun, Menu, X, Phone, Globe, ExternalLink, ChevronDown, Building, Users, AlertTriangle, Shield, Gavel } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const ContactsPage = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-slate-900 sticky top-0 z-50">
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
            <Link to="/faq" className="text-slate-400 hover:text-white text-sm transition-colors">FAQ</Link>
            <Link to="/legal-resources" className="text-slate-400 hover:text-white text-sm transition-colors">Resources</Link>
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
            <Link to="/faq" className="block py-2 text-slate-300 hover:text-white">FAQ</Link>
            <Link to="/legal-resources" className="block py-2 text-slate-300 hover:text-white">Resources</Link>
            <Link to="/" className="block py-2 text-blue-500 hover:text-blue-400">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-12 px-6 bg-gradient-to-b from-slate-900 to-slate-800 text-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-600 flex items-center justify-center">
              <Building className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Legal Contacts Directory
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto">
            All legal assistance contacts across Australia in one place. Legal Aid, Law Societies, Complaints Bodies, Courts, Community Legal Centres, and Pro Bono services.
          </p>
          <div className="mt-5">
            <Link to="/contact" data-testid="legal-contacts-contact-deb-link">
              <Button className="bg-red-600 hover:bg-blue-700 text-white rounded-lg">
                Contact Deb Directly
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-12">

        {/* Legal Aid Section */}
          <div id="legal-aid" className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Legal Aid Services
              </h2>
              <p className="text-slate-600 text-sm">
                Government-funded legal assistance available in every state and territory.
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
                website="https://www.ntlac.nt.gov.au"
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

        {/* Law Societies Section */}
          <div id="law-societies" className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Law Societies & Bar Associations
              </h2>
              <p className="text-slate-600 text-sm">
                Professional bodies representing solicitors and barristers. They offer referral services and handle complaints.
              </p>
            </div>

            {/* Solicitors */}
            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Law Societies (Solicitors)
              </h3>
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
                  website="https://www.taslawsociety.asn.au"
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
            </div>

            {/* Bar Associations */}
            <div className="mt-8">
              <h3 className="text-lg font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
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

        {/* Complaints Section */}
          <div id="complaints" className="space-y-6">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Complaints Bodies & Legal Services Commissioners
              </h2>
              <p className="text-slate-600 text-sm">
                If you have a complaint about a lawyer's conduct, fees, or service, these independent bodies can investigate.
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
          </div>

        {/* Courts Section */}
          <div id="courts" className="space-y-6">
            <div className="bg-slate-100 border border-slate-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Courts of Australia
              </h2>
              <p className="text-slate-600 text-sm">
                Direct links to court websites for filing, forms, and case information.
              </p>
            </div>

            {/* Federal Courts */}
            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Federal Courts
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <ResourceCard
                  title="High Court of Australia"
                  state="Federal"
                  phone="(02) 6270 6811"
                  website="https://www.hcourt.gov.au"
                  description="Australia's highest court."
                  color="slate"
                />
                <ResourceCard
                  title="Federal Court of Australia"
                  state="Federal"
                  phone="1300 720 980"
                  website="https://www.fedcourt.gov.au"
                  description="Handles federal law matters."
                  color="slate"
                />
              </div>
            </div>

            {/* State Courts - NSW */}
            <div className="mt-8">
              <h3 className="text-lg font-bold text-blue-600 mb-4">
                New South Wales Courts
              </h3>
              <div className="grid md:grid-cols-3 gap-3">
                <SmallResourceCard title="Supreme Court NSW" website="https://www.supremecourt.justice.nsw.gov.au" />
                <SmallResourceCard title="Court of Criminal Appeal" website="https://www.supremecourt.justice.nsw.gov.au/Pages/sco2_criminalappeal/sco2_criminalappeal.aspx" />
                <SmallResourceCard title="District Court NSW" website="https://www.districtcourt.justice.nsw.gov.au" />
              </div>
            </div>

            {/* VIC */}
            <div className="mt-6">
              <h3 className="text-lg font-bold text-purple-600 mb-4">
                Victoria Courts
              </h3>
              <div className="grid md:grid-cols-3 gap-3">
                <SmallResourceCard title="Supreme Court VIC" website="https://www.supremecourt.vic.gov.au" />
                <SmallResourceCard title="Court of Appeal VIC" website="https://www.supremecourt.vic.gov.au/court-of-appeal" />
                <SmallResourceCard title="County Court VIC" website="https://www.countycourt.vic.gov.au" />
              </div>
            </div>

            {/* QLD */}
            <div className="mt-6">
              <h3 className="text-lg font-bold text-red-600 mb-4">
                Queensland Courts
              </h3>
              <div className="grid md:grid-cols-3 gap-3">
                <SmallResourceCard title="Supreme Court QLD" website="https://www.courts.qld.gov.au/courts/supreme-court" />
                <SmallResourceCard title="Court of Appeal QLD" website="https://www.courts.qld.gov.au/courts/court-of-appeal" />
                <SmallResourceCard title="District Court QLD" website="https://www.courts.qld.gov.au/courts/district-court" />
              </div>
            </div>

            {/* Other States */}
            <div className="mt-6">
              <h3 className="text-lg font-bold text-slate-600 mb-4">
                Other State & Territory Courts
              </h3>
              <div className="grid md:grid-cols-3 gap-3">
                <SmallResourceCard title="Supreme Court SA" website="https://www.courts.sa.gov.au/courts/supreme-court" />
                <SmallResourceCard title="Supreme Court WA" website="https://www.supremecourt.wa.gov.au" />
                <SmallResourceCard title="Supreme Court TAS" website="https://www.supremecourt.tas.gov.au" />
                <SmallResourceCard title="Supreme Court NT" website="https://supremecourt.nt.gov.au" />
                <SmallResourceCard title="Supreme Court ACT" website="https://www.courts.act.gov.au/supreme" />
              </div>
            </div>
          </div>

        {/* Community Legal Section */}
          <div id="community" className="space-y-6">
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Community Legal Centres
              </h2>
              <p className="text-slate-600 text-sm">
                Independent, non-profit organisations providing free legal advice and assistance.
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
              <h3 className="text-lg font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
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

        {/* Pro Bono Section */}
          <div id="pro-bono" className="space-y-6">
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Pro Bono Legal Services
              </h2>
              <p className="text-slate-600 text-sm">
                Many law firms and barristers provide free legal services for those who cannot afford representation.
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
                title="QPILCH"
                state="QLD"
                phone="(07) 3846 6317"
                website="https://www.qpilch.org.au"
                description="Queensland Public Interest Law Clearing House - pro bono referrals."
                color="red"
              />
            </div>
          </div>

      </main>

      {/* Footer */}
      <footer className="bg-slate-900 px-6 py-8 border-t border-slate-800 mt-12">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-slate-400 text-sm">
            All contact information is publicly available. Links open in a new tab to official websites.
          </p>
          <p className="text-red-400 text-xs mt-2 font-medium">
            This is not legal advice. Always verify information directly with the relevant organisation.
          </p>
        </div>
      </footer>
    </div>
  );
};

// Resource Card Component
const ResourceCard = ({ title, state, phone, website, description, color, highlight }) => {
  const colorClasses = {
    blue: "bg-blue-600",
    purple: "bg-purple-600",
    red: "bg-red-600",
    blue_mapped: "bg-red-600",
    emerald: "bg-emerald-600",
    teal: "bg-teal-600",
    orange: "bg-orange-600",
    indigo: "bg-indigo-600",
    slate: "bg-slate-700",
    pink: "bg-pink-600",
  };

  return (
    <div className={`bg-white border ${highlight ? 'border-blue-400 border-2' : 'border-slate-200'} rounded-xl p-5 hover:shadow-md transition-shadow`}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 ${colorClasses[color]} rounded-lg flex items-center justify-center text-white text-xs font-bold shrink-0`}>
            {state.slice(0, 3)}
          </div>
          <h3 className="font-bold text-slate-900 text-sm leading-tight">{title}</h3>
        </div>
      </div>
      <p className="text-slate-600 text-xs mb-3">{description}</p>
      <div className="space-y-2 text-sm">
        {phone && phone !== "N/A" && (
          <a href={`tel:${phone.replace(/[^0-9]/g, '')}`} className="flex items-center gap-2 text-slate-600 hover:text-slate-900">
            <Phone className="w-4 h-4 text-emerald-600" />
            <span>{phone}</span>
          </a>
        )}
        {website && (
          <a href={website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-blue-600 hover:underline">
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
    className="flex items-center gap-2 p-3 bg-slate-50 hover:bg-slate-100 rounded-lg text-sm transition-colors group"
  >
    <Gavel className="w-4 h-4 text-slate-600 group-hover:text-slate-900 shrink-0" />
    <span className="text-slate-900 truncate">{title}</span>
    <ExternalLink className="w-3 h-3 text-slate-600 ml-auto shrink-0" />
  </a>
);

export default ContactsPage;
