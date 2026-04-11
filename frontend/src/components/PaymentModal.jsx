import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  Lock, Check, Loader2, Building2, Copy, CheckCircle,
  AlertCircle, X, Smartphone, Search, ArrowLeft
} from "lucide-react";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "./ui/dialog";
import { API } from "../App";

const FEATURE_INFO = {
  grounds_of_merit: {
    title: "Unlock Grounds of Merit Details",
    description: "See full descriptions, supporting evidence, and detailed analysis of each potential ground for appeal.",
    benefits: [
      "Full descriptions of all grounds identified",
      "Supporting evidence from your documents",
      "Relevant law sections and citations",
      "Deep investigation feature unlocked"
    ]
  },
  full_report: {
    title: "Full Detailed Report",
    description: "Comprehensive legal analysis with similar cases, legislation links, and appeal filing guide.",
    benefits: [
      "Detailed legal analysis with legislation references",
      "4-6 similar cases with AustLII decision links",
      "Step-by-step appeal filing guide for your court",
      "Strategic recommendations for presenting your case",
      "PDF and Word export + Barrister View"
    ]
  },
  extensive_report: {
    title: "Extensive Log Report",
    description: "The ultimate forensic-level analysis — a barrister's primary working document.",
    benefits: [
      "Everything in the Full Report, plus:",
      "12-15 similar cases with AustLII decision links",
      "Complete step-by-step appeal filing guide for ALL court levels",
      "Detailed outcome analysis for each comparative case",
      "Sentencing comparison with before/after sentence modelling",
      "Complete appeal strategy with oral & written submission advice",
      "Links to required appeal forms and court registries",
      "Barrister conference dossier"
    ]
  }
};

const PAYID_INFO = {
  payid: "djkingy79@gmail.com",
  account_name: "Deb King - Appeal Case Manager",
  bank: "NAB"
};

const FEATURE_PRICES_DISPLAY = {
  grounds_of_merit: 99,
  full_report: 150,
  extensive_report: 200,
};

