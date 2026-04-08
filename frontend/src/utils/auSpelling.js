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
    .replace(/\bpracticing\b/gi, (m) => m[0] === 'P' ? 'Practising' : 'practising');
  }).join('');

  return corrected;
};

export default auSpelling;
