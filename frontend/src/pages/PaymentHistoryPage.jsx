import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import {
  ArrowLeft,
  CreditCard,
  Building2,
  Download,
  Loader2,
  CheckCircle,
  Clock,
  XCircle,
  AlertCircle,
  DollarSign,
  FileText,
  Briefcase,
  Mail,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { API } from "../App";

const STATUS_CONFIG = {
  completed: { icon: CheckCircle, color: "text-emerald-600", bg: "bg-emerald-50", border: "border-emerald-200", label: "Confirmed" },
  submitted: { icon: Clock, color: "text-amber-600", bg: "bg-amber-50", border: "border-amber-200", label: "Awaiting Confirmation" },
  pending: { icon: Clock, color: "text-slate-500", bg: "bg-slate-50", border: "border-slate-200", label: "Pending" },
  submitted_for_review: { icon: Clock, color: "text-amber-600", bg: "bg-amber-50", border: "border-amber-200", label: "Under Review" },
  failed: { icon: XCircle, color: "text-red-600", bg: "bg-red-50", border: "border-red-200", label: "Failed" },
  expired: { icon: XCircle, color: "text-red-500", bg: "bg-red-50", border: "border-red-200", label: "Expired" },
};

const METHOD_CONFIG = {
  stripe: { icon: CreditCard, label: "Card", color: "text-blue-600" },
  payid: { icon: Building2, label: "PayID", color: "text-emerald-600" },
};

function formatDate(isoStr) {
  if (!isoStr) return "—";
  try {
    const dt = new Date(isoStr);
    return dt.toLocaleDateString("en-AU", {
      day: "numeric", month: "short", year: "numeric",
    });
  } catch {
    return isoStr.slice(0, 10);
  }
}

function formatDateTime(isoStr) {
  if (!isoStr) return "—";
  try {
    const dt = new Date(isoStr);
    return dt.toLocaleDateString("en-AU", {
      day: "numeric", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return isoStr.slice(0, 19);
  }
}

function SummaryCard({ icon: Icon, label, value, subtext, color }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 flex items-start gap-4" data-testid={`summary-${label.toLowerCase().replace(/\s/g, "-")}`}>
      <div className={`w-11 h-11 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-wide font-medium">{label}</p>
        <p className="text-2xl font-bold text-slate-900 mt-0.5" style={{ fontFamily: "'Times New Roman', Times, serif" }}>{value}</p>
        {subtext && <p className="text-xs text-slate-500 mt-0.5">{subtext}</p>}
      </div>
    </div>
  );
}

function PaymentRow({ payment, onDownloadReceipt, downloading }) {
  const status = STATUS_CONFIG[payment.status] || STATUS_CONFIG.pending;
  const method = METHOD_CONFIG[payment.method] || METHOD_CONFIG.payid;
  const StatusIcon = status.icon;
  const MethodIcon = method.icon;

  return (
    <div className={`bg-white border ${status.border} rounded-xl p-4 sm:p-5 transition-all hover:shadow-sm`} data-testid={`payment-row-${payment.payment_id}`}>
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        {/* Feature & Case */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="font-semibold text-slate-900 text-sm truncate">{payment.feature_name}</p>
            {payment.is_trial && (
              <span className="text-[10px] px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">TRIAL</span>
            )}
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <MethodIcon className={`w-3.5 h-3.5 ${method.color}`} />
              {method.label}
            </span>
            <span>{formatDate(payment.created_at)}</span>
            <span className="truncate max-w-[120px]">Ref: {payment.reference}</span>
          </div>
        </div>

        {/* Amount */}
        <div className="text-right sm:text-left sm:w-28">
          <p className="text-lg font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            ${payment.amount?.toFixed(2)}
          </p>
          <p className="text-[10px] text-slate-400 uppercase">AUD</p>
        </div>

        {/* Status */}
        <div className="sm:w-40 flex items-center gap-2">
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${status.bg} ${status.border} border`}>
            <StatusIcon className={`w-3.5 h-3.5 ${status.color}`} />
            <span className={`text-xs font-medium ${status.color}`}>{status.label}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="sm:w-24 flex justify-end">
          {payment.status === "completed" && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onDownloadReceipt(payment.payment_id, payment.reference)}
              disabled={downloading === payment.payment_id}
              className="text-xs h-8 px-3"
              data-testid={`download-receipt-${payment.payment_id}`}
            >
              {downloading === payment.payment_id ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <><Download className="w-3.5 h-3.5 mr-1" />Receipt</>
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Case link */}
      {payment.case_id && (
        <div className="mt-2 pt-2 border-t border-slate-100">
          <Link
            to={`/cases/${payment.case_id}`}
            className="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
            data-testid={`case-link-${payment.case_id}`}
          >
            <Briefcase className="w-3 h-3" />
            View Case
          </Link>
        </div>
      )}
    </div>
  );
}

export default function PaymentHistoryPage() {
  const [payments, setPayments] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(null);
  const [filter, setFilter] = useState("all"); // all, completed, pending

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [historyRes, summaryRes] = await Promise.all([
        axios.get(`${API}/payments/history`),
        axios.get(`${API}/payments/history/summary`),
      ]);
      setPayments(historyRes.data.payments || []);
      setSummary(summaryRes.data);
    } catch (err) {
      toast.error("Failed to load payment history");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReceipt = async (paymentId, reference) => {
    setDownloading(paymentId);
    try {
      const response = await axios.get(`${API}/payments/receipt/${paymentId}/pdf`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Receipt_${reference || paymentId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Receipt downloaded");
    } catch {
      toast.error("Failed to download receipt");
    } finally {
      setDownloading(null);
    }
  };

  const filtered = payments.filter((p) => {
    if (filter === "completed") return p.status === "completed";
    if (filter === "pending") return p.status !== "completed";
    return true;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50" data-testid="payment-history-page">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="text-slate-500 hover:text-slate-700" data-testid="back-to-dashboard">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Payment History
              </h1>
              <p className="text-xs text-slate-500 mt-0.5">View all payments and download receipts</p>
            </div>
          </div>
          <a
            href="mailto:djkingy79@gmail.com"
            className="flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-800 hover:underline"
            data-testid="contact-support-link"
          >
            <Mail className="w-4 h-4" />
            <span className="hidden sm:inline">Contact Support</span>
          </a>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="summary-cards">
            <SummaryCard
              icon={DollarSign}
              label="Total Spent"
              value={`$${summary.total_spent?.toFixed(2) || "0.00"}`}
              subtext="AUD"
              color="bg-blue-600"
            />
            <SummaryCard
              icon={CheckCircle}
              label="Completed"
              value={summary.completed_payments || 0}
              subtext={`of ${summary.total_payments || 0} total`}
              color="bg-emerald-600"
            />
            <SummaryCard
              icon={FileText}
              label="Features Unlocked"
              value={summary.features_unlocked_count || 0}
              subtext="premium features"
              color="bg-indigo-600"
            />
            <SummaryCard
              icon={Briefcase}
              label="Cases"
              value={summary.cases_with_payments || 0}
              subtext="with payments"
              color="bg-slate-700"
            />
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
          {[
            { key: "all", label: "All Payments" },
            { key: "completed", label: "Confirmed" },
            { key: "pending", label: "Pending" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                filter === tab.key
                  ? "bg-blue-600 text-white"
                  : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
              }`}
              data-testid={`filter-${tab.key}`}
            >
              {tab.label}
              {tab.key === "all" && ` (${payments.length})`}
              {tab.key === "completed" && ` (${payments.filter(p => p.status === "completed").length})`}
              {tab.key === "pending" && ` (${payments.filter(p => p.status !== "completed").length})`}
            </button>
          ))}
        </div>

        {/* Payments List */}
        {filtered.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center" data-testid="empty-payments">
            <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-600 font-medium">No payments found</p>
            <p className="text-sm text-slate-400 mt-1">
              {filter !== "all"
                ? "Try changing the filter above"
                : "Payments will appear here once you unlock premium features"}
            </p>
            <Link to="/dashboard">
              <Button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white" data-testid="go-to-dashboard-btn">
                Go to Dashboard
              </Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-3" data-testid="payments-list">
            {filtered.map((payment) => (
              <PaymentRow
                key={payment.payment_id}
                payment={payment}
                onDownloadReceipt={handleDownloadReceipt}
                downloading={downloading}
              />
            ))}
          </div>
        )}

        {/* Footer */}
        <div className="text-center pt-4 pb-8 border-t border-slate-100">
          <p className="text-xs text-slate-400">
            Questions about a payment?{" "}
            <a href="mailto:djkingy79@gmail.com" className="text-blue-600 hover:underline">
              djkingy79@gmail.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
