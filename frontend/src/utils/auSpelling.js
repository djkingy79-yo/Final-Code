/* DO NOT UNDO — Australian spelling normaliser for ALL user-visible text.
   Converts American English to Australian English. Used across all components
   that display AI-generated or dynamic content. */

const auSpelling = (text) => {
  if (!text || typeof text !== 'string') return text || '';

  // Split text into "protected" (URLs, markdown links, code blocks) and "plain" segments.
  // Only apply spelling corrections to plain-text segments.
  // NOTE: Create fresh regex each call to avoid iOS Safari "readonly lastIndex" bug.
  const splitRe = /(\[[^\]]*\]\([^)]*\)|https?:\/\/[^\s)]+|`[^`]+`)/g;
  const parts = text.split(splitRe);

  let corrected = parts.map((part) => {
    // If the part matches a protected pattern, return it untouched
    // Fresh regex per test avoids lastIndex mutation issues on iOS Safari
    if (/(\[[^\]]*\]\([^)]*\)|https?:\/\/[^\s)]+|`[^`]+`)/.test(part)) return part;

    return part
    .replace(/\bcharacterization\b/gi, (m) => m[0] === 'C' ? 'Characterisation' : 'characterisation')
    .replace(/\bMischaracterization\b/g, 'Mischaracterisation')
    .replace(/\bmischaracterization\b/g, 'mischaracterisation')
    .replace(/\bBehavior\b/g, 'Behaviour')
    .replace(/\bbehavior\b/g, 'behaviour')
    .replace(/\bbehavioral\b/gi, (m) => m[0] === 'B' ? 'Behavioural' : 'behavioural')
    .replace(/\bfavoring\b/gi, (m) => m[0] === 'F' ? 'Favouring' : 'favouring')
    .replace(/\banalyzing\b/gi, (m) => m[0] === 'A' ? 'Analysing' : 'analysing')
    .replace(/\brecognized\b/gi, (m) => m[0] === 'R' ? 'Recognised' : 'recognised')
    .replace(/\borganized\b/gi, (m) => m[0] === 'O' ? 'Organised' : 'organised')
    .replace(/\borganizing\b/gi, (m) => m[0] === 'O' ? 'Organising' : 'organising')
    .replace(/\bdefense\b/gi, (m) => m[0] === 'D' ? 'Defence' : 'defence')
    .replace(/\boffense\b/gi, (m) => m[0] === 'O' ? 'Offence' : 'offence')
    .replace(/\boffenses\b/gi, (m) => m[0] === 'O' ? 'Offences' : 'offences')
    .replace(/\butilized\b/gi, (m) => m[0] === 'U' ? 'Utilised' : 'utilised')
    .replace(/\butilize\b/gi, (m) => m[0] === 'U' ? 'Utilise' : 'utilise')
    .replace(/\butilizing\b/gi, (m) => m[0] === 'U' ? 'Utilising' : 'utilising')
    .replace(/\banalyze\b/gi, (m) => m[0] === 'A' ? 'Analyse' : 'analyse')
    .replace(/\banalyzed\b/gi, (m) => m[0] === 'A' ? 'Analysed' : 'analysed')
    .replace(/\borganize\b/gi, (m) => m[0] === 'O' ? 'Organise' : 'organise')
    .replace(/\brecognize\b/gi, (m) => m[0] === 'R' ? 'Recognise' : 'recognise')
    .replace(/\brecognizing\b/gi, (m) => m[0] === 'R' ? 'Recognising' : 'recognising')
    .replace(/\bhonor\b/gi, (m) => m[0] === 'H' ? 'Honour' : 'honour')
    .replace(/\bhonors\b/gi, (m) => m[0] === 'H' ? 'Honours' : 'honours')
    .replace(/\bhonourable\b/gi, (m) => m[0] === 'H' ? 'Honourable' : 'honourable')
    .replace(/\bhonorable\b/gi, (m) => m[0] === 'H' ? 'Honourable' : 'honourable')
    .replace(/\bfavor\b/gi, (m) => m[0] === 'F' ? 'Favour' : 'favour')
    .replace(/\bfavorable\b/gi, (m) => m[0] === 'F' ? 'Favourable' : 'favourable')
    .replace(/\bfavoured\b/gi, (m) => m[0] === 'F' ? 'Favoured' : 'favoured')
    .replace(/\bfavored\b/gi, (m) => m[0] === 'F' ? 'Favoured' : 'favoured')
    .replace(/\blabor\b/gi, (m) => m[0] === 'L' ? 'Labour' : 'labour')
    .replace(/\bcenter\b/gi, (m) => m[0] === 'C' ? 'Centre' : 'centre')
    .replace(/\bcentered\b/gi, (m) => m[0] === 'C' ? 'Centred' : 'centred')
    .replace(/\bcolored\b/gi, (m) => m[0] === 'C' ? 'Coloured' : 'coloured')
    .replace(/\bcounseling\b/gi, (m) => m[0] === 'C' ? 'Counselling' : 'counselling')
    .replace(/\bcounselor\b/gi, (m) => m[0] === 'C' ? 'Counsellor' : 'counsellor')
    .replace(/\bcriminalize\b/gi, (m) => m[0] === 'C' ? 'Criminalise' : 'criminalise')
    .replace(/\bcriminalized\b/gi, (m) => m[0] === 'C' ? 'Criminalised' : 'criminalised')
    .replace(/\bspecialize\b/gi, (m) => m[0] === 'S' ? 'Specialise' : 'specialise')
    .replace(/\bspecialized\b/gi, (m) => m[0] === 'S' ? 'Specialised' : 'specialised')
    .replace(/\bspecializing\b/gi, (m) => m[0] === 'S' ? 'Specialising' : 'specialising')
    .replace(/\bauthorize\b/gi, (m) => m[0] === 'A' ? 'Authorise' : 'authorise')
    .replace(/\bauthorized\b/gi, (m) => m[0] === 'A' ? 'Authorised' : 'authorised')
    .replace(/\bemphasize\b/gi, (m) => m[0] === 'E' ? 'Emphasise' : 'emphasise')
    .replace(/\bemphasized\b/gi, (m) => m[0] === 'E' ? 'Emphasised' : 'emphasised')
    .replace(/\bemphasizing\b/gi, (m) => m[0] === 'E' ? 'Emphasising' : 'emphasising')
    .replace(/\bsummarize\b/gi, (m) => m[0] === 'S' ? 'Summarise' : 'summarise')
    .replace(/\bsummarized\b/gi, (m) => m[0] === 'S' ? 'Summarised' : 'summarised')
    .replace(/\bsummarizing\b/gi, (m) => m[0] === 'S' ? 'Summarising' : 'summarising')
    .replace(/\bminimize\b/gi, (m) => m[0] === 'M' ? 'Minimise' : 'minimise')
    .replace(/\bminimized\b/gi, (m) => m[0] === 'M' ? 'Minimised' : 'minimised')
    .replace(/\bmaximize\b/gi, (m) => m[0] === 'M' ? 'Maximise' : 'maximise')
    .replace(/\bmaximized\b/gi, (m) => m[0] === 'M' ? 'Maximised' : 'maximised')
    .replace(/\bnormalize\b/gi, (m) => m[0] === 'N' ? 'Normalise' : 'normalise')
    .replace(/\bnormalized\b/gi, (m) => m[0] === 'N' ? 'Normalised' : 'normalised')
    .replace(/\bprioritize\b/gi, (m) => m[0] === 'P' ? 'Prioritise' : 'prioritise')
    .replace(/\bprioritized\b/gi, (m) => m[0] === 'P' ? 'Prioritised' : 'prioritised')
    .replace(/\bapologize\b/gi, (m) => m[0] === 'A' ? 'Apologise' : 'apologise')
    .replace(/\bapologized\b/gi, (m) => m[0] === 'A' ? 'Apologised' : 'apologised')
    .replace(/\bcriticize\b/gi, (m) => m[0] === 'C' ? 'Criticise' : 'criticise')
    .replace(/\bcriticized\b/gi, (m) => m[0] === 'C' ? 'Criticised' : 'criticised')
    .replace(/\bcriticizing\b/gi, (m) => m[0] === 'C' ? 'Criticising' : 'criticising')
    .replace(/\bjeopardize\b/gi, (m) => m[0] === 'J' ? 'Jeopardise' : 'jeopardise')
    .replace(/\bjeopardized\b/gi, (m) => m[0] === 'J' ? 'Jeopardised' : 'jeopardised')
    .replace(/\blegalize\b/gi, (m) => m[0] === 'L' ? 'Legalise' : 'legalise')
    .replace(/\blegalized\b/gi, (m) => m[0] === 'L' ? 'Legalised' : 'legalised')
    .replace(/\bfinaliz/gi, (m) => m.replace(/liz/i, 'lis'))
    .replace(/\bgeneralize\b/gi, (m) => m[0] === 'G' ? 'Generalise' : 'generalise')
    .replace(/\bgeneralized\b/gi, (m) => m[0] === 'G' ? 'Generalised' : 'generalised')
    .replace(/\bcategorize\b/gi, (m) => m[0] === 'C' ? 'Categorise' : 'categorise')
    .replace(/\bcategorized\b/gi, (m) => m[0] === 'C' ? 'Categorised' : 'categorised')
    .replace(/\bharmonize\b/gi, (m) => m[0] === 'H' ? 'Harmonise' : 'harmonise')
    .replace(/\bjudgment\b/gi, (m) => m[0] === 'J' ? 'Judgement' : 'judgement')
    .replace(/\bpracticing\b/gi, (m) => m[0] === 'P' ? 'Practising' : 'practising')
    .replace(/\brealize\b/gi, (m) => m[0] === 'R' ? 'Realise' : 'realise')
    .replace(/\brealized\b/gi, (m) => m[0] === 'R' ? 'Realised' : 'realised')
    .replace(/\brealizing\b/gi, (m) => m[0] === 'R' ? 'Realising' : 'realising')
    .replace(/\bcustomize\b/gi, (m) => m[0] === 'C' ? 'Customise' : 'customise')
    .replace(/\bcustomized\b/gi, (m) => m[0] === 'C' ? 'Customised' : 'customised')
    .replace(/\boptimize\b/gi, (m) => m[0] === 'O' ? 'Optimise' : 'optimise')
    .replace(/\boptimized\b/gi, (m) => m[0] === 'O' ? 'Optimised' : 'optimised')
    .replace(/\bvisualize\b/gi, (m) => m[0] === 'V' ? 'Visualise' : 'visualise')
    .replace(/\bvisualized\b/gi, (m) => m[0] === 'V' ? 'Visualised' : 'visualised')
    .replace(/\bpenalize\b/gi, (m) => m[0] === 'P' ? 'Penalise' : 'penalise')
    .replace(/\bpenalized\b/gi, (m) => m[0] === 'P' ? 'Penalised' : 'penalised')
    .replace(/\bpenalizing\b/gi, (m) => m[0] === 'P' ? 'Penalising' : 'penalising')
    .replace(/\blegitimize\b/gi, (m) => m[0] === 'L' ? 'Legitimise' : 'legitimise')
    .replace(/\blegitimized\b/gi, (m) => m[0] === 'L' ? 'Legitimised' : 'legitimised')
    .replace(/\bstandardize\b/gi, (m) => m[0] === 'S' ? 'Standardise' : 'standardise')
    .replace(/\bstandardized\b/gi, (m) => m[0] === 'S' ? 'Standardised' : 'standardised')
    .replace(/\bcharacterize\b/gi, (m) => m[0] === 'C' ? 'Characterise' : 'characterise')
    .replace(/\bcharacterized\b/gi, (m) => m[0] === 'C' ? 'Characterised' : 'characterised')
    .replace(/\bcharacterizing\b/gi, (m) => m[0] === 'C' ? 'Characterising' : 'characterising')
    .replace(/\bmemorandum\b/gi, (m) => m[0] === 'M' ? 'Memorandum' : 'memorandum')
    .replace(/\bneighbor\b/gi, (m) => m[0] === 'N' ? 'Neighbour' : 'neighbour')
    .replace(/\bneighboring\b/gi, (m) => m[0] === 'N' ? 'Neighbouring' : 'neighbouring')
    .replace(/\bsignaling\b/gi, (m) => m[0] === 'S' ? 'Signalling' : 'signalling')
    .replace(/\btraveling\b/gi, (m) => m[0] === 'T' ? 'Travelling' : 'travelling')
    .replace(/\bmodeling\b/gi, (m) => m[0] === 'M' ? 'Modelling' : 'modelling')
    .replace(/\bprograming\b/gi, (m) => m[0] === 'P' ? 'Programming' : 'programming')
    // Criminal/legal context conversions
    .replace(/\btraumatize\b/gi, (m) => m[0] === 'T' ? 'Traumatise' : 'traumatise')
    .replace(/\btraumatized\b/gi, (m) => m[0] === 'T' ? 'Traumatised' : 'traumatised')
    .replace(/\btraumatizing\b/gi, (m) => m[0] === 'T' ? 'Traumatising' : 'traumatising')
    .replace(/\bvictimize\b/gi, (m) => m[0] === 'V' ? 'Victimise' : 'victimise')
    .replace(/\bvictimized\b/gi, (m) => m[0] === 'V' ? 'Victimised' : 'victimised')
    .replace(/\bvictimizing\b/gi, (m) => m[0] === 'V' ? 'Victimising' : 'victimising')
    .replace(/\bterrorize\b/gi, (m) => m[0] === 'T' ? 'Terrorise' : 'terrorise')
    .replace(/\bterrorized\b/gi, (m) => m[0] === 'T' ? 'Terrorised' : 'terrorised')
    .replace(/\bscrutinize\b/gi, (m) => m[0] === 'S' ? 'Scrutinise' : 'scrutinise')
    .replace(/\bscrutinized\b/gi, (m) => m[0] === 'S' ? 'Scrutinised' : 'scrutinised')
    .replace(/\bscrutinizing\b/gi, (m) => m[0] === 'S' ? 'Scrutinising' : 'scrutinising')
    .replace(/\bhypothesiz/gi, (m) => m.replace(/siz/i, 'sis'))
    .replace(/\brationalize\b/gi, (m) => m[0] === 'R' ? 'Rationalise' : 'rationalise')
    .replace(/\brationalized\b/gi, (m) => m[0] === 'R' ? 'Rationalised' : 'rationalised')
    .replace(/\bmarginalize\b/gi, (m) => m[0] === 'M' ? 'Marginalise' : 'marginalise')
    .replace(/\bmarginalized\b/gi, (m) => m[0] === 'M' ? 'Marginalised' : 'marginalised')
    .replace(/\bmarginalizing\b/gi, (m) => m[0] === 'M' ? 'Marginalising' : 'marginalising')
    .replace(/\bweaponize\b/gi, (m) => m[0] === 'W' ? 'Weaponise' : 'weaponise')
    .replace(/\bweaponized\b/gi, (m) => m[0] === 'W' ? 'Weaponised' : 'weaponised')
    .replace(/\bsympathize\b/gi, (m) => m[0] === 'S' ? 'Sympathise' : 'sympathise')
    .replace(/\bsympathized\b/gi, (m) => m[0] === 'S' ? 'Sympathised' : 'sympathised')
    .replace(/\bneutralize\b/gi, (m) => m[0] === 'N' ? 'Neutralise' : 'neutralise')
    .replace(/\bneutralized\b/gi, (m) => m[0] === 'N' ? 'Neutralised' : 'neutralised')
    .replace(/\bmobilize\b/gi, (m) => m[0] === 'M' ? 'Mobilise' : 'mobilise')
    .replace(/\bmobilized\b/gi, (m) => m[0] === 'M' ? 'Mobilised' : 'mobilised')
    .replace(/\bmemorize\b/gi, (m) => m[0] === 'M' ? 'Memorise' : 'memorise')
    .replace(/\bmemorized\b/gi, (m) => m[0] === 'M' ? 'Memorised' : 'memorised')
    // Noun/misc conversions
    .replace(/\blicen([sc])e\b/gi, (m) => m[0] === 'L' ? 'Licence' : 'licence')
    .replace(/\bpretense\b/gi, (m) => m[0] === 'P' ? 'Pretence' : 'pretence')
    .replace(/\bdialog\b/gi, (m) => m[0] === 'D' ? 'Dialogue' : 'dialogue')
    .replace(/\bcatalog\b/gi, (m) => m[0] === 'C' ? 'Catalogue' : 'catalogue')
    .replace(/\bcanceled\b/gi, (m) => m[0] === 'C' ? 'Cancelled' : 'cancelled')
    .replace(/\bcanceling\b/gi, (m) => m[0] === 'C' ? 'Cancelling' : 'cancelling')
    .replace(/\blabeled\b/gi, (m) => m[0] === 'L' ? 'Labelled' : 'labelled')
    .replace(/\blabeling\b/gi, (m) => m[0] === 'L' ? 'Labelling' : 'labelling')
    .replace(/\baging\b/gi, (m) => m[0] === 'A' ? 'Ageing' : 'ageing')
    .replace(/\bfulfill\b/gi, (m) => m[0] === 'F' ? 'Fulfil' : 'fulfil')
    .replace(/\bfulfilled\b/gi, (m) => m[0] === 'F' ? 'Fulfilled' : 'fulfilled')
    .replace(/\bmaneuver\b/gi, (m) => m[0] === 'M' ? 'Manoeuvre' : 'manoeuvre')
    .replace(/\bwillful\b/gi, (m) => m[0] === 'W' ? 'Wilful' : 'wilful')
    .replace(/\bskillful\b/gi, (m) => m[0] === 'S' ? 'Skilful' : 'skilful')
    // -or → -our
    .replace(/\brumor\b/gi, (m) => m[0] === 'R' ? 'Rumour' : 'rumour')
    .replace(/\bhumor\b/gi, (m) => m[0] === 'H' ? 'Humour' : 'humour')
    .replace(/\bflavor\b/gi, (m) => m[0] === 'F' ? 'Flavour' : 'flavour')
    // -er → -re
    .replace(/\bfiber\b/gi, (m) => m[0] === 'F' ? 'Fibre' : 'fibre')
    .replace(/\btheater\b/gi, (m) => m[0] === 'T' ? 'Theatre' : 'theatre')
    .replace(/\bmeter\b/gi, (m) => m[0] === 'M' ? 'Metre' : 'metre')
    // Medical/forensic
    .replace(/\bhemorrhage\b/gi, (m) => m[0] === 'H' ? 'Haemorrhage' : 'haemorrhage')
    .replace(/\banesthetic\b/gi, (m) => m[0] === 'A' ? 'Anaesthetic' : 'anaesthetic')
    .replace(/\bpediatric\b/gi, (m) => m[0] === 'P' ? 'Paediatric' : 'paediatric');
  }).join('');

  // DO_NOT_UNDO — Forensic appellate language enforcement
  // Converts direct accusatory language to proper forensic framing
  // RULE: Never directly blame the judge. Use varied forensic framing — not just "It is arguable".
  // Rotate: "It is arguable that", "It may be contended that", "There is a tenable argument that",
  //         "It is open to argument that", "A question arises as to whether",
  //         "It is submitted that", "Grounds may exist to suggest that",
  //         "It warrants consideration whether", "It is respectfully submitted that"

  // Counter to rotate forensic prefixes within a single pass
  let _forensicIdx = 0;
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
  const nextPrefix = () => _PREFIXES[_forensicIdx++ % _PREFIXES.length];

  const forensicFixes = [
    // ── Judge possessive patterns (e.g. "The sentencing judge's approach…") ──
    [/^The (sentencing |trial |appeal )?judge's /gm, (m, mod) => `${nextPrefix()} the ${mod || ''}judge's `],
    [/(\. )The (sentencing |trial |appeal )?judge's /g, (m, dot, mod) => `${dot}${nextPrefix()} the ${mod || ''}judge's `],

    // ── Judge action patterns — start of line ──
    [/^The (sentencing |trial |appeal )?judge (failed to|erred|was wrong|made an error|was biased|misdirected|ignored|disregarded|overlooked|should have|ought to have|did not|neglected to|omitted to)/gm,
      (m, mod, verb) => `${nextPrefix()} the ${mod || ''}judge ${verb}`],
    [/^The jury was misdirected/gm, () => `${nextPrefix()} the jury was misdirected`],
    [/^The court (ignored|wrongly|improperly|failed|erred|did not)/gm, (m, verb) => `${nextPrefix()} the court ${verb}`],
    [/^The trial was unfair/gm, () => `${nextPrefix()} the trial was unfair`],
    [/^The verdict (is|was) unreasonable/gm, (m, v) => `${nextPrefix()} the verdict ${v} unreasonable`],
    [/^The sentence (is|was) (inadequate|excessive|manifestly excessive|manifestly inadequate)/gm, (m, v, adj) => `${nextPrefix()} the sentence ${v} ${adj}`],
    [/^The directions were inadequate/gm, () => `${nextPrefix()} the directions were inadequate`],
    [/^The evidence was (wrongly|improperly)/gm, (m, adv) => `${nextPrefix()} the evidence was ${adv}`],
    [/^There was (no proper|a failure to)/gm, (m, rest) => `${nextPrefix()} there was ${rest}`],

    // ── Judge action patterns — mid-sentence (after ". ") ──
    [/(\. )The (sentencing |trial |appeal )?judge (failed to|erred|was wrong|made an error|was biased|misdirected|ignored|disregarded|overlooked|should have|ought to have|did not|neglected to|omitted to)/g,
      (m, dot, mod, verb) => `${dot}${nextPrefix()} the ${mod || ''}judge ${verb}`],
    [/(\. )The (court|jury) (ignored|wrongly|improperly|was misdirected|failed|erred|did not)/g,
      (m, dot, who, verb) => `${dot}${nextPrefix()} the ${who} ${verb}`],

    // ── Inline blame phrases (anywhere in text) ──
    [/\bwas clearly wrong\b/g, 'was arguably wrong'],
    [/\bwas plainly wrong\b/g, 'was arguably wrong'],
    [/\bwas fundamentally flawed\b/g, 'was arguably fundamentally flawed'],
    [/\bno reasonable judge\b/g, 'arguably no reasonable judge'],
    [/\bthe (sentencing |trial |appeal )?judge clearly erred\b/gi, (m, mod) => `it is contended that the ${mod || ''}judge erred`],
  ];
  for (const [pattern, replacer] of forensicFixes) {
    corrected = corrected.replace(pattern, replacer);
  }

  return corrected;
};

export default auSpelling;
