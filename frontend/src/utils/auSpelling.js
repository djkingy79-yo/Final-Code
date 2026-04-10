/* DO NOT UNDO — Australian spelling normaliser for ALL user-visible text.
   Converts American English to Australian English. Used across all components
   that display AI-generated or dynamic content. */

const auSpelling = (text) => {
  if (!text) return text;

  // Split text into "protected" (URLs, markdown links, code blocks) and "plain" segments.
  // Only apply spelling corrections to plain-text segments.
  const PROTECTED = /(\[[^\]]*\]\([^)]*\)|https?:\/\/[^\s)]+|`[^`]+`)/g;
  const parts = text.split(PROTECTED);

  const corrected = parts.map((part) => {
    // If the part matches a protected pattern, return it untouched
    if (PROTECTED.test(part)) return part;
    // Reset lastIndex since we reuse the regex
    PROTECTED.lastIndex = 0;

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
    corrected = corrected.replace(pattern, replacer);
  }

  return corrected;
};

export default auSpelling;
