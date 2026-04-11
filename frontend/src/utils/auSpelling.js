/* DO NOT UNDO — Australian spelling normaliser for ALL user-visible text.
   Converts American English to Australian English. Used across all components
   that display AI-generated or dynamic content. */

// ── Word-level American → Australian spelling map ──
// Keys are lowercase American spellings, values are lowercase Australian spellings.
const SPELLING_MAP = {
  'characterization': 'characterisation', 'mischaracterization': 'mischaracterisation',
  'behavior': 'behaviour', 'behavioral': 'behavioural',
  'favoring': 'favouring', 'analyzing': 'analysing',
  'recognized': 'recognised', 'organized': 'organised', 'organizing': 'organising',
  'defense': 'defence', 'offense': 'offence', 'offenses': 'offences',
  'utilized': 'utilised', 'utilize': 'utilise', 'utilizing': 'utilising',
  'analyze': 'analyse', 'analyzed': 'analysed',
  'organize': 'organise', 'recognize': 'recognise', 'recognizing': 'recognising',
  'honor': 'honour', 'honors': 'honours', 'honourable': 'honourable', 'honorable': 'honourable',
  'favor': 'favour', 'favorable': 'favourable', 'favoured': 'favoured', 'favored': 'favoured',
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
  'modeling': 'modelling', 'programing': 'programming',
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
  'aging': 'ageing', 'fulfill': 'fulfil', 'fulfilled': 'fulfilled',
  'maneuver': 'manoeuvre', 'willful': 'wilful', 'skillful': 'skilful',
  'rumor': 'rumour', 'humor': 'humour', 'flavor': 'flavour',
  'fiber': 'fibre', 'theater': 'theatre', 'meter': 'metre',
  'hemorrhage': 'haemorrhage', 'anesthetic': 'anaesthetic', 'pediatric': 'paediatric',
  'licence': 'licence', 'license': 'licence',
};

// Build a single regex from all keys (longest first to avoid partial matches)
const _sortedKeys = Object.keys(SPELLING_MAP).sort((a, b) => b.length - a.length);
const _spellingRegex = new RegExp('\\b(' + _sortedKeys.join('|') + ')\\b', 'gi');

// ── Forensic language prefixes ──
const _PREFIXES = [
  'It is arguable that',
  'It may be contended that',
  'There is a tenable argument that',
  'It is open to argument that',
  'It is submitted that',
  'Grounds may exist to suggest that',
  'It warrants consideration whether',
  'It is respectfully submitted that',
  'A question arises as to whether',
];

const auSpelling = (text) => {
  // Guard: return empty string for non-string/falsy input
  if (!text || typeof text !== 'string') return text || '';

  try {
    // Step 1: Protect URLs, markdown links, code blocks by replacing with placeholders
    var placeholders = [];
    var working = text.replace(/\[[^\]]*\]\([^)]*\)|https?:\/\/[^\s)]+|`[^`]+`/g, function(m) {
      placeholders.push(m);
      return '\x00PH' + (placeholders.length - 1) + '\x00';
    });

    // Step 2: Single-pass dictionary replacement for AU spelling
    working = working.replace(_spellingRegex, function(match) {
      var lower = match.toLowerCase();
      var replacement = SPELLING_MAP[lower];
      if (!replacement) return match;
      // Preserve capitalisation of the first letter
      if (match[0] === match[0].toUpperCase()) {
        return replacement[0].toUpperCase() + replacement.slice(1);
      }
      return replacement;
    });

    // Step 3: Forensic appellate language enforcement
    var forensicIdx = 0;
    function nextPrefix() {
      return _PREFIXES[forensicIdx++ % _PREFIXES.length];
    }

    // Judge possessive patterns
    working = working.replace(/^The (sentencing |trial |appeal )?judge's /gm, function(m, mod) {
      return nextPrefix() + ' the ' + (mod || '') + "judge's ";
    });
    working = working.replace(/\. The (sentencing |trial |appeal )?judge's /g, function(m, mod) {
      return '. ' + nextPrefix() + ' the ' + (mod || '') + "judge's ";
    });

    // Judge action patterns — start of line
    working = working.replace(/^The (sentencing |trial |appeal )?judge (failed to|erred|was wrong|made an error|was biased|misdirected|ignored|disregarded|overlooked|should have|ought to have|did not|neglected to|omitted to)/gm, function(m, mod, verb) {
      return nextPrefix() + ' the ' + (mod || '') + 'judge ' + verb;
    });
    working = working.replace(/^The jury was misdirected/gm, function() {
      return nextPrefix() + ' the jury was misdirected';
    });
    working = working.replace(/^The court (ignored|wrongly|improperly|failed|erred|did not)/gm, function(m, verb) {
      return nextPrefix() + ' the court ' + verb;
    });
    working = working.replace(/^The trial was unfair/gm, function() {
      return nextPrefix() + ' the trial was unfair';
    });
    working = working.replace(/^The verdict (is|was) unreasonable/gm, function(m, v) {
      return nextPrefix() + ' the verdict ' + v + ' unreasonable';
    });
    working = working.replace(/^The sentence (is|was) (inadequate|excessive|manifestly excessive|manifestly inadequate)/gm, function(m, v, adj) {
      return nextPrefix() + ' the sentence ' + v + ' ' + adj;
    });
    working = working.replace(/^The directions were inadequate/gm, function() {
      return nextPrefix() + ' the directions were inadequate';
    });
    working = working.replace(/^The evidence was (wrongly|improperly)/gm, function(m, adv) {
      return nextPrefix() + ' the evidence was ' + adv;
    });
    working = working.replace(/^There was (no proper|a failure to)/gm, function(m, rest) {
      return nextPrefix() + ' there was ' + rest;
    });

    // Judge action patterns — mid-sentence
    working = working.replace(/\. The (sentencing |trial |appeal )?judge (failed to|erred|was wrong|made an error|was biased|misdirected|ignored|disregarded|overlooked|should have|ought to have|did not|neglected to|omitted to)/g, function(m, mod, verb) {
      return '. ' + nextPrefix() + ' the ' + (mod || '') + 'judge ' + verb;
    });
    working = working.replace(/\. The (court|jury) (ignored|wrongly|improperly|was misdirected|failed|erred|did not)/g, function(m, who, verb) {
      return '. ' + nextPrefix() + ' the ' + who + ' ' + verb;
    });

    // Inline blame phrases
    working = working.replace(/\bwas clearly wrong\b/g, 'was arguably wrong');
    working = working.replace(/\bwas plainly wrong\b/g, 'was arguably wrong');
    working = working.replace(/\bwas fundamentally flawed\b/g, 'was arguably fundamentally flawed');
    working = working.replace(/\bno reasonable judge\b/g, 'arguably no reasonable judge');
    working = working.replace(/\bthe (sentencing |trial |appeal )?judge clearly erred\b/gi, function(m, mod) {
      return 'it is contended that the ' + (mod || '') + 'judge erred';
    });

    // Step 4: Restore protected placeholders
    working = working.replace(/\x00PH(\d+)\x00/g, function(m, idx) {
      return placeholders[parseInt(idx, 10)] || m;
    });

    return working;
  } catch (e) {
    // Safety net: if ANY error occurs (iOS Safari JIT, etc.), return original text
    return text;
  }
};

export default auSpelling;
