import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { Loader2, Scale, Share2, AlertCircle } from "lucide-react";
import { Button } from "../components/ui/button";
import { API } from "../App";

export default function AcceptShareLink() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);

  const sessionToken = localStorage.getItem("session_token");

  useEffect(() => {
    if (!sessionToken) {
      localStorage.setItem("pending_share_token", token);
      toast.info("Please sign in to accept the shared case");
      navigate("/");
      return;
    }
    acceptLink();
  }, [token, sessionToken]);

  const acceptLink = async () => {
    try {
      const res = await axios.post(`${API}/share-link/${token}/accept`, {}, {
        headers: { Authorization: `Bearer ${sessionToken}` }
      });
      toast.success(res.data.message || "Case access granted!");
      navigate(`/cases/${res.data.case_id}`);
    } catch (e) {
      setStatus("error");
      setError(e.response?.data?.detail || "Failed to accept share link");
    }
  };

  if (status === "error") {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Unable to Access Case
          </h2>
          <p className="text-sm text-slate-600 mb-6">{error}</p>
          <Button onClick={() => navigate("/dashboard")} className="bg-blue-600 hover:bg-blue-700 text-white">
            Go to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 max-w-md text-center">
        <Loader2 className="w-10 h-10 text-blue-600 animate-spin mx-auto mb-4" />
        <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
          Joining Shared Case...
        </h2>
        <p className="text-sm text-slate-600 mt-2">Setting up your access</p>
      </div>
    </div>
  );
}