export default function PaymentModal({ 
  isOpen, 
  onClose, 
  caseId, 
  featureType, 
  price,
  useTrial,
  onPaymentSuccess 
}) {
  const [loading, setLoading] = useState(false);
  const [payidReference, setPayidReference] = useState(null);
  const [payidDetails, setPayidDetails] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const [copied, setCopied] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const featureInfo = FEATURE_INFO[featureType] || { 
    title: "Premium Feature", 
    description: "", 
    benefits: [] 
  };

  useEffect(() => {
    if (isOpen) {
      setPayidReference(null);
      setPayidDetails(null);
      setVerifying(false);
      setCopied("");
      setSubmitted(false);
      setLoading(false);
    }
  }, [isOpen]);

  const copyToClipboard = (text, field) => {
    navigator.clipboard.writeText(text);
    setCopied(field);
    setTimeout(() => setCopied(""), 2000);
    toast.success("Copied to clipboard!");
  };

  // ─── PayID Flow ───
  const handlePayIDStart = async () => {
    if (!caseId || !featureType) {
      toast.error("Missing payment information");
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${API}/payments/payid/create-reference`, {
        feature_type: featureType,
        case_id: caseId,
        use_trial: !!useTrial
      });
      setPayidReference(response.data.reference);
      setPayidDetails(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to generate payment reference");
    } finally {
      setLoading(false);
    }
  };

  const handlePayIDVerify = async () => {
    if (!payidReference) return;
    setVerifying(true);
    try {
      const response = await axios.post(`${API}/payments/payid/verify`, {
        reference: payidReference,
        case_id: caseId,
        feature_type: featureType
      });
      if (response.data.status === "already_verified") {
        toast.success("Payment verified! Feature unlocked.");
        onPaymentSuccess?.();
        onClose();
      } else if (response.data.status === "submitted_for_review" || response.data.status === "pending_verification") {
        setSubmitted(true);
        toast.success(response.data.message || "Payment submitted! The admin has been notified and will confirm shortly.");
      } else {
        toast.info(response.data.message);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Verification failed");
    } finally {
      setVerifying(false);
    }
  };

  const handleCheckStatus = async () => {
    setVerifying(true);
    try {
      const response = await axios.post(`${API}/payments/payid/verify`, {
        reference: payidReference,
        case_id: caseId,
        feature_type: featureType
      });
      if (response.data.status === "already_verified") {
        toast.success("Payment confirmed! Feature unlocked.");
        onPaymentSuccess?.();
        onClose();
      } else {
        toast.info("Payment is still awaiting admin confirmation. You will receive an email once confirmed.");
      }
    } catch (error) {
      toast.error("Unable to check status. Please try again.");
    } finally {
      setVerifying(false);
    }
  };

  const handleClose = () => {
    onPaymentSuccess?.();
    onClose();
  };

  // ─── Payment Screen (PayID Only) ───
  const renderPaymentScreen = () => (
    <div className="space-y-4 py-2">
      {/* Price display */}
      <div className={`rounded-xl p-4 text-center border ${useTrial ? 'bg-gradient-to-r from-blue-600 to-blue-800 border-blue-500' : 'bg-gradient-to-r from-slate-50 to-blue-50 border-slate-200'}`}>
        {useTrial && (
          <p className="text-xs font-bold text-white uppercase tracking-wider mb-1" data-testid="trial-label">
            One-Time Trial Offer
          </p>
        )}
        <p className={`text-sm mb-1 ${useTrial ? 'text-white/80' : 'text-slate-600'}`}>One-time payment</p>
        {useTrial ? (
          <div>
            <span className="text-lg line-through text-white/50 mr-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              ${FEATURE_PRICES_DISPLAY[featureType]?.toFixed(2) || "99.00"}
            </span>
            <span className="text-3xl sm:text-4xl font-bold text-pink-400" style={{ fontFamily: "'Times New Roman', Times, serif" }} data-testid="trial-price">
              ${price?.toFixed(2)} <span className="text-base font-normal text-white/80">AUD</span>
            </span>
          </div>
        ) : (
          <p className="text-3xl sm:text-4xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            ${price?.toFixed(2)} <span className="text-base font-normal text-slate-600">AUD</span>
          </p>
        )}
      </div>

      {/* Benefits */}
      <details className="group">
        <summary className="flex items-center justify-between cursor-pointer text-sm font-medium text-slate-900 py-2">
          <span>What you get ({featureInfo.benefits.length} features)</span>
          <span className="text-slate-600 group-open:rotate-180 transition-transform">&#x25BC;</span>
        </summary>
        <ul className="space-y-1 pt-2">
          {featureInfo.benefits.map((benefit, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
              <Check className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
              <span className="text-xs sm:text-sm">{benefit}</span>
            </li>
          ))}
        </ul>
      </details>

      {/* PayID Payment */}
      <div className="space-y-3">
        <p className="text-sm font-semibold text-slate-800 text-center">Pay via PayID (Bank Transfer)</p>

        <Button
          onClick={() => handlePayIDStart()}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-base rounded-xl min-h-[56px] flex items-center justify-center gap-3"
          data-testid="pay-by-payid-btn"
        >
          {loading ? (
            <><Loader2 className="w-5 h-5 animate-spin" />Getting Payment Details...</>
          ) : (
            <>
              <Building2 className="w-5 h-5" />
              <span>Pay by PayID</span>
              <span className="text-xs opacity-80 ml-1">Bank Transfer</span>
            </>
          )}
        </Button>
      </div>

      <p className="text-xs text-slate-600 text-center pt-2">
        Questions? <a href="mailto:djkingy79@gmail.com" className="text-red-600 hover:underline">djkingy79@gmail.com</a>
      </p>
    </div>
  );

  // ─── PayID Flow Screen ───
  const renderPayIDFlow = () => (
    <div className="space-y-4 py-2">
      {/* Back button */}
      <button
        onClick={() => { setPayidDetails(null); setPayidReference(null); }}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
        data-testid="payid-back-btn"
      >
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      {!payidDetails ? (
        <>
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <Smartphone className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-emerald-800 text-sm">Pay via your banking app</p>
                <p className="text-emerald-700 text-xs mt-1">
                  Open your bank app, select "Pay Anyone" then "PayID" and enter:
                </p>
              </div>
            </div>
            
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between bg-white rounded-lg p-3">
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-slate-600">PayID (Email)</p>
                  <p className="font-mono font-bold text-emerald-700 text-sm truncate">{PAYID_INFO.payid}</p>
                </div>
                <Button size="sm" variant="outline" onClick={() => copyToClipboard(PAYID_INFO.payid, "payid-preview")} className="shrink-0 ml-2 h-10 px-3">
                  {copied === "payid-preview" ? <CheckCircle className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                </Button>
              </div>
              
              <div className="bg-white rounded-lg p-3">
                <p className="text-xs text-slate-600">Account Name (verify this matches)</p>
                <p className="font-semibold text-emerald-700 text-sm">{PAYID_INFO.account_name}</p>
              </div>
              
              <div className="bg-blue-100 rounded-lg p-3">
                <p className="text-xs text-blue-700">Amount to transfer</p>
                <p className="font-bold text-blue-800 text-xl">${price?.toFixed(2)} AUD</p>
              </div>
            </div>
          </div>

          <Button
            onClick={handlePayIDStart}
            disabled={loading}
            className="w-full bg-blue-700 hover:bg-blue-600 text-white py-6 text-base rounded-xl min-h-[56px]"
            data-testid="payid-start-btn"
          >
            {loading ? (
              <><Loader2 className="w-5 h-5 mr-2 animate-spin" />Getting Reference...</>
            ) : (
              <><Building2 className="w-5 h-5 mr-2" />Get My Payment Reference</>
            )}
          </Button>
          
          <p className="text-xs text-center text-slate-600">
            Click above to get your unique reference code to include in the transfer
          </p>
        </>
      ) : (
        <div className="space-y-4">
          <div className="bg-white border-2 border-emerald-500 rounded-xl p-4">
            <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2 text-base">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              Transfer These Details
            </h4>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-slate-600">PayID (Email)</p>
                  <p className="font-mono font-semibold text-slate-900 text-sm truncate">{payidDetails.payid}</p>
                </div>
                <Button size="sm" variant="ghost" onClick={() => copyToClipboard(payidDetails.payid, "payid")} className="shrink-0 ml-2 h-10 w-10 p-0">
                  {copied === "payid" ? <CheckCircle className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
                </Button>
              </div>

              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div>
                  <p className="text-xs text-blue-700">Amount</p>
                  <p className="font-bold text-blue-800 text-xl">${payidDetails.amount.toFixed(2)} AUD</p>
                </div>
                <Button size="sm" variant="ghost" onClick={() => copyToClipboard(payidDetails.amount.toFixed(2), "amount")} className="shrink-0 h-10 w-10 p-0">
                  {copied === "amount" ? <CheckCircle className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
                </Button>
              </div>

              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border-2 border-red-400">
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-red-700 font-semibold">REFERENCE (Required)</p>
                  <p className="font-mono font-bold text-red-800 text-lg">{payidDetails.reference}</p>
                </div>
                <Button size="sm" variant="ghost" onClick={() => copyToClipboard(payidDetails.reference, "ref")} className="shrink-0 ml-2 h-10 w-10 p-0">
                  {copied === "ref" ? <CheckCircle className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
                </Button>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4 text-sm">
            <p className="font-semibold text-blue-800 mb-2 flex items-center gap-2">
              <Smartphone className="w-4 h-4" />
              In Your Banking App:
            </p>
            <ol className="list-decimal list-inside space-y-1 text-blue-700 text-xs">
              <li>Pay Anyone &rarr; PayID</li>
              <li>Enter: <strong>{payidDetails.payid}</strong></li>
              <li>Amount: <strong>${payidDetails.amount.toFixed(2)}</strong></li>
              <li>Description: <strong>{payidDetails.reference}</strong></li>
              <li>Send payment</li>
            </ol>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
              <p className="text-xs text-blue-800">
                <strong>Include the reference</strong> in your transfer description so we can match your payment.
              </p>
            </div>
          </div>

          <div className="space-y-3 pt-1">
            {submitted ? (
              <>
                <div className="bg-emerald-50 border-2 border-emerald-300 rounded-xl p-4 text-center">
                  <CheckCircle className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
                  <p className="font-semibold text-emerald-800 text-sm mb-1">Payment Submitted for Review</p>
                  <p className="text-xs text-emerald-700">
                    The admin has been notified. Once confirmed, click the button below or refresh this page to unlock your content.
                  </p>
                </div>
                <Button
                  onClick={handleCheckStatus}
                  disabled={verifying}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 rounded-xl min-h-[56px] text-base"
                  data-testid="payid-check-status-btn"
                >
                  {verifying ? (
                    <><Loader2 className="w-5 h-5 mr-2 animate-spin" />Checking...</>
                  ) : (
                    <><Search className="w-5 h-5 mr-2" />Check if Payment Confirmed</>
                  )}
                </Button>
                <Button
                  onClick={handleClose}
                  variant="outline"
                  className="w-full text-sm min-h-[48px]"
                >
                  Close &amp; Refresh Page
                </Button>
              </>
            ) : (
              <>
                <Button
                  onClick={handlePayIDVerify}
                  disabled={verifying}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 rounded-xl min-h-[56px] text-base"
                  data-testid="payid-verify-btn"
                >
                  {verifying ? (
                    <><Loader2 className="w-5 h-5 mr-2 animate-spin" />Checking...</>
                  ) : (
                    <><CheckCircle className="w-5 h-5 mr-2" />I've Sent the Payment</>
                  )}
                </Button>

                <Button
                  onClick={() => { setPayidDetails(null); setPayidReference(null); }}
                  className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm min-h-[48px]"
                  data-testid="payid-start-over-btn"
                >
                  <X className="w-4 h-4 mr-1" /> Start Over
                </Button>
              </>
            )}
          </div>
        </div>
      )}

      <p className="text-xs text-slate-600 text-center pt-2">
        Questions? <a href="mailto:djkingy79@gmail.com" className="text-red-600 hover:underline">djkingy79@gmail.com</a>
      </p>
    </div>
  );

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="w-[95vw] max-w-lg max-h-[90vh] overflow-y-auto p-4 sm:p-6" data-testid="payment-modal">
        <DialogHeader className="space-y-2">
          <DialogTitle className="flex items-center gap-2 text-lg" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Lock className="w-5 h-5 text-blue-500 shrink-0" />
            <span className="line-clamp-1">{featureInfo.title}</span>
          </DialogTitle>
          <DialogDescription className="text-sm">
            {featureInfo.description}
          </DialogDescription>
        </DialogHeader>

        {payidDetails ? renderPayIDFlow() : renderPaymentScreen()}
      </DialogContent>
    </Dialog>
  );
}
