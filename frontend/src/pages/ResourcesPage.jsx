/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "../App";
import { 
  ArrowLeft, Phone, Globe, MapPin, Users, Scale, 
  Building, Clock, ExternalLink, Search
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

const ResourcesPage = () => {
  const navigate = useNavigate();
  const [resources, setResources] = useState(null);
  const [loading, setLoading] = useState(true);
  const [setSearchQuery] = useState("");

  useEffect(() => {
    const fetchResources = async () => {
      try {
        const response = await axios.get(`${API}/resources/directory`);
        setResources(response.data);
      } catch (error) {
        console.error("Failed to fetch resources:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchResources();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-slate-300 border-t-slate-900 rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate(-1)}
              className="text-slate-600 hover:text-slate-900"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back
            </Button>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-emerald-600" />
              <h1 className="text-xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Resource Directory
              </h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Intro */}
        <Card className="mb-8 bg-gradient-to-r from-emerald-900 to-emerald-800 text-white">
          <CardContent className="p-6">
            <h2 className="text-2xl font-bold mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Support Services & Resources
            </h2>
            <p className="text-emerald-100">
              Free and low-cost support services, advocacy groups, and resources to help with your criminal appeal in NSW.
            </p>
          </CardContent>
        </Card>

        {/* Appeal Deadlines Alert */}
        <Card className="mb-8 bg-blue-50 border-blue-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-blue-800">
              <Clock className="w-5 h-5" />
              Important Appeal Deadlines
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-white p-3 rounded-lg border border-blue-200">
                <p className="font-semibold text-blue-900">Notice of Appeal</p>
                <p className="text-sm text-blue-700">{resources?.appeal_deadlines?.notice_of_appeal}</p>
              </div>
              <div className="bg-white p-3 rounded-lg border border-blue-200">
                <p className="font-semibold text-blue-900">Leave to Appeal</p>
                <p className="text-sm text-blue-700">{resources?.appeal_deadlines?.leave_to_appeal}</p>
              </div>
              <div className="bg-white p-3 rounded-lg border border-blue-200">
                <p className="font-semibold text-blue-900">Extension of Time</p>
                <p className="text-sm text-blue-700">{resources?.appeal_deadlines?.extension}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Support Services */}
        <section className="mb-8">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Scale className="w-5 h-5 text-slate-600" />
            Support Services
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {resources?.support_services?.map((org, i) => (
              <Card key={i} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <h4 className="font-semibold text-slate-900 mb-2">{org.name}</h4>
                  <div className="space-y-2 text-sm">
                    {org.phone && (
                      <p className="flex items-center gap-2 text-slate-600">
                        <Phone className="w-4 h-4 text-emerald-600" />
                        <a href={`tel:${org.phone.replace(/\s/g, '')}`} className="hover:text-emerald-600">
                          {org.phone}
                        </a>
                      </p>
                    )}
                    {org.website && (
                      <p className="flex items-center gap-2 text-slate-600">
                        <Globe className="w-4 h-4 text-blue-600" />
                        <a href={org.website} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 flex items-center gap-1">
                          Visit website <ExternalLink className="w-3 h-3" />
                        </a>
                      </p>
                    )}
                    {org.region && (
                      <Badge variant="outline" className="bg-slate-50">{org.region}</Badge>
                    )}
                  </div>
                  {org.services && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {org.services.map((service, j) => (
                        <Badge key={j} variant="secondary" className="text-xs bg-emerald-50 text-emerald-700">
                          {service}
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Advocacy Groups */}
        <section className="mb-8">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Users className="w-5 h-5 text-slate-600" />
            Advocacy & Support Groups
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {resources?.advocacy_groups?.map((org, i) => (
              <Card key={i} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <h4 className="font-semibold text-slate-900 mb-1">{org.name}</h4>
                  {org.focus && (
                    <p className="text-sm text-purple-700 mb-2">{org.focus}</p>
                  )}
                  <div className="space-y-2 text-sm">
                    {org.phone && (
                      <p className="flex items-center gap-2 text-slate-600">
                        <Phone className="w-4 h-4 text-emerald-600" />
                        <a href={`tel:${org.phone.replace(/\s/g, '')}`} className="hover:text-emerald-600">
                          {org.phone}
                        </a>
                      </p>
                    )}
                    {org.website && (
                      <p className="flex items-center gap-2 text-slate-600">
                        <Globe className="w-4 h-4 text-blue-600" />
                        <a href={org.website} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 flex items-center gap-1">
                          Visit website <ExternalLink className="w-3 h-3" />
                        </a>
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Courts */}
        <section className="mb-8">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Building className="w-5 h-5 text-slate-600" />
            Courts
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {resources?.courts?.map((court, i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <h4 className="font-semibold text-slate-900 mb-2">{court.name}</h4>
                  {court.website && (
                    <p className="flex items-center gap-2 text-sm text-slate-600 mb-2">
                      <Globe className="w-4 h-4 text-blue-600" />
                      <a href={court.website} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 flex items-center gap-1">
                        Official website <ExternalLink className="w-3 h-3" />
                      </a>
                    </p>
                  )}
                  {court.address && (
                    <p className="flex items-start gap-2 text-sm text-slate-600">
                      <MapPin className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                      {court.address}
                    </p>
                  )}
                  {court.note && (
                    <p className="text-sm text-red-600 mt-2 italic">{court.note}</p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Footer */}
        <div className="mt-8 text-center text-slate-500 text-sm">
          <p className="font-medium">Deb King, Glenmore Park 2745</p>
          <p className="italic">One woman's fight for justice — seeking truth for Joshua Homann, failed by the system</p>
        </div>
      </main>
    </div>
  );
};

export default ResourcesPage;
