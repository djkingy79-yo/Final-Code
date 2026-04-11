import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { CheckCircle, Loader2, XCircle, ArrowLeft } from "lucide-react";
import { Button } from "../components/ui/button";
import { API } from "../App";

export default function PaymentSuccessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState("checking"); // checking, paid, failed, error
  const [paymentInfo, setPaymentInfo] = useState(null);
  const [attempts, setAttempts] = useState(0);

  const sessionId = searchParams.get("session_id");
  const caseId = searchParams.get("case_id");
  const featureType = searchParams.get("feature_type");

  useEffect(() => {
    if (!sessionId) {
      setStatus("error");
      return;
    }
    pollStatus();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const pollStatus = async (attempt = 0) => {
    const maxAttempts = 6;
    const pollInterval = 2000;

    if (attempt >= maxAttempts) {
      setStatus("failed");
      return;
    }

    try {
      const response = await axios.get(`${API}/payments/stripe/status/${sessionId}`);
      const data = response.data;
      setPaymentInfo(data);

      if (data.payment_status === "paid") {
        setStatus("paid");
        toast.success("Payment confirmed! Feature unlocked.");
        return;
      } else if (data.status === "expired") {
        setStatus("failed");
        return;
      }

      // Continue polling
      setAttempts(attempt + 1);
      setTimeout(() => pollStatus(attempt + 1), pollInterval);
    } catch {
      if (attempt < maxAttempts - 1) {
        setTimeout(() => pollStatus(attempt + 1), pollInterval);
      } else {
        setStatus("error");
      }
    }
  };

  const featureNames = {
    grounds_of_merit: "Grounds of Merit",
    full_report: "Full Detailed Report",
    extensive_report: "Extensive Log Report",
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center" data-testid="payment-success-page">
        {status === "checking" && (
          <>
            <Loader2 className="w-16 h-16 text-blue-500 mx-auto mb-4 animate-spin" />
            <h1 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Processing Payment
            </h1>
            <p className="text-slate-600 text-sm">
              Confirming your payment with Stripe... (Attempt {attempts + 1})
            </p>
          </>
        )}

        {status === "paid" && (
          <>
            <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-12 h-12 text-emerald-600" />
            </div>
            <h1 className="text-2xl font-bold text-emerald-800 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Payment Confirmed
            </h1>
            <p className="text-slate-600 text-sm mb-4">
              <strong>{featureNames[featureType] || featureType}</strong> has been unlocked successfully.
            </p>
            {paymentInfo?.amount && (
              <p className="text-slate-500 text-sm mb-6">
                Amount paid: <strong>${paymentInfo.amount.toFixed(2)} AUD</strong>
              </p>
            )}
            <Button
              onClick={() => navigate(caseId ? `/cases/${caseId}` : "/dashboard")}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl text-base"
              data-testid="payment-success-continue-btn"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              {caseId ? "Return to Case" : "Go to Dashboard"}
            </Button>
          </>
        )}

        {(status === "failed" || status === "error") && (
          <>
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-12 h-12 text-red-600" />
            </div>
            <h1 className="text-2xl font-bold text-red-800 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              {status === "error" ? "Payment Error" : "Payment Not Confirmed"}
            </h1>
            <p className="text-slate-600 text-sm mb-6">
              {status === "error"
                ? "Something went wrong while checking your payment. Please contact support."
                : "The payment could not be confirmed. If you completed the payment, it may take a moment to process. Try returning to your case and refreshing."}
            </p>
            <div className="space-y-3">
              <Button
                onClick={() => pollStatus(0)}
                variant="outline"
                className="w-full py-4 rounded-xl text-base"
                data-testid="payment-retry-btn"
              >
                <Loader2 className="w-5 h-5 mr-2" /> Retry Check
              </Button>
              <Button
                onClick={() => navigate(caseId ? `/cases/${caseId}` : "/dashboard")}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl text-base"
                data-testid="payment-return-btn"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                {caseId ? "Return to Case" : "Go to Dashboard"}
              </Button>
            </div>
          </>
        )}

        <p className="text-xs text-slate-500 mt-6">
          Questions? <a href="mailto:djkingy79@gmail.com" className="text-blue-600 hover:underline">djkingy79@gmail.com</a>
        </p>
      </div>
    </div>
  );
}
