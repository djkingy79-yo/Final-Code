/*  — Australian spelling normaliser for ALL user-visible text.
   Converts American English to Australian English.

   CRITICAL iOS SAFARI COMPATIBILITY:
   - NO const/module-level regex with 'g' flag (causes JIT "readonly property" crash)
   - NO .replace() chains (same iOS Safari JIT issue)
   - Uses pure word-by-word string splitting — zero regex in hot paths
   - Entire function wrapped in try-catch as ultimate safety net
*/

// ── Word-level American → Australian spelling map ──
var WORDS = {
  'characterization': 'characterisation', 'mischaracterization': 'mischaracterisation',
  'behavior': 'behaviour', 'behavioral': 'behavioural',
  'favoring': 'favouring', 'analyzing': 'analysing',
  'recognized': 'recognised', 'organized': 'organised', 'organizing': 'organising',
  'defense': 'defence', 'offense': 'offence', 'offenses': 'offences',
  'utilized': 'utilised', 'utilize': 'utilise', 'utilizing': 'utilising',
  'analyze': 'analyse', 'analyzed': 'analysed',
  'organize': 'organise', 'recognize': 'recognise', 'recognizing': 'recognising',
  'honor': 'honour', 'honors': 'honours', 'honorable': 'honourable',
  'favor': 'favour', 'favorable': 'favourable', 'favored': 'favoured',
  'labor': 'labour', 'center': 'centre', 'centered': 'centred',
  'colored': 'coloured', 'counseling': 'counselling', 'counselor': 'counsellor',
  'criminalize': 'criminalise', 'criminalized': 'criminalised',
  'specialize': 'specialise', 'specialized': 'specialised', 'specializing': 'specialising',
  'authorize': 'authorise', 'authorized': 'authorised',
  'emphasize': 'emphasise', 'emphasized': 'emphasised', 'emphasizing': 'emphasising',
  'summarize': 'summarise', 'summarized': 'summarised', 'summarizing': 'summarising',
  'minimize': 'minimise', 'minimized': 'minimised',
  'maximize': 'maximise', 'maximized': 'maximised',
  'normalize': 'normalise', 'normalized': 'normalised',
  'prioritize': 'prioritise', 'prioritized': 'prioritised',
  'apologize': 'apologise', 'apologized': 'apologised',
  'criticize': 'criticise', 'criticized': 'criticised', 'criticizing': 'criticising',
  'jeopardize': 'jeopardise', 'jeopardized': 'jeopardised',
  'legalize': 'legalise', 'legalized': 'legalised',
  'finalize': 'finalise', 'finalized': 'finalised', 'finalizing': 'finalising',
  'generalize': 'generalise', 'generalized': 'generalised',
  'categorize': 'categorise', 'categorized': 'categorised',
  'harmonize': 'harmonise', 'judgment': 'judgement',
  'practicing': 'practising',
  'realize': 'realise', 'realized': 'realised', 'realizing': 'realising',
  'customize': 'customise', 'customized': 'customised',
  'optimize': 'optimise', 'optimized': 'optimised',
  'visualize': 'visualise', 'visualized': 'visualised',
  'penalize': 'penalise', 'penalized': 'penalised', 'penalizing': 'penalising',
  'legitimize': 'legitimise', 'legitimized': 'legitimised',
  'standardize': 'standardise', 'standardized': 'standardised',
  'characterize': 'characterise', 'characterized': 'characterised', 'characterizing': 'characterising',
  'neighbor': 'neighbour', 'neighboring': 'neighbouring',
  'signaling': 'signalling', 'traveling': 'travelling',
  'modeling': 'modelling',
  'traumatize': 'traumatise', 'traumatized': 'traumatised', 'traumatizing': 'traumatising',
  'victimize': 'victimise', 'victimized': 'victimised', 'victimizing': 'victimising',
  'terrorize': 'terrorise', 'terrorized': 'terrorised',
  'scrutinize': 'scrutinise', 'scrutinized': 'scrutinised', 'scrutinizing': 'scrutinising',
  'hypothesize': 'hypothesise', 'hypothesized': 'hypothesised',
  'rationalize': 'rationalise', 'rationalized': 'rationalised',
  'marginalize': 'marginalise', 'marginalized': 'marginalised', 'marginalizing': 'marginalising',
  'weaponize': 'weaponise', 'weaponized': 'weaponised',
  'sympathize': 'sympathise', 'sympathized': 'sympathised',
  'neutralize': 'neutralise', 'neutralized': 'neutralised',
  'mobilize': 'mobilise', 'mobilized': 'mobilised',
  'memorize': 'memorise', 'memorized': 'memorised',
  'pretense': 'pretence', 'dialog': 'dialogue', 'catalog': 'catalogue',
  'canceled': 'cancelled', 'canceling': 'cancelling',
  'labeled': 'labelled', 'labeling': 'labelling',
  'aging': 'ageing', 'fulfill': 'fulfil',
  'maneuver': 'manoeuvre', 'willful': 'wilful', 'skillful': 'skilful',
  'rumor': 'rumour', 'humor': 'humour', 'flavor': 'flavour',
  'fiber': 'fibre', 'theater': 'theatre', 'meter': 'metre',
  'hemorrhage': 'haemorrhage', 'anesthetic': 'anaesthetic', 'pediatric': 'paediatric',
  'license': 'licence'
};

// Simple word-boundary split: split on any non-alphanumeric character while keeping delimiters
function splitWords(str) {
  var result = [];
  var current = '';
  var i = 0;
  while (i < str.length) {
    var ch = str.charAt(i);
    var isWordChar = (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch === '_' || ch === "'";
    if (isWordChar) {
      current += ch;
    } else {
      if (current.length > 0) {
        result.push(current);
        current = '';
      }
      result.push(ch);
    }
    i++;
  }
  if (current.length > 0) {
    result.push(current);
  }
  return result;
}

function replaceWord(word) {
  var lower = word.toLowerCase();
  var replacement = WORDS[lower];
  if (!replacement) return word;
  // Preserve capitalisation of first letter
  if (word.charAt(0) >= 'A' && word.charAt(0) <= 'Z') {
    return replacement.charAt(0).toUpperCase() + replacement.substring(1);
  }
  return replacement;
}

function auSpelling(text) {
  if (!text) return text || '';
  if (typeof text !== 'string') return '';

  try {
    var parts = splitWords(text);
    var out = '';
    var i = 0;
    while (i < parts.length) {
      out = out + replaceWord(parts[i]);
      i++;
    }
    return out;
  } catch (e) {
    // Absolute safety net — return original text unchanged
    return text;
  }
}

export default auSpelling;
