/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect, useMemo, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { isIOSDevice } from "../utils/isIOS";
import ReportTranslator from "../components/ReportTranslator";
import {
  Scale,
  ArrowLeft,
  Download,
  Printer,
  
  Loader2,
  FileText,
  ListOrdered,
  
  ChevronRight,
  
  
  Clock,
  
  AlertTriangle,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { API } from "../App";
import ReportMetadataPanel from "../components/ReportMetadataPanel";
import VerificationBadge from "../components/VerificationBadge";
import auSpelling from "../utils/auSpelling";
import { normaliseMarkdown } from "../utils/mdRender";

const titleFromSnake = (value) => {
  if (!value) return "Not specified";
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
};

const cleanSentence = (s) => {
  if (!s) return s;
  let c = s
    .replace(/\s*\[.*$/, "")
    .replace(/\s*\(https?:.*$/, "")
    .replace(/\s*\(http.*$/, "")
    .replace(/\s*https?:.*$/, "")
    .replace(/\s*[|•].*$/, "")
    .replace(/[,;:]?\s*(?:appeal|conviction|leave|outcome)\b.*$/i, "")
    .replace(/[,;:]?\s*(?:dismissed|upheld|refused|granted)\b.*$/i, "")
    .replace(/\s+for\s+[a-z\s'-]+(?=,|\s+with\b|$)/i, "")
    .replace(/\bminimum\s+non[- ]?parole\s+period\b/gi, "non-parole period")
    .replace(/\bwith\s+a\s+minimum\s+non[- ]?parole\s+period\b/gi, "with a non-parole period")
    .replace(/imprisonment,\s+with/gi, "imprisonment with");
  c = c.trim();
  // Truncate overly long sentences — extract just the core penalty
  if (c.length > 120) {
    const nppMatch = c.match(/(\d+\s*(?:years?|months?)\s*(?:imprisonment|gaol|jail|custody|in prison)[^,]*(?:,?\s*(?:with\s+a?\s*)?(?:non[- ]?parole|NPP)\s*(?:period\s*(?:of|set at)?\s*)?(?:over\s+)?\d+\s*(?:years?|months?))?)/i);
    if (nppMatch?.[1]) {
      c = nppMatch[1].replace(/\s*for\s+(?:murdering|killing|assaulting|robbing)[^,]*/i, "").trim();
    }
    // Check for life sentence
    const lifeMatch = c.match(/(life\s+(?:imprisonment|sentence)(?:\s+with(?:out)?\s+(?:parole|a\s+non[- ]?parole\s+period\s+of\s+\d+\s+years?))?)/i);
    if (lifeMatch?.[1]) {
      c = lifeMatch[1];
    }
    if (c.length > 120) c = c.substring(0, 117) + "...";
  }
  return c.trim();
};

const isValidSentenceCandidate = (candidate = "") => {
  if (!candidate || candidate === "Not recorded") return false;
  if (!/(life|year|month|non[- ]?parole|imprisonment|gaol|custody|sentence)/i.test(candidate)) return false;
  if (/\b(reduced|reduce|precedent|appeal|submissions|could|should|potentially|perhaps|would|adequacy|seek|sought|relief)\b/i.test(candidate)) return false;
  return candidate.length < 140;
};

const extractSentenceSummary = (caseInfo, analysis = "") => {
  if (caseInfo?.sentence && caseInfo.sentence.trim().length > 3) return caseInfo.sentence.trim();
  const bySentenceImposed = analysis.match(/(?:sentence\s+imposed\s+was|sentence\s+was|head\s+sentence\s+was|head\s+sentence:|sentenced?\s+to)\s+([^\.\n]{8,160})/i);
  if (bySentenceImposed?.[1]) {
    const cleaned = cleanSentence(bySentenceImposed[1]);
    if (isValidSentenceCandidate(cleaned)) return cleaned;
  }
  const byExactYears = analysis.match(/(\d+\s+years?'?\s+with\s+a\s+non[- ]?parole\s+period\s+of\s+\d+\s+years?(?:\s+and\s+\d+\s+months?)?)/i);
  if (byExactYears?.[1] && isValidSentenceCandidate(cleanSentence(byExactYears[1]))) return cleanSentence(byExactYears[1]);
  const byThirtyStyle = analysis.match(/(\d+\s+years?'?(?:\s+and\s+\d+\s+months?)?\s*(?:imprisonment|gaol|jail|custody)?\s*(?:with\s+(?:a\s+)?non[- ]?parole\s+period\s+of\s+\d+\s+years?(?:\s+and\s+\d+\s+months?)?)?)/i);
  if (byThirtyStyle?.[1] && /non[- ]?parole|imprisonment|gaol|custody/i.test(byThirtyStyle[1]) && isValidSentenceCandidate(cleanSentence(byThirtyStyle[1]))) return cleanSentence(byThirtyStyle[1]);
  const combined = analysis.match(/sentenced?\s+to\s+([^\n\.]{10,180}?(?:non[- ]?parole\s+period|NPP)[^\n\.]{0,160})/i);
  if (combined?.[1] && isValidSentenceCandidate(cleanSentence(combined[1]))) return cleanSentence(combined[1]);
  // Match "sentenced to X years imprisonment" patterns
  const byVerb = analysis.match(/(?:was\s+)?sentenced?\s+to\s+(\d+\s*(?:years?|months?)\s+(?:and\s+\d+\s*(?:years?|months?)\s+)?(?:imprisonment|gaol|jail|custody)[^\n\.]{0,80})/i);
  if (byVerb?.[1] && isValidSentenceCandidate(cleanSentence(byVerb[1]))) return cleanSentence(byVerb[1]);
  // Match "Head Sentence: X years"
  const byHead = analysis.match(/(?:^|\n)\s*(?:Head\s+)?Sentence\s*:\s*(\d+[^\n]{5,100})/im);
  if (byHead?.[1] && /\d+\s*(year|month|life)/i.test(byHead[1]) && isValidSentenceCandidate(cleanSentence(byHead[1]))) return cleanSentence(byHead[1]);
  // Match "life imprisonment" / "imprisonment for life"
  const byLife = analysis.match(/(?:sentenced?\s+to\s+)?(life\s+imprisonment|imprisonment\s+for\s+life|life\s+sentence)[^\n\.]{0,60}/i);
  if (byLife && isValidSentenceCandidate(cleanSentence(byLife[0].replace(/^sentenced?\s+to\s+/i, "")))) return cleanSentence(byLife[0].replace(/^sentenced?\s+to\s+/i, ""));
  // Match "X years' imprisonment" or "X-year sentence"
  const byYears = analysis.match(/(\d+[\s-]*(?:years?|months?)(?:'s?)?\s*(?:imprisonment|gaol|jail|custody|sentence|non[- ]?parole)[^\n\.]{0,80})/i);
  if (byYears?.[1] && isValidSentenceCandidate(cleanSentence(byYears[1]))) return cleanSentence(byYears[1]);
  // Match "sentence of X years"
  const bySentOf = analysis.match(/sentence\s+of\s+(\d+[^\n\.]{5,80})/i);
  if (bySentOf?.[1] && isValidSentenceCandidate(cleanSentence(bySentOf[1]))) return cleanSentence(bySentOf[1]);
  // Match "minimum/non-parole period of X years"
  const byNPP = analysis.match(/((?:minimum|non[- ]?parole)\s+(?:period\s+)?of\s+\d+[^\n\.]{3,60})/i);
  if (byNPP?.[1] && isValidSentenceCandidate(cleanSentence(byNPP[1]))) return cleanSentence(byNPP[1]);
  return "Not recorded";
};

const extractSentenceFromSourceReports = (reports = [], caseInfo = null, fallbackAnalysis = "") => {
  const typeOrder = ["quick_summary", "full_detailed", "extensive_log", "barrister_view"];

  for (const reportType of typeOrder) {
    const orderedReports = [...reports]
      .filter((item) => item?.report_type === reportType)
      .sort((a, b) => new Date(b?.generated_at || 0) - new Date(a?.generated_at || 0));

    for (const item of orderedReports) {
      const candidate = extractSentenceSummary(caseInfo, item?.content?.analysis || "")
        .replace(/^sentence\s*[:\-]?\s*/i, "")
        .trim();
      if (isValidSentenceCandidate(candidate)) {
        return candidate;
      }
    }
  }

  return extractSentenceSummary(caseInfo, fallbackAnalysis);
};

const sanitiseReportOutput = (text = "") => {
  if (!text) return text;
  const filtered = text.split(/\n/).filter((line) => {
    if (/\[Your Name\]|\[Your Legal Organisation\/Team\]/i.test(line)) return false;
    if (/Best regards|Prepared by|Prepared for|This report was generated by|Criminal Appeal AI|Justitia AI/i.test(line)) return false;
    if (/\bDO NOT UNDO\.?\b/i.test(line)) return false;
    return true;
  });
  let cleaned = filtered.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  // Strip "you/your" language — third-person only
  const youReplacements = [
    [/\byour opportunity\b/gi, 'the opportunity'],
    [/\byour conviction\b/gi, 'the conviction'],
    [/\bgiven to you\b/gi, 'imposed'],
    [/\byour sentence\b/gi, 'the sentence'],
    [/\byour appeal\b/gi, 'the appeal'],
    [/\byour case\b/gi, 'the case'],
    [/\byour trial\b/gi, 'the trial'],
    [/\byour lawyer\b/gi, 'the legal representative'],
    [/\byour barrister\b/gi, 'the barrister'],
    [/\byour solicitor\b/gi, 'the solicitor'],
    [/\byour legal team\b/gi, 'the legal team'],
    [/\byour legal representative\b/gi, 'the legal representative'],
    [/\byour defence\b/gi, 'the defence'],
    [/\byour rights\b/gi, "the rights of the applicant"],
    [/\byour circumstances\b/gi, 'the circumstances'],
    [/\byour prospects\b/gi, 'the prospects'],
    [/\byour grounds\b/gi, 'the grounds'],
    [/\bYou may\b/g, 'The applicant may'],
    [/\byou may\b/g, 'the applicant may'],
    [/\bYou can\b/g, 'The applicant can'],
    [/\byou can\b/g, 'the applicant can'],
    [/\bYou should\b/g, 'The applicant should'],
    [/\byou should\b/g, 'the applicant should'],
    [/\bYou must\b/g, 'The applicant must'],
    [/\byou must\b/g, 'the applicant must'],
    [/\bYou will\b/g, 'The applicant will'],
    [/\byou will\b/g, 'the applicant will'],
    [/\bYou need\b/g, 'The applicant needs'],
    [/\byou need\b/g, 'the applicant needs'],
    [/\bYou have\b/g, 'The applicant has'],
    [/\byou have\b/g, 'the applicant has'],
    [/\bYou are\b/g, 'The applicant is'],
    [/\byou are\b/g, 'the applicant is'],
    [/\bYou were\b/g, 'The applicant was'],
    [/\byou were\b/g, 'the applicant was'],
    [/\bfor you\b/gi, 'for the applicant'],
    [/\bto you\b/gi, 'to the applicant'],
    [/\bagainst you\b/gi, 'against the applicant'],
    [/\bif you\b/gi, 'if the applicant'],
    [/\bwhen you\b/gi, 'when the applicant'],
    [/\byour\b/g, "the applicant's"],
    [/\bYour\b/g, "The applicant's"],
  ];
  for (const [pattern, replacement] of youReplacements) {
    cleaned = cleaned.replace(pattern, replacement);
  }
  // Strip placeholder filler text
  cleaned = cleaned.replace(/(?:The |This )?(?:comparative sentencing |sentencing )?table (?:below )?will (?:reference|provide|include|contain|show|list|detail|present|outline|cover)\b/gi, 'The table references');
  return cleaned;
};

const extractOffenceFromAnalysis = (analysis = "") => {
  const patterns = [
    /(?:offence(?:s)?\s+of|for\s+the\s+offence\s+of|convicted\s+of|charged\s+with)\s+([A-Z][A-Za-z0-9\s,'-]{4,120})/i,
    /(?:primary|principal)\s+offence(?:\s+was|:)?\s+([A-Z][A-Za-z0-9\s,'-]{4,120})/i,
    /(?:count\s+\d+\s*[:\-])\s*([A-Z][A-Za-z0-9\s,'-]{4,120})/i
  ];

  for (const pattern of patterns) {
    const match = analysis.match(pattern);
    if (match?.[1]) {
      return match[1]
        .replace(/under\s+s\.[^\n\.]+/i, "")
        .replace(/,?\s*(?:under|pursuant\s+to).*/i, "")
        .replace(/\s+(?:on|by|amid(?:st)?|with|during)\b.*$/i, "")
        .replace(/\s+of\b.*$/i, "")
        .trim();
    }
  }
  return "";
};

const extractDefendantFromAnalysis = (analysis = "") => {
  const byCaseName = analysis.match(/\bR\s+v\.?\s+([A-Z][A-Za-z\s'\-]{2,60})/);
  if (byCaseName?.[1]) return byCaseName[1].trim();
  const byAppellant = analysis.match(/(?:the\s+)?appellant\s+([A-Z][A-Za-z\s'\-]{2,60})/i);
  if (byAppellant?.[1]) return byAppellant[1].trim();
  const byDefendant = analysis.match(/(?:the\s+)?defendant\s+(?:was|is|,)?\s*([A-Z][A-Za-z\s'\-]{2,60})/i);
  if (byDefendant?.[1]) return byDefendant[1].trim();
  return "N/A";
};

const cleanAIContent = (text) => {
  if (!text) return text;
  let cleaned = text;
  // Strip AI preamble lines ("Certainly!", "Here's a comprehensive...", "Sure!", etc.)
  cleaned = cleaned.replace(/^(Certainly!|Sure!|Of course!|Absolutely!|Here('s| is) a comprehensive[^\n]*\n?)/i, "");
  cleaned = cleaned.replace(/^(Here('s| is) (a |the |your )?detailed[^\n]*\n?)/i, "");
  cleaned = cleaned.replace(/^(Here('s| is) (a |the |your )?thorough[^\n]*\n?)/i, "");
  cleaned = cleaned.replace(/^(I('ve| have) (prepared|created|compiled|generated)[^\n]*\n?)/i, "");
  // Strip \1 artifacts
  cleaned = cleaned.replace(/\\1/g, "");
  cleaned = cleaned.replace(/\u0001/g, "");
  // Strip bracket placeholder notes — BOTH square [] and round () brackets
  cleaned = cleaned.replace(/\[Note:\s*[^\]]*\]/gi, "");

  // Strip prompt instruction text from section headings (e.g. "— keep ALL outcome pathways in this ONE section")
  cleaned = cleaned.replace(/\s*—\s*keep ALL[^\n]*/gi, "");
  cleaned = cleaned.replace(/\s*—\s*DETAILED PATHWAY ANALYSIS[^\n]*/gi, "");
  cleaned = cleaned.replace(/\s*—\s*keep ALL timeframes[^\n]*/gi, "");
  cleaned = cleaned.replace(/\s*—\s*keep ALL timeframes in this ONE section/gi, "");
  // Strip parenthesised word counts from headings like "(900+ words per ground, flowing paragraphs)"
  cleaned = cleaned.replace(/\s*\(\d+\+?\s*words[^)]*\)/gi, "");
  // Strip "— DEEP ANALYSIS" from headings
  cleaned = cleaned.replace(/(GROUNDS OF MERIT)\s*—\s*DEEP ANALYSIS/gi, "$1");
  // Remove parenthesised instructions like "(12+ CASES with full citations...)"
  cleaned = cleaned.replace(/\s*\(\d+\+?\s*CASES[^)]*\)/gi, "");
  // Clean "keep ALL ... in this ONE section" remnants
  cleaned = cleaned.replace(/\s*—?\s*keep ALL[^.\n]*/gi, "");
  cleaned = cleaned.replace(/\[Continue[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Repeat[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Follow[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Insert[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Add[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Include[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Provide[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Similar[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[See[^\]]*\]/gi, "");
  // Round bracket notes — (Note: ...), (See: ...), etc.
  cleaned = cleaned.replace(/\(Note:\s*[^)]*\)/gi, "");
  cleaned = cleaned.replace(/\(See:\s*[^)]*\)/gi, "");
  cleaned = cleaned.replace(/\(Continue[^)]*\)/gi, "");
  cleaned = cleaned.replace(/\(Link formatting[^)]*\)/gi, "");
  cleaned = cleaned.replace(/\(Entries will[^)]*\)/gi, "");
  // Strip AI meta-commentary about truncation or its own output
  cleaned = cleaned.replace(/\n*This truncated document[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*This (?:document|report|analysis) (?:provides|covers|contains|demonstrates)[^\n]*(?:sections?|overview|summary)[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*Each section (?:demonstrates|provides|covers)[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*The sections? above (?:are|is|were|was) (?:crafted|designed|written|prepared|created)[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*(?:The above|These) sections? (?:are|is|were|was) (?:crafted|designed|written|prepared|created)[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*(?:presenting|advances?) (?:a comprehensive|field-specific|detailed)[^\n]*(?:court of appeal|legal professionals?)[^\n]*/gi, "");
  
  // Strip "we/us/our" language — convert to third-person educational tone
  const weUsReplacements = [
    [/\bWe are arguing\b/g, 'The applicant argues'],
    [/\bwe are arguing\b/g, 'the applicant argues'],
    [/\bWe are aiming\b/g, 'The appeal aims'],
    [/\bwe are aiming\b/g, 'the appeal aims'],
    [/\bWe are filing\b/g, 'The legal professional is filing'],
    [/\bwe are filing\b/g, 'the legal professional is filing'],
    [/\bWe are taking\b/g, 'The legal professional is taking'],
    [/\bwe are taking\b/g, 'the legal professional is taking'],
    [/\bWe succeed\b/g, 'The appeal succeeds'],
    [/\bwe succeed\b/g, 'the appeal succeeds'],
    [/\bwe will gather\b/g, 'the legal professional will gather'],
    [/\bWe will gather\b/g, 'The legal professional will gather'],
    [/\bwe will craft\b/g, 'the legal professional will craft'],
    [/\bWe will craft\b/g, 'The legal professional will craft'],
    [/\bwe will file\b/g, 'the legal professional will file'],
    [/\bWe will file\b/g, 'The legal professional will file'],
    [/\bwe will prepare\b/g, 'the legal professional will prepare'],
    [/\bWe will prepare\b/g, 'The legal professional will prepare'],
    [/\bwe will submit\b/g, 'the legal professional will submit'],
    [/\bWe will submit\b/g, 'The legal professional will submit'],
    [/\bwe will seek\b/g, 'the applicant will seek'],
    [/\bWe will seek\b/g, 'The applicant will seek'],
    [/\bwe will argue\b/g, 'the applicant will argue'],
    [/\bWe will argue\b/g, 'The applicant will argue'],
    [/\bwe will demonstrate\b/g, 'the appeal will demonstrate'],
    [/\bWe will demonstrate\b/g, 'The appeal will demonstrate'],
    [/\bwe will show\b/g, 'the appeal will show'],
    [/\bWe will show\b/g, 'The appeal will show'],
    [/\bcontact with us\b/g, 'contact with the legal professional'],
    [/\bContact us\b/g, 'Contact the legal professional'],
    [/\bcontact us\b/g, 'contact the legal professional'],
    [/\bour submissions\b/g, 'the submissions'],
    [/\bOur submissions\b/g, 'The submissions'],
    [/\bour claims\b/g, "the applicant's claims"],
    [/\bOur claims\b/g, "The applicant's claims"],
    [/\bour arguments\b/g, "the applicant's arguments"],
    [/\bOur arguments\b/g, "The applicant's arguments"],
    [/\bour position\b/g, "the applicant's position"],
    [/\bOur position\b/g, "The applicant's position"],
    [/\bour case\b/g, "the applicant's case"],
    [/\bOur case\b/g, "The applicant's case"],
    [/\bour strategy\b/g, "the legal strategy"],
    [/\bOur strategy\b/g, "The legal strategy"],
    [/\bour analysis\b/g, "this analysis"],
    [/\bOur analysis\b/g, "This analysis"],
    [/\bon our behalf\b/g, "on behalf of the applicant"],
    [/\bback our\b/g, "support the applicant's"],
    [/\bensuring our\b/g, "ensuring the"],
    [/\b, we are\b/g, ', the legal professional is'],
    [/\b, we will\b/g, ', the legal professional will'],
    [/\b, we have\b/g, ', the legal professional has'],
    [/\bWe have identified\b/g, 'This analysis has identified'],
    [/\bwe have identified\b/g, 'this analysis has identified'],
    [/\bWe have reviewed\b/g, 'This analysis has reviewed'],
    [/\bwe have reviewed\b/g, 'this analysis has reviewed'],
    [/\bWe have analysed\b/g, 'This analysis has examined'],
    [/\bwe have analysed\b/g, 'this analysis has examined'],
    [/\bWe have analyzed\b/g, 'This analysis has examined'],
    [/\bwe have analyzed\b/g, 'this analysis has examined'],
    [/\bWe argue\b/g, 'The applicant argues'],
    [/\bwe argue\b/g, 'the applicant argues'],
    [/\byour legal team\b/g, 'the legal professional'],
    [/\bYour legal team\b/g, 'The legal professional'],
    [/\byou've been\b/g, 'the applicant has been'],
    [/\bYou've been\b/g, 'The applicant has been'],
  ];
  for (const [pattern, replacer] of weUsReplacements) {
    cleaned = cleaned.replace(pattern, replacer);
  }

  // DO_NOT_UNDO — Convert American spellings to Australian English in all report content.
  // Uses shared auSpelling utility for comprehensive coverage.
  cleaned = auSpelling(cleaned);

  // DO_NOT_UNDO — Forensic appellate language enforcement (safety net for backend filter)
  const forensicFixes = [
    [/^The judge failed to/gm, 'It is arguable that the judge failed to'],
    [/^The trial judge failed to/gm, 'It is arguable that the trial judge failed to'],
    [/^The sentencing judge failed to/gm, 'It is arguable that the sentencing judge failed to'],
    [/^The judge was wrong/gm, 'It is arguable that the judge was wrong'],
    [/^The judge made an error/gm, 'It is arguable that the judge made an error'],
    [/^The judge was biased/gm, 'It is arguable that the judge was biased'],
    [/^The judge misdirected/gm, 'It is arguable that the judge misdirected'],
    [/^The trial judge misdirected/gm, 'It is arguable that the trial judge misdirected'],
    [/^The jury was misdirected/gm, 'It is arguable that the jury was misdirected'],
    [/^The judge ignored/gm, 'It is arguable that the judge ignored'],
    [/^The judge disregarded/gm, 'It is arguable that the judge disregarded'],
    [/^The judge overlooked/gm, 'It is arguable that the judge overlooked'],
    [/^The court ignored/gm, 'It is arguable that the court ignored'],
    [/^The court wrongly/gm, 'It is arguable that the court wrongly'],
    [/^The court improperly/gm, 'It is arguable that the court improperly'],
    [/^The judge should have/gm, 'It is arguable that the judge should have'],
    [/^The judge ought to have/gm, 'It is arguable that the judge ought to have'],
    [/^The trial was unfair/gm, 'It is arguable that the trial was unfair'],
    [/^The verdict is unreasonable/gm, 'It is arguable that the verdict is unreasonable'],
    [/^The verdict was unreasonable/gm, 'It is arguable that the verdict was unreasonable'],
    [/^The sentence is inadequate/gm, 'It is arguable that the sentence is inadequate'],
    [/^The sentence was inadequate/gm, 'It is arguable that the sentence was inadequate'],
    [/^The directions were inadequate/gm, 'It is arguable that the directions were inadequate'],
    [/^The evidence was wrongly/gm, 'It is arguable that the evidence was wrongly'],
    [/^The evidence was improperly/gm, 'It is arguable that the evidence was improperly'],
    [/^There was no proper/gm, 'It is arguable that there was no proper'],
    [/^There was a failure to/gm, 'It is arguable that there was a failure to'],
    [/\bwas clearly wrong\b/g, 'was arguably wrong'],
    [/\bwas plainly wrong\b/g, 'was arguably wrong'],
    [/\bwas fundamentally flawed\b/g, 'was arguably fundamentally flawed'],
    [/\bno reasonable judge\b/g, 'arguably no reasonable judge'],
  ];
  for (const [pattern, replacer] of forensicFixes) {
    cleaned = cleaned.replace(pattern, replacer);
  }
  
  return cleaned.trim();
};

const parseAnalysisSections = (analysis = "") => {
  // Normalise the markdown FIRST so sections with single-newline separators,
  // trailing two-space hard breaks, or missing blank lines around ## headings
  // are all detected correctly.
  const normalised = normaliseMarkdown(analysis.replace(/\r\n/g, "\n").trim());
  const text = cleanAIContent(normalised);
  if (!text) return [];
  const lines = text.split("\n");
  const sections = [];
  const cleanSectionTitle = (value) => (value || "")
    .replace(/^\d+\.\s*/, "")
    .replace(/[\-:]+$/, "")
    .replace(/\*\*/g, "")
    .trim();
  let currentTitle = "Executive Analysis";
  let currentLines = [];

  const pushSection = () => {
    const content = cleanAIContent(currentLines.join("\n").trim());
    // Push sections even when content is short — a heading with little body
    // is still a navigable landmark for the reader. Only skip truly empty ones.
    if (!content) return;
    sections.push({ id: `report-section-${sections.length + 1}`, title: currentTitle, content });
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    // Accept three heading shapes (in priority order):
    //   1. ## 1. TITLE            (numbered, LLM's default)
    //   2. ## TITLE IN ALL CAPS   (all-caps fallback)
    //   3. ## Any Section Title   (mixed-case fallback — covers barrister
    //      synthesis sections like "## Executive Overview for Counsel")
    const mainSectionHeader =
      trimmed.match(/^##\s+(\d+\.?\s+.+)$/) ||
      trimmed.match(/^##\s+([A-Z][A-Z\s\-&+:]+)$/) ||
      trimmed.match(/^##\s+([A-Z][A-Za-z][^\n]*?)$/);
    if (mainSectionHeader) {
      pushSection();
      currentTitle = cleanSectionTitle(mainSectionHeader[1]);
      currentLines = [];
      return;
    }
    currentLines.push(line);
  });

  pushSection();
  return sections.length > 0 ? sections : [{ id: "report-section-1", title: "Analysis", content: text }];
};

const MarkdownBlock = ({ text, testId }) => (
  <div className="legal-report text-slate-900" data-testid={testId}>
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-700 underline underline-offset-2 hover:text-blue-500 break-words font-medium">{children}</a>
        ),
        table: ({ children }) => (
          <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch', display: 'block', maxWidth: '100%', margin: '1rem 0', border: '1px solid #cbd5e1', borderRadius: '16px', background: '#ffffff' }} data-testid={`${testId}-table-wrapper`}>
            <table style={{ width: 'max-content', minWidth: '100%', borderCollapse: 'collapse', tableLayout: 'auto' }}>{children}</table>
          </div>
        ),
        thead: ({ children }) => (
          <thead style={{ background: '#1e3a8a' }}>{children}</thead>
        ),
        th: ({ children }) => (
          <th style={{ background: '#1e3a8a', color: '#ffffff', fontWeight: 700, fontSize: '0.8rem', padding: '8px 10px', border: '1px solid #cbd5e1', verticalAlign: 'top', whiteSpace: 'normal', wordBreak: 'break-word' }}>{children}</th>
        ),
        td: ({ children }) => (
          <td style={{ color: '#0f172a', padding: '8px 10px', border: '1px solid #cbd5e1', fontSize: '0.85rem', verticalAlign: 'top', whiteSpace: 'normal', wordBreak: 'break-word' }}>{children}</td>
        ),
        strong: ({ children }) => <strong>{children}</strong>,
        p: ({ children, ...props }) => {
          const renderWithColours = (nodes) => {
            if (!Array.isArray(nodes)) nodes = [nodes];
            return nodes.map((node, idx) => {
              if (typeof node === 'string') {
                if (/:\s*Strong\b/i.test(node)) {
                  const parts = node.split(/(Strong)/i);
                  return parts.map((part, i) =>
                    /^Strong$/i.test(part) 
                      ? <span key={`${idx}-${i}`} className="font-bold text-red-600">{part}</span> 
                      : <span key={`${idx}-${i}`}>{part}</span>
                  );
                }
                if (/:\s*Moderate\b/i.test(node)) {
                  const parts = node.split(/(Moderate)/i);
                  return parts.map((part, i) =>
                    /^Moderate$/i.test(part) 
                      ? <span key={`${idx}-${i}`} className="font-bold text-blue-600">{part}</span> 
                      : <span key={`${idx}-${i}`}>{part}</span>
                  );
                }
                if (/:\s*Weak\b/i.test(node)) {
                  const parts = node.split(/(Weak)/i);
                  return parts.map((part, i) =>
                    /^Weak$/i.test(part) 
                      ? <span key={`${idx}-${i}`} className="font-bold text-orange-500">{part}</span> 
                      : <span key={`${idx}-${i}`}>{part}</span>
                  );
                }
              }
              return node;
            });
          };
          return <p {...props}>{renderWithColours(children)}</p>;
        },
      }}
    >
      {normaliseMarkdown(text)}
    </ReactMarkdown>
  </div>
);

/* Lazy-loaded section wrapper — only renders markdown when scrolled into view.
   Prevents the browser from choking on 100K+ char reports (Extensive Log). */
const LazySection = ({ section, idx, theme, isFirst, forceRender }) => {
  const ref = useRef(null);
  const [visible, setVisible] = useState(isFirst || forceRender);
  
  useEffect(() => {
    if (forceRender) setVisible(true);
  }, [forceRender]);
  
  useEffect(() => {
    if (visible || !ref.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: '400px' }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [visible]);

  return (
    <article key={section.id} id={section.id} className="scroll-mt-24" ref={ref}>
      <div className={`border-l-4 ${theme.sectionBorder} pl-4 mb-4`}>
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full ${theme.sectionNumberBg} text-xs font-bold`}>
            {idx + 1}
          </span>
          <h3
            className={`text-lg sm:text-xl font-bold ${theme.accentText} tracking-tight`}
            style={{ fontFamily: "'Times New Roman', Times, serif" }}
            data-testid={`report-section-heading-${idx + 1}`}
          >
            {section.title}
          </h3>
        </div>
      </div>
      <div className="bg-white rounded-lg border border-slate-200 p-6 sm:p-7 shadow-sm" data-testid={`report-section-content-${idx + 1}`}>
        {visible ? (
          <MarkdownBlock text={section.content} testId={`report-section-md-${idx + 1}`} />
        ) : (
          <div className="h-32 flex items-center justify-center text-slate-400">
            <Loader2 className="w-5 h-5 animate-spin mr-2" /> Loading section...
          </div>
        )}
      </div>
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        className="mt-2 inline-flex items-center gap-1 text-xs text-slate-700 hover:text-slate-900"
        data-testid={`report-back-to-top-${idx + 1}`}
      >
        <ChevronRight className="w-3 h-3 rotate-[-90deg]" /> Back to top
      </button>
    </article>
  );
};

/* Colour configs per report type — matches landing page design */
const REPORT_THEME = {
  quick_summary: {
    label: "Quick Summary Report",
    headerBg: "bg-emerald-600",
    previewColor: "#059669",
    accentBg: "bg-emerald-600",
    accentText: "text-emerald-800",
    priceBadge: "bg-emerald-500",
    price: "FREE",
    borderColor: "border-emerald-300",
    lightBg: "from-emerald-50 via-white to-lime-50",
    sectionBorder: "border-emerald-500",
    tocBg: "bg-emerald-50/80",
    tocBorder: "border-emerald-200",
    sectionNumberBg: "bg-emerald-200 text-emerald-900",
  },
  full_detailed: {
    label: "Full Detailed Report",
    headerBg: "bg-blue-700",
    previewColor: "#1d4ed8",
    accentBg: "bg-blue-600",
    accentText: "text-blue-900",
    priceBadge: "bg-blue-500",
    price: "$150 AUD",
    borderColor: "border-blue-300",
    lightBg: "from-blue-50 via-white to-cyan-50",
    sectionBorder: "border-blue-500",
    tocBg: "bg-blue-50/80",
    tocBorder: "border-blue-200",
    sectionNumberBg: "bg-blue-200 text-blue-900",
  },
  extensive_log: {
    label: "Extensive Log Report",
    headerBg: "bg-purple-700",
    previewColor: "#7e22ce",
    accentBg: "bg-purple-600",
    accentText: "text-purple-900",
    priceBadge: "bg-purple-600",
    price: "$200 AUD",
    borderColor: "border-purple-300",
    lightBg: "from-purple-50 via-white to-fuchsia-50",
    sectionBorder: "border-purple-600",
    tocBg: "bg-purple-50/90",
    tocBorder: "border-purple-200",
    sectionNumberBg: "bg-purple-200 text-purple-900",
  },
};

const ReportView = () => {
  const { caseId, reportId } = useParams();
  const navigate = useNavigate();
  const requestRef = useRef(0);
  const [report, setReport] = useState(null);
  const [caseData, setCaseData] = useState(null);
  const [grounds, setGrounds] = useState([]);
  const [sourceReports, setSourceReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hasAllReports, setHasAllReports] = useState(false);
  const [forceRenderAll, setForceRenderAll] = useState(false);

  useEffect(() => {
    const requestId = requestRef.current + 1;
    requestRef.current = requestId;
    setLoading(true);
    setReport(null);
    setCaseData(null);
    setGrounds([]);
    setSourceReports([]);
    setHasAllReports(false);
    fetchData(requestId);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId, reportId]);

  const fetchData = async (requestId = requestRef.current) => {
    try {
      const [reportRes, caseRes, groundsRes, reportsRes] = await Promise.all([
        axios.get(`${API}/cases/${caseId}/reports/${reportId}`),
        axios.get(`${API}/cases/${caseId}`),
        axios.get(`${API}/cases/${caseId}/grounds`),
        axios.get(`${API}/cases/${caseId}/reports`),
      ]);
      if (requestId !== requestRef.current) return;
      setReport(reportRes.data);
      setCaseData(caseRes.data);
      setGrounds(groundsRes.data?.grounds || []);
      setSourceReports(reportsRes.data || []);
      const requiredTypes = ["quick_summary", "full_detailed", "extensive_log"];
      const hasAll = requiredTypes.every((type) =>
        (reportsRes.data || []).some((item) =>
          item.report_type === type &&
          item.status === "completed" &&
          !item.content?.aggressive_mode
        )
      );
      setHasAllReports(hasAll);
    } catch (error) {
      if (requestId !== requestRef.current) return;
      toast.error("Failed to load report");
      navigate(`/cases/${caseId}?tab=reports`);
    } finally {
      if (requestId !== requestRef.current) return;
      setLoading(false);
    }
  };

  const handlePrint = () => {
    openReportPreview("print");
  };

  const handleBackToCase = () => {
    window.location.assign(`/cases/${caseId}?tab=reports`);
  };

  const iosShareOrDownload = async (blob, filename, mimeType) => {
    const isIOS = isIOSDevice();
    if (isIOS && navigator.share) {
      try {
        const file = new File([blob], filename, { type: mimeType });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({ title: filename, files: [file] });
          toast.success("Shared successfully!");
          return;
        }
      } catch (shareErr) {
        if (shareErr.name === 'AbortError') return;
        console.warn("Share API failed, using download fallback");
      }
    }
    if (isIOS) {
      const url = window.URL.createObjectURL(blob);
      window.location.href = url;
      toast.success("File opened — use the Share button to save.");
      setTimeout(() => window.URL.revokeObjectURL(url), 30000);
    } else {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Downloaded successfully!");
      setTimeout(() => window.URL.revokeObjectURL(url), 10000);
    }
  };

  const buildAuthUrl = async (baseUrl) => {
    const { buildSecureDownloadUrl } = await import("../utils/downloadToken");
    return buildSecureDownloadUrl(baseUrl);
  };

  const openReportPreview = (mode = "print") => {
    // Force all lazy sections to render before building print HTML
    setForceRenderAll(true);
    setTimeout(() => {
      _buildAndOpenPreview(mode);
    }, 500);
  };

  const _buildAndOpenPreview = (mode) => {
    const contentEl = document.querySelector('[data-testid="report-content"]');
    if (!contentEl) {
      toast.error("Unable to open report preview.");
      return;
    }
    const title = report?.title || `${caseData?.title || "Case"} Report`;
    const meta = `${caseData?.court || "Court"} — ${(caseData?.state || "NSW").toUpperCase()}`;
    const notice = mode === "pdf"
      ? '<div class="notice">PDF preview — use Print / Save as PDF to download.</div>'
      : '';
    const previewDate = new Date(report?.generated_at || Date.now()).toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" });
    const appellantForFooter = defendantName || caseData?.defendant_name || caseData?.title || "Appellant";
    // Footer spec locked by owner 21/4/2026:
    //   LEFT  = {Appellant}  ·  {Document Type}  ·  {Date in en-AU long form}
    //   RIGHT = Page X of Y
    const previewFooterLabel = `${appellantForFooter}  \\00B7  ${title}  \\00B7  ${previewDate}`;

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    @page {
      size: A4 portrait;
      margin: 18mm 20mm 22mm 20mm;
      @bottom-left {
        content: "${previewFooterLabel}";
        font-family: 'Times New Roman', Times, serif;
        font-size: 9pt; font-style: italic; color: #334155;
      }
      @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-family: 'Times New Roman', Times, serif;
        font-size: 9pt; font-style: italic; color: #334155;
      }
    }
    @page landscape-table {
      size: A4 landscape;
      margin: 14mm 18mm 20mm 18mm;
      @bottom-left {
        content: "${previewFooterLabel}";
        font-family: 'Times New Roman', Times, serif;
        font-size: 9pt; font-style: italic; color: #334155;
      }
      @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-family: 'Times New Roman', Times, serif;
        font-size: 9pt; font-style: italic; color: #334155;
      }
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Times New Roman', Times, serif; padding: 0; color: #0f172a; line-height: 1.5; font-size: 11pt; background: #fff; }
    th { background: #1d4ed8 !important; color: #fff !important; font-weight: 700 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .report-container { max-width: 900px; margin: 0 auto; }
    .cover-page { padding: 20px 0 10px; }
    .cover-page-inner { border: 2px solid #cbd5e1; border-radius: 14px; padding: 20px 18px; text-align: center; background: #fff; }
    .cover-page-kicker { margin: 0 0 4px; text-transform: uppercase; letter-spacing: 0.18em; font-size: 8pt; font-weight: 800; color: #1d4ed8; }
    .cover-page h1 { margin: 0 0 6px; font-family: 'Times New Roman', Times, serif; font-size: 14pt; color: #0f172a; font-weight: 700; line-height: 1.3; }
    .cover-page p { margin: 0 0 4px; color: #334155; font-size: 11pt; }
    .cover-page-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin: 14px 0 12px; text-align: left; }
    .cover-page-card { border: 1px solid #cbd5e1; border-radius: 10px; padding: 8px 10px; background: #f8fafc; }
    .cover-page-card-label { font-size: 8pt; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 2px; }
    .cover-page-card-value { font-size: 10pt; font-weight: 700; color: #0f172a; }
    .cover-page-note { margin-top: 8px; border: 2px solid #b91c1c; border-radius: 10px; padding: 8px 10px; font-size: 8pt; font-weight: 700; color: #ffffff; background: #dc2626; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .page-break { page-break-after: always; break-after: page; }
    .report-header { background: ${theme.previewColor}; color: #fff !important; padding: 18px 24px; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; page-break-inside: avoid; break-inside: avoid; }
    .report-header, .report-header * { color: #fff !important; }
    .report-header h1 { font-family: 'Times New Roman', Times, serif; font-size: 14pt; font-weight: 700; margin-bottom: 3px; color: #fff !important; line-height: 1.3; }
    .report-header .meta-line { font-size: 11pt; color: rgba(255,255,255,0.9); margin-top: 2px; }
    .report-header .grounds-count { font-size: 18pt; font-weight: 700; color: #fff; text-align: right; }
    .report-header .grounds-label { font-size: 8pt; color: rgba(255,255,255,0.8); text-align: right; }
    .report-header .header-row { display: flex; justify-content: space-between; align-items: flex-start; }
    .report-header .badge { display: inline-block; background: rgba(255,255,255,0.25); padding: 2px 10px; border-radius: 999px; font-size: 9pt; font-weight: 700; margin-top: 4px; }
    .report-header .gen-date { font-size: 8pt; color: rgba(255,255,255,0.85); margin-top: 3px; }
    /* 5-cell grid on auto-fit so no empty placeholder cell on row 2 when the
       grid would otherwise leave a blank slot (was: repeat(3, 1fr) → 2-empty). */
    .report-header .case-info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 6px 12px; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2); background: inherit; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .report-header .case-info-grid .ci-label { font-size: 8pt; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(255,255,255,0.7); margin-bottom: 1px; }
    .report-header .case-info-grid .ci-value { font-size: 10pt; font-weight: 700; color: #fff; font-family: 'Times New Roman', Times, serif; }
    .toc { padding: 10px 24px; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
    .toc-title { font-size: 9pt; text-transform: uppercase; letter-spacing: 0.05em; color: #475569; font-weight: 700; margin-bottom: 4px; }
    .toc-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 2px 14px; }
    .toc-grid a { font-size: 8pt; color: #334155; text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
    .toc-grid a:hover { color: #1d4ed8; }

    /* ── Tailwind utilities for captured DOM content ── */
    .flex { display: flex; }
    .items-center { align-items: center; }
    .gap-2 { gap: 8px; }
    .gap-3 { gap: 12px; }
    .mb-2 { margin-bottom: 8px; }
    .mb-4 { margin-bottom: 16px; }
    .mt-2 { margin-top: 8px; }
    .mt-3 { margin-top: 12px; }
    .p-2 { padding: 8px; }
    .p-4 { padding: 16px; }
    .border { border: 1px solid #e2e8f0; }
    .border-slate-200 { border-color: #e2e8f0; }
    .rounded { border-radius: 4px; }
    .rounded-lg { border-radius: 8px; }
    .font-medium { font-weight: 500; }
    .font-semibold { font-weight: 600; }
    .font-bold { font-weight: 700; }
    .text-xs { font-size: 11px; }
    .text-sm { font-size: 13px; }
    .text-slate-500 { color: #64748b; }
    .text-slate-600 { color: #475569; }
    .text-slate-700 { color: #334155; }
    .text-slate-900 { color: #0f172a; }
    .text-white { color: #ffffff; }
    .uppercase { text-transform: uppercase; }
    .whitespace-pre-wrap { white-space: pre-wrap; }
    .flex-wrap { flex-wrap: wrap; }
    .underline { text-decoration: underline; }
    .break-words { overflow-wrap: break-word; }
    .inline-flex { display: inline-flex; }
    .sections { padding: 16px 24px; }
    .section { margin-bottom: 14px; }
    .section-header { display: flex; align-items: center; gap: 8px; border-left: 3px solid ${theme.previewColor}; padding-left: 10px; margin-bottom: 6px; }
    .section-number { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; background: #e2e8f0; color: #0f172a; font-size: 10pt; font-weight: 700; flex-shrink: 0; }
    .section-title { font-family: 'Times New Roman', Times, serif; font-size: 12pt; font-weight: 700; color: #0f172a; text-transform: uppercase; }
    .section-body { background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; font-size: 11pt; line-height: 1.5; }
    .section-body h1, .section-body h2, .section-body h3, .section-body h4 { font-family: 'Times New Roman', Times, serif; font-weight: 700; color: #0f172a; }
    .section-body h2 { font-size: 12pt; border-bottom: 1.5pt solid #1e3a8a; padding-bottom: 3px; margin: 12pt 0 6pt; page-break-after: avoid; break-after: avoid; }
    /* Subheading break rules removed 2026-04-21. Previously page-break-after:
       avoid was forcing multi-paragraph subsections to the next page,
       producing the giant whitespace gaps the owner reported. Browser
       default orphan/widow handling + the per-paragraph rules below keep
       readability without half-blank pages. */
    .section-body h3 { font-size: 12pt; font-style: italic; color: #1e3a8a; margin: 10pt 0 4pt; }
    .section-body h4 { font-size: 11pt; color: #334155; margin: 8pt 0 3pt; }
    .section-body p { margin: 0 0 10pt 0; font-size: 11pt; line-height: 1.5; orphans: 3; widows: 3; }
    .section-body strong { color: #0f172a; font-weight: 700; }
    .section-body ul, .section-body ol { padding-left: 1.6rem; margin: 4pt 0 10pt; }
    .section-body li { margin-bottom: 3pt; font-size: 11pt; line-height: 1.5; }
    .section-body a { color: #1d4ed8; text-decoration: underline; }
    .section-body .legal-report-table-wrap { overflow-x: auto; }
    .section-body table {
      /* Landscape page for tables — but NO forced break-before/after because
         that pushes the table to a fresh page and leaves huge whitespace
         before it on the preceding portrait page. Let the browser break
         naturally based on table height. */
      page: landscape-table;
      width: 100%; border-collapse: collapse; margin: 8pt 0;
      font-size: 10pt !important; table-layout: fixed;
      page-break-inside: auto; break-inside: auto;
    }
    .section-body th { background: #1d4ed8; color: #fff !important; font-weight: 700; padding: 5px 7px; text-align: left; border: 1px solid #cbd5e1; font-size: 9.5pt !important; word-wrap: break-word; overflow-wrap: break-word; }
    .section-body td { border: 1px solid #cbd5e1; padding: 5px 7px; color: #0f172a !important; vertical-align: top; word-break: break-word; overflow-wrap: anywhere; hyphens: auto; font-size: 10pt !important; }
    .section-body blockquote { border-left: 3px solid #1e3a8a; padding: 6px 10px; margin: 6px 0; background: #eff6ff; color: #1e3a8a; font-size: 10pt; }
    /* Fallback styling for pipe-delimited <pre> tables — keep readable (not black). */
    .section-body pre, .report-container pre {
      background: #f8fafc !important; color: #1e293b !important;
      font-family: 'Courier New', monospace; font-size: 8pt;
      padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 4px;
      white-space: pre-wrap; word-wrap: break-word; overflow-wrap: anywhere;
      break-inside: avoid; page-break-inside: avoid; margin: 6px 0;
    }
    .disclaimer { padding: 10px 24px; border-top: 1px solid #e2e8f0; display: flex; gap: 8px; align-items: flex-start; }
    .disclaimer-icon { color: #ef4444; font-size: 16px; flex-shrink: 0; }
    .disclaimer-text { font-size: 8pt; color: #334155; }
    .disclaimer-text strong { font-size: 8pt; text-transform: uppercase; letter-spacing: 0.05em; color: #1e293b; display: block; margin-bottom: 1px; }
    .disclaimer-bold { background: #dc2626; border: 2px solid #b91c1c; padding: 10px 16px; margin: 10px 24px; border-radius: 6px; display: flex; gap: 10px; align-items: flex-start; page-break-inside: avoid; break-inside: avoid; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .disclaimer-bold .disc-icon { color: #facc15; font-size: 22px; flex-shrink: 0; }
    .disclaimer-bold .disc-text { font-size: 8pt; color: #ffffff; font-weight: 700; }
    .disclaimer-bold .disc-text strong { font-size: 10pt; text-transform: uppercase; letter-spacing: 0.08em; color: #ffffff; display: block; margin-bottom: 3px; }
    .notice { background: #eff6ff; border: 1px solid #93c5fd; padding: 6px 12px; border-radius: 6px; color: #1e3a8a; margin: 10px 24px; font-size: 10pt; }
    .print-footer { display: none; position: fixed; left: 0; right: 0; bottom: 0; background: #fff; border-top: 1px solid #1d4ed8; padding: 3px 18mm 4px; }
    .print-footer-row { display: flex; justify-content: space-between; align-items: center; font-family: 'Times New Roman', Times, serif; font-size: 7pt; font-style: italic; color: #475569; }
    .print-footer-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .print-footer-page::after { content: ''; }
    .no-print { display: none !important; }
    @media print {
      * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
      body { print-color-adjust: exact; -webkit-print-color-adjust: exact; padding-bottom: 40px; }
      .report-container { max-width: none; }
      .cover-page { page-break-after: always; break-after: page; }
      .report-header { print-color-adjust: exact; -webkit-print-color-adjust: exact; page-break-inside: avoid; break-inside: avoid; }
      .report-header .case-info-grid { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; background: inherit; }
      .section-number { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .section-body th { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .disclaimer-bold { page-break-inside: avoid; break-inside: avoid; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .report-branding { page-break-inside: avoid; break-inside: avoid; }
      .disclaimer-bold + .report-branding { page-break-before: avoid; break-before: avoid; }
      .section-body .legal-report-table-wrap { overflow: visible; }
      .section-body table { min-width: 0 !important; width: 100% !important; table-layout: fixed !important; }
      .print-footer { display: block; }
      .print-footer-page::after { content: "Page " counter(page) " of " counter(pages); }
    }
    @media (max-width: 768px) {
      .cover-page-grid { grid-template-columns: 1fr; }
      body { font-size: 13px; padding: 0 0 60px; }
      .report-container { max-width: 100%; }
      .cover-page-inner { padding: 18px 16px; }
      .cover-page h1 { font-size: 22px; }
      .cover-page-card-value { font-size: 12px; }
      .cover-page-note { font-size: 10px; padding: 10px 12px; }
      .report-header { padding: 18px 16px; }
      .report-header h1 { font-size: 20px; }
      .report-header .case-info-grid { grid-template-columns: 1fr 1fr; gap: 6px; }
      .report-header .case-info-grid .ci-value { font-size: 11px; }
      .toc { padding: 10px 16px; }
      .toc-grid { grid-template-columns: repeat(2, 1fr); gap: 2px 12px; }
      .sections { padding: 16px; }
      .section-title { font-size: 16px; }
      .section-body { padding: 14px 16px; }
      .section-body h2 { font-size: 1.1rem; }
      .section-body h3 { font-size: 1rem; }
      .section-body table { font-size: 9pt !important; }
      .section-body th, .section-body td { padding: 5px 6px; font-size: 9pt !important; }
      .disclaimer-bold { margin: 12px 16px; padding: 14px 16px; }
      .disclaimer-bold .disc-text { font-size: 11px; }
      .disclaimer-bold .disc-text strong { font-size: 12px; }
      .notice { margin: 10px 16px; font-size: 11px; }
      .print-footer { padding: 6px 12px; }
      .print-footer-row { font-size: 8px; }
    }
  </style>
</head>
<body>
    ${notice}
    <section class="cover-page page-break">
      <div class="cover-page-inner">
        <p class="cover-page-kicker">Appeal Case Manager</p>
        <h1>${title}</h1>
        <p>${caseData?.title || "Case"}</p>
        <div class="cover-page-grid">
          <div class="cover-page-card"><div class="cover-page-card-label">Defendant</div><div class="cover-page-card-value">${defendantName}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Court / State</div><div class="cover-page-card-value">${meta}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Offence</div><div class="cover-page-card-value">${offenceDisplay}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Sentence</div><div class="cover-page-card-value">${sentenceSummary}</div></div>
        </div>
        <div class="cover-page-note">NOT LEGAL ADVICE — This application is an educational research tool only and does NOT constitute legal advice. The creator is not a lawyer. All analysis and recommendations must be independently verified by a qualified Australian legal professional. Australian law only. No solicitor-client relationship is created. No document, report, or output generated by this Application should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body.</div>
      </div>
    </section>
  <div class="report-container">
    <div class="report-header">
      <div class="header-row">
        <div>
          <div style="font-size:12px;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:4px;">${theme.label}</div>
          <h1>${title}</h1>
          <div class="meta-line">${meta}</div>
          <div class="badge">${theme.price}</div>
          <div class="gen-date">Generated: ${formatDate(report?.generated_at)}</div>
        </div>
        <div>
          <div class="grounds-count">${grounds.length}</div>
          <div class="grounds-label">Ground${grounds.length !== 1 ? 's' : ''} Identified</div>
        </div>
      </div>
      <div class="case-info-grid">
        <div><div class="ci-label">Defendant</div><div class="ci-value">${defendantName}</div></div>
        <div><div class="ci-label">Offence</div><div class="ci-value">${offenceDisplay}</div></div>
        <div><div class="ci-label">Sentence</div><div class="ci-value">${sentenceSummary}</div></div>
        <div><div class="ci-label">Documents</div><div class="ci-value">${documentsCount} files analysed</div></div>
        <div><div class="ci-label">Timeline Events</div><div class="ci-value">${eventsCount} events</div></div>
      </div>
    </div>
    ${sections.length > 1 ? `<div class="toc-container" style="padding:14px 32px;"><p class="toc-heading" style="font-size:11pt;text-transform:uppercase;letter-spacing:0.05em;color:#334155;font-weight:700;margin:0 0 8px;font-family:'Times New Roman',Times,serif;">CONTENTS (${sections.length} SECTIONS)</p><div class="toc-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:4px 20px;">${sections.map((s, i) => `<div class="toc-item" style="font-size:9pt;color:#334155;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:2px 0;font-weight:500;font-family:'Times New Roman',Times,serif;"><strong>${i+1}.</strong> ${s.title}</div>`).join('')}</div></div>` : ''}
    <div class="sections">
      ${sections.map((section, idx) => `
        <div class="section" id="print-section-${idx+1}">
          <div class="section-header">
            <span class="section-number">${idx+1}</span>
            <span class="section-title">${section.title}</span>
          </div>
          <div class="section-body">${(document.getElementById(section.id)?.querySelector('[data-testid^="report-section-content-"]')?.innerHTML || '').replace(/<th(?=[\s>])([^>]*?)style="[^"]*"/gi, '<th$1').replace(/<th(?=[\s>])/gi, '<th style="background:#1d4ed8;color:#ffffff;font-weight:800;"')}</div>
        </div>
      `).join('')}
    </div>
    <div class="disclaimer-bold">
      <div class="disc-icon">&#9888;</div>
      <div class="disc-text">
        <strong>NOT LEGAL ADVICE</strong>
        This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service. No document, report, or output generated by this Application should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body.
      </div>
    </div>
    <div style="text-align:center;margin:16px 32px;padding:12px 0;page-break-inside:avoid;" class="report-branding">
      <p style="font-size:10px;font-weight:700;color:#334155;margin:0 0 8px;">Created and Designed by Deb King</p>
      <div style="display:inline-flex;align-items:center;gap:8px;">
        <div style="width:28px;height:28px;background:#dc2626;border-radius:5px;display:flex;align-items:center;justify-content:center;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
        </div>
        <div style="text-align:left;">
          <p style="margin:0;font-weight:700;font-size:11px;color:#0f172a;">Appeal Case Manager</p>
          <p style="margin:0;font-size:9px;color:#64748b;">Founded by Debra King</p>
          <p style="margin:0;font-size:9px;color:#64748b;">Criminal Appeal Research Tool &mdash; Australian Law Only</p>
        </div>
      </div>
    </div>
  </div>
  <!-- Page-level footer handled by @page @bottom-left / @bottom-right -->
</body>
</html>`;

    localStorage.setItem(
      "document-preview-payload",
      JSON.stringify({
        html,
        mode,
        title,
        source: "report",
        returnTo: `/cases/${caseId}/reports/${reportId}`,
        createdAt: Date.now(),
      })
    );

    const previewUrl = `${window.location.origin}/document-preview?mode=${mode}`;
    window.location.assign(previewUrl);

    toast.success(mode === "print" ? "Preview opened — use Print." : "PDF preview opened.");
  };

  const handleExportPDF = async () => {
    openReportPreview("pdf");
  };

  const handleExportDOCX = async () => {
    // Use document-preview route for iOS compatibility (blob URLs fail on Safari)
    openReportPreview("word");
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
  };

  const rawAnalysis = report?.content?.analysis || "";
  const analysisText = sanitiseReportOutput(rawAnalysis);
  const sections = useMemo(() => parseAnalysisSections(analysisText), [analysisText]);
  const documentsCount = report?.content?.document_count || 0;
  const eventsCount = report?.content?.event_count || 0;
  const sentenceSummary = extractSentenceFromSourceReports(sourceReports, caseData, analysisText);
  const defendantName = caseData?.defendant_name || report?.content?.defendant || extractDefendantFromAnalysis(analysisText);
  const extractedOffence = extractOffenceFromAnalysis(analysisText);
  const rawOffence = caseData?.offence_type || extractedOffence || titleFromSnake(caseData?.offence_category) || "";
  const cleanedOffence = rawOffence.replace(/^the\s+/i, "").trim();
  const offenceDisplay = cleanedOffence.charAt(0).toUpperCase() + cleanedOffence.slice(1);
  const theme = REPORT_THEME[report?.report_type] || REPORT_THEME.quick_summary;

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50" data-testid="report-view-loading">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-slate-400 mx-auto" />
          <p className="mt-4 text-slate-700">Loading report...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="report-page min-h-screen bg-white">
      {/* Sticky action bar */}
      <header className="bg-white/95 backdrop-blur border-b border-slate-200 sticky top-0 z-40 no-print" data-testid="report-header">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between gap-3 flex-wrap text-slate-900">
            <Button size="sm" onClick={handleBackToCase} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="back-btn">
              <ArrowLeft className="w-4 h-4 mr-1" /> Back to Reports
            </Button>
            <div className="flex items-center gap-2 flex-wrap">
              <Button size="sm" onClick={handlePrint} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="print-btn">
                <Printer className="w-4 h-4 mr-2" /> Print
              </Button>
              <Button size="sm" onClick={handleExportDOCX} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="export-docx-btn">
                <FileText className="w-4 h-4 mr-2" /> Export Word
              </Button>
              <Button size="sm" onClick={handleExportPDF} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="export-pdf-btn">
                <Download className="w-4 h-4 mr-2" /> Export PDF
              </Button>
              <ReportTranslator caseId={caseId} reportId={reportId} />
            </div>
          </div>
        </div>
        {/* Quick Navigate between reports */}
        {sourceReports.length > 0 && (
          <div className="max-w-5xl mx-auto px-4 sm:px-6 py-1.5 border-t border-slate-100">
            <div className="flex items-center gap-2 flex-wrap text-xs" data-testid="report-quick-nav">
              <span className="text-slate-400 font-medium uppercase tracking-wider mr-1">Jump to:</span>
              {sourceReports
                .filter(r => r.status === "completed" && !r.content?.aggressive_mode)
                .sort((a, b) => {
                  const order = ["quick_summary", "full_detailed", "extensive_log", "barrister_view"];
                  return order.indexOf(a.report_type) - order.indexOf(b.report_type);
                })
                .map(r => {
                  const labels = { quick_summary: "Quick Summary", full_detailed: "Full Detailed", extensive_log: "Extensive Log", barrister_view: "Appellate Research Brief" };
                  const isCurrent = r.report_id === reportId;
                  const href = r.report_type === "barrister_view"
                    ? `/cases/${caseId}/reports/${r.report_id}/barrister`
                    : `/cases/${caseId}/reports/${r.report_id}`;
                  return (
                    <button
                      key={r.report_id}
                      onClick={() => { if (!isCurrent) window.location.assign(href); }}
                      disabled={isCurrent}
                      className={`px-2.5 py-1 rounded-md font-medium transition-colors ${isCurrent ? 'bg-blue-700 text-white cursor-default' : 'bg-slate-100 text-slate-600 hover:bg-blue-100 hover:text-blue-700'}`}
                      data-testid={`quick-nav-${r.report_type}`}
                    >
                      {labels[r.report_type] || r.report_type}
                    </button>
                  );
                })}
            </div>
          </div>
        )}
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <div className={`bg-white rounded-xl border ${theme.borderColor} overflow-hidden shadow-xl`} data-testid="report-content">

          {/* ===== COLOUR-CODED REPORT HEADER (matches landing page) ===== */}
          <div className={`${theme.headerBg} text-white p-6 sm:p-8`} data-testid="report-colour-header">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
              <div>
                <p className="text-sm uppercase tracking-wider font-semibold text-white mb-1">{theme.label}</p>
                <h1 className="text-xl sm:text-2xl font-bold text-white" style={{ fontFamily: "'Times New Roman', Times, serif" }} data-testid="report-title">
                  {report?.title || `${caseData?.title || "Case"} Report`}
                </h1>
                <p className="text-sm text-white/90 mt-1 font-medium">{caseData?.court || "Court"} — {(caseData?.state || "NSW").toUpperCase()}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-white">{grounds.length} Ground{grounds.length !== 1 ? "s" : ""}</p>
                <p className="text-xs text-white/80 font-semibold">Identified</p>
              </div>
            </div>
            <div className="flex items-center gap-3 flex-wrap text-sm text-white/90 mb-5">
              <span className={`${theme.priceBadge} px-3 py-1 rounded-full text-sm font-bold text-white`}>{theme.price}</span>
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Generated: {formatDate(report?.generated_at)}</span>
            </div>

            {/* Case Overview Grid — INSIDE the coloured box */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 border-t border-white/20 pt-4" data-testid="report-top-summary-box">
              <div>
                <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Defendant</p>
                <p className="text-sm sm:text-base font-bold text-white" data-testid="report-summary-accused">{defendantName}</p>
              </div>
              <div>
                <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Offence</p>
                <p className="text-sm sm:text-base font-bold text-white" data-testid="report-summary-offence">{offenceDisplay}</p>
              </div>
              <div className="col-span-2 sm:col-span-1">
                <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Sentence</p>
                <p className="text-sm sm:text-base font-bold text-white" data-testid="report-summary-sentence">{sentenceSummary}</p>
              </div>
              <div>
                <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Documents</p>
                <p className="text-sm sm:text-base font-bold text-white">{documentsCount} files analysed</p>
              </div>
              <div>
                <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Timeline Events</p>
                <p className="font-bold text-white">{eventsCount} events</p>
              </div>
            </div>
          </div>

          {/* ===== TABLE OF CONTENTS BAR (matches landing page grey bar) ===== */}
          {sections.length > 1 && (
            <div className={`${theme.tocBg} border-b ${theme.tocBorder} p-4 sm:p-5`} data-testid="report-table-of-contents">
              <div className="flex items-center gap-2 mb-2">
                <ListOrdered className="w-4 h-4 text-slate-700" />
                <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Contents ({sections.length} Sections)
                </p>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-1.5">
                {sections.map((section, idx) => (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className="text-left text-xs text-slate-700 hover:text-blue-700 transition-colors truncate"
                    data-testid={`report-toc-item-${idx + 1}`}
                  >
                    <span className="font-semibold text-slate-900">{idx + 1}.</span> {section.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ===== REPORT SECTIONS ===== */}
          <div className="p-5 sm:p-6 md:p-8 space-y-6" data-testid="report-full-analysis-section">
            {sections.map((section, idx) => (
              <LazySection
                key={section.id}
                section={section}
                idx={idx}
                theme={theme}
                isFirst={idx < 3}
                forceRender={forceRenderAll}
              />
            ))}
          </div>

          {/* AI-analysis warning + metadata */}
          <div className="px-6 sm:px-8 py-4 bg-slate-50 border-t border-slate-200" data-testid="report-ai-footer">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <VerificationBadge status={report?.verification_status || "generated"} />
            </div>

            <p className="text-xs text-slate-400 leading-relaxed mt-2">
              This report is AI-assisted analysis for case preparation and legal review. It is not a determination of legal merit or appeal outcome.
            </p>
            <ReportMetadataPanel
              metadata={report?.metadata || report?.content?.metadata}
              verificationStatus={report?.verification_status}
            />
          </div>

          {/* ===== DISCLAIMER FOOTER ===== */}
          <div className="bg-red-700 px-4 py-3" data-testid="report-footer">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-300 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-white uppercase tracking-wide mb-0.5">NOT LEGAL ADVICE</p>
                <p className="text-[10px] text-white/90 leading-snug">This application is an educational research tool only and does NOT constitute legal advice. The creator is not a lawyer. All analysis must be independently verified by a qualified Australian legal professional. Australian law only. No solicitor-client relationship is created. No document, report, or output should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body.</p>
              </div>
            </div>
          </div>
          {/* ===== BRANDING FOOTER ===== */}
          <div className="bg-white py-6 text-center" data-testid="report-branding-footer">
            <p className="text-xs font-bold text-slate-600 mb-3">Created and Designed by Deb King</p>
            <div className="flex items-center justify-center gap-2.5">
              <div className="w-9 h-9 bg-red-600 rounded-md flex items-center justify-center flex-shrink-0">
                <Scale className="w-5 h-5 text-white" />
              </div>
              <div className="text-left">
                <p className="font-bold text-slate-900 text-sm leading-tight">Appeal Case Manager</p>
                <p className="text-xs text-slate-500 leading-tight">Founded by Debra King</p>
                <p className="text-xs text-slate-500 leading-tight">Criminal Appeal Research Tool — Australian Law Only</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <style>{`
        .legal-report {
          font-size: 0.95rem;
          line-height: 1.5;
          color: #0f172a;
        }
        .legal-report p { margin: 0 0 0.5rem; }
        .legal-report h1,
        .legal-report h2,
        .legal-report h3,
        .legal-report h4 {
          font-family: 'Times New Roman', Times, serif;
          font-weight: 700;
          color: #1e3a8a;
          margin: 0.75rem 0 0.3rem;
          page-break-after: avoid;
          break-after: avoid;
        }
        .legal-report h2 { font-size: 1.1rem; border-bottom: 1.5px solid #1e3a8a; padding-bottom: 3px; }
        .legal-report h3 { font-size: 1rem; color: #1e40af; font-style: italic; }
        .legal-report h4 { font-size: 0.95rem; color: #334155; }
        .legal-report strong { color: #0f172a; font-weight: 700; }
        .legal-report ul, .legal-report ol { padding-left: 1.3rem; margin: 0.3rem 0 0.5rem; }
        .legal-report li { margin-bottom: 0.15rem; font-size: 0.95rem; line-height: 1.5; }
        .legal-report table {
          width: max-content;
          min-width: 100%;
          border-collapse: collapse;
          margin: 0;
          background: #ffffff;
          table-layout: auto;
        }
        .legal-report th {
          background: #1d4ed8;
          color: #ffffff !important;
          font-weight: 800;
          font-size: 0.8rem;
          white-space: normal;
          word-break: keep-all;
          overflow-wrap: normal;
          hyphens: none;
          vertical-align: top;
        }
        .legal-report th, .legal-report td {
          border: 1px solid #cbd5e1;
          padding: 8px 10px;
          font-size: 0.85rem;
          vertical-align: top;
          white-space: normal;
          word-break: keep-all;
          overflow-wrap: break-word;
          hyphens: none;
        }
        .legal-report th {
          color: #ffffff !important;
        }
        .legal-report td {
          color: #0f172a;
        }
        @media (max-width: 768px) {
          .legal-report {
            font-size: 0.88rem;
            line-height: 1.65;
          }
          .legal-report li {
            font-size: 0.88rem;
          }
          .legal-report table {
            min-width: 560px;
          }
          .legal-report th, .legal-report td {
            padding: 8px 9px;
            font-size: 0.8rem;
          }
        }
        .legal-report blockquote {
          border-left: 4px solid #1e3a8a;
          padding: 12px 14px;
          margin: 0.9rem 0;
          background: #eff6ff;
          color: #1e3a8a;
        }
        @media print {
          body {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }
          .no-print { display: none !important; }
          .legal-report { font-size: 11pt; line-height: 1.4; color: #0f172a; }
          .legal-report p { margin: 0 0 6pt; }
          .legal-report h1,
          .legal-report h2,
          .legal-report h3,
          .legal-report strong { color: #0f172a; }
          .legal-report h2 { font-size: 12pt; margin: 10pt 0 4pt; }
          .legal-report h3 { font-size: 11pt; margin: 8pt 0 3pt; }
          .legal-report h4 { font-size: 11pt; margin: 6pt 0 2pt; }
          .legal-report ul, .legal-report ol { margin: 2pt 0 6pt; }
          .legal-report li { margin-bottom: 1pt; font-size: 11pt; line-height: 1.4; }
          .legal-report table { background: #ffffff; width: 100%; table-layout: fixed; font-size: 9pt; }
          .legal-report th { background: #1d4ed8; color: #ffffff !important; font-size: 9pt; padding: 4pt 5pt; word-break: keep-all; overflow-wrap: break-word; hyphens: none; }
          .legal-report th, .legal-report td { color: #0f172a; border-color: #cbd5e1; padding: 4pt 5pt; word-break: keep-all; overflow-wrap: break-word; hyphens: none; font-size: 9pt; line-height: 1.3; }
          .legal-report blockquote { background: #eff6ff; color: #1e3a8a; border-left: 4px solid #1e3a8a; }
        }
      `}</style>
    </div>
  );
};

export default ReportView;
