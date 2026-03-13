/* DO NOT UNDO — LegalGlossary section. All features in this file are approved and must be preserved. */
import { Scale, ArrowLeft, Search, BookOpen, Gavel, Shield, FileText, Users, AlertTriangle, Clock, ChevronDown, ChevronRight, Moon, Sun } from "lucide-react";
import PageCTA from "../components/PageCTA";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Link } from "react-router-dom";
import { useState } from "react";
import { useTheme } from "../contexts/ThemeContext";

// Categorised glossary with more comprehensive terms
const glossaryCategories = [
  {
    id: "fundamentals",
    name: "Legal Fundamentals",
    icon: Scale,
    color: "amber",
    image: "https://images.unsplash.com/photo-1589578527966-fdac0f44566c?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=200&fit=crop",
    terms: [
      {
        term: "Mens Rea",
        latin: "Guilty Mind",
        simple: "The 'guilty mind' - what you were thinking",
        detailed: "Latin for 'guilty mind'. This refers to the mental state or intention behind committing a crime. For murder, the prosecution must prove you intended to kill or cause serious harm. Without proving mens rea, there's no crime.",
        example: "If someone accidentally causes death without intending harm, they may lack the mens rea for murder."
      },
      {
        term: "Actus Reus",
        latin: "Guilty Act",
        simple: "The 'guilty act' - what you actually did",
        detailed: "Latin for 'guilty act'. This is the physical act of committing the crime. Both actus reus (the act) and mens rea (the intent) must be proven for most serious crimes.",
        example: "The actus reus of assault is the physical act that causes someone to fear violence."
      },
      {
        term: "Burden of Proof",
        simple: "The prosecution must prove you're guilty - you don't have to prove you're innocent",
        detailed: "In criminal cases, the prosecution bears the burden of proving guilt 'beyond reasonable doubt'. The accused doesn't have to prove anything. If the jury has reasonable doubt, they must acquit.",
        example: "You don't need to prove where you were - the prosecution must prove you committed the crime."
      },
      {
        term: "Beyond Reasonable Doubt",
        simple: "The jury must be sure you did it",
        detailed: "The highest standard of proof in law. The jury must be satisfied so they feel sure of guilt. It's not about mathematical certainty, but there shouldn't be any reasonable doubt left.",
        example: "If jurors have lingering doubts about guilt, they cannot convict."
      },
      {
        term: "Standard of Proof",
        simple: "How sure the court needs to be",
        detailed: "Criminal cases require 'beyond reasonable doubt' (very high). Civil cases only require 'balance of probabilities' (more likely than not - over 50%).",
        example: "OJ Simpson was acquitted criminally but found liable civilly because of different standards."
      },
      {
        term: "Prima Facie",
        latin: "At First Sight",
        simple: "Evidence that looks sufficient on its face",
        detailed: "Latin meaning 'at first appearance'. A prima facie case means there's enough evidence that, if unopposed, would be sufficient to prove the case. It can be rebutted by contrary evidence.",
        example: "The prosecution established a prima facie case of theft when CCTV showed the defendant taking goods."
      },
      {
        term: "Onus",
        simple: "Who has to prove what",
        detailed: "The obligation to prove something. In criminal law, the onus is generally on the prosecution to prove guilt. In some defences (like diminished responsibility), the onus shifts to the defendant.",
        example: "The onus is on the prosecution to prove you weren't acting in self-defence."
      },
      {
        term: "Presumption of Innocence",
        simple: "You're innocent until proven guilty",
        detailed: "A fundamental right meaning every person charged with a crime is presumed innocent until the prosecution proves their guilt beyond reasonable doubt. The accused need not prove anything.",
        example: "Despite media coverage, the defendant must be treated as innocent until convicted."
      }
    ]
  },
  {
    id: "appeal_grounds",
    name: "Appeal Grounds",
    icon: Gavel,
    color: "red",
    image: "https://images.unsplash.com/photo-1662516201865-8633915e668a?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=200&fit=crop",
    terms: [
      {
        term: "Appellant",
        simple: "The person who is appealing",
        detailed: "The party who brings an appeal against a conviction or sentence. In criminal appeals, this is usually the person who was convicted, though the Crown can also appeal against sentence.",
        example: "As the appellant, you bear the burden of showing error in your trial."
      },
      {
        term: "Respondent",
        simple: "The other side in an appeal",
        detailed: "The party responding to an appeal. In criminal appeals, when you appeal your conviction, the Crown (prosecution) is the respondent. When the Crown appeals your sentence, you are the respondent.",
        example: "The Crown as respondent will argue your conviction should stand."
      },
      {
        term: "Leave to Appeal",
        simple: "Permission to appeal - some appeals need the court's approval first",
        detailed: "For some appeals, you need the court's permission before you can proceed. Appeals against sentence usually require leave. The court grants leave if there's an arguable case that the sentence was wrong.",
        example: "You need to apply for leave to appeal against your sentence within 28 days."
      },
      {
        term: "Grounds of Appeal",
        simple: "The specific reasons why your conviction or sentence should be overturned",
        detailed: "The legal arguments setting out why the appeal should succeed. Each ground identifies a specific error — such as a misdirection, procedural unfairness, or unreasonable verdict. Well-drafted grounds are essential to success.",
        example: "Ground 1: The trial judge misdirected the jury on the element of intent."
      },
      {
        term: "Miscarriage of Justice",
        simple: "When something went seriously wrong with your trial or conviction",
        detailed: "A broad term covering situations where the justice system has failed, resulting in an unfair outcome. Includes wrongful convictions, procedural errors, and other failures that undermine confidence in the verdict.",
        example: "Discovering the main witness lied under oath could constitute a miscarriage of justice."
      },
      {
        term: "Manifest Injustice",
        simple: "When the verdict or sentence is clearly wrong or unfair",
        detailed: "A ground for appeal where the outcome is so obviously unjust that it shocks the conscience. Courts can overturn convictions where there has been a serious miscarriage of justice.",
        example: "A life sentence for a minor first offence might be considered manifestly unjust."
      },
      {
        term: "Manifestly Excessive",
        simple: "When the sentence is way too harsh for what you did",
        detailed: "A common ground for sentence appeals. A sentence is manifestly excessive if it's clearly unreasonable or unjust given the circumstances of the offence and the offender. The error must be obvious, not just that another judge might have given less.",
        example: "A 10-year sentence for a first offence with strong mitigating factors may be manifestly excessive."
      },
      {
        term: "Manifestly Inadequate",
        simple: "When the sentence is too lenient (Crown appeals this)",
        detailed: "A ground used by the Crown when appealing a sentence. The sentence must be so unreasonably low that it fails to reflect the seriousness of the crime. The Crown must show the error is obvious.",
        example: "A suspended sentence for a violent home invasion may be manifestly inadequate."
      },
      {
        term: "Natural Justice",
        simple: "Your fundamental right to be treated fairly",
        detailed: "Also called procedural fairness. The basic principles that ensure a fair hearing: the right to know the case against you, the right to be heard, and the right to an impartial decision-maker. Denial of natural justice is a powerful appeal ground.",
        example: "Being denied the right to call witnesses or cross-examine is a breach of natural justice."
      },
      {
        term: "Denial of Natural Justice",
        simple: "When you weren't given a fair go",
        detailed: "Occurs when fundamental fairness principles are violated. This includes being denied a fair hearing, not being told the case against you, being judged by someone with bias, or being denied the right to present your defence. A strong ground for appeal.",
        example: "The judge refused to hear your alibi evidence — this is denial of natural justice."
      },
      {
        term: "Procedural Fairness",
        simple: "Your right to a fair process",
        detailed: "The same as natural justice. Means you have the right to know the case against you, the right to be heard, and the right to have your case decided by an impartial judge. Denial of procedural fairness is a strong appeal ground.",
        example: "The prosecution ambushed you with evidence you'd never seen before trial."
      },
      {
        term: "Misdirection",
        simple: "When the judge gives the jury wrong instructions",
        detailed: "If the trial judge incorrectly explains the law to the jury, this can be grounds for appeal. Common misdirections include wrong explanations of intent, self-defence, or burden of proof.",
        example: "The judge wrongly told jurors they could convict if they thought it was 'probably' the defendant."
      },
      {
        term: "Non-Direction",
        simple: "When the judge fails to tell the jury something important",
        detailed: "When a trial judge fails to give a necessary direction to the jury on a matter of law. The judge must direct on all essential elements of the offence and any defences raised.",
        example: "The judge failed to direct the jury on self-defence when it was clearly raised."
      },
      {
        term: "Fresh Evidence",
        simple: "New evidence that wasn't available at trial",
        detailed: "Evidence that has come to light after the trial that could have affected the verdict. To succeed on appeal, you generally need to show the evidence wasn't available at trial, is credible, and would likely have resulted in a different verdict.",
        example: "DNA testing that wasn't available in 1990 now shows someone else committed the crime."
      },
      {
        term: "Unsafe and Unsatisfactory Verdict",
        simple: "The jury got it wrong based on the evidence",
        detailed: "An appeal ground where the conviction is considered unsafe because no reasonable jury, properly instructed, could have convicted on the evidence presented. The appellate court asks whether there was reasonable doubt.",
        example: "The only evidence was a single unreliable witness with motivation to lie."
      },
      {
        term: "Unreasonable Verdict",
        simple: "No reasonable jury could have convicted on the evidence",
        detailed: "A ground of appeal arguing the verdict was against the weight of evidence. The appeal court considers whether, based on the whole evidence, it was open to the jury to be satisfied beyond reasonable doubt.",
        example: "The evidence was so weak that conviction was not reasonably open to the jury."
      },
      {
        term: "Ineffective Assistance of Counsel",
        simple: "Your lawyer didn't do their job properly",
        detailed: "If your defence lawyer's performance was so deficient that it affected the outcome of your trial, this can be grounds for appeal. Examples include failing to call important witnesses, not challenging key evidence, or not properly preparing.",
        example: "Your lawyer was drunk during trial and failed to cross-examine the key witness."
      },
      {
        term: "Judicial Bias",
        simple: "The judge wasn't fair or neutral",
        detailed: "If the trial judge showed prejudice against the accused, made inappropriate comments to the jury, or appeared to favour the prosecution, this can be grounds for appeal. Judges must be impartial.",
        example: "The judge told the jury 'people like the defendant' usually lie."
      },
      {
        term: "Judge Alone Trial",
        simple: "A trial decided by a judge without a jury",
        detailed: "Under s.132 Criminal Procedure Act 1986 (NSW), an accused can elect to be tried by a judge alone instead of a jury. Both prosecution and court must consent. The judge decides both fact and law.",
        example: "In complex fraud cases, defendants often elect for judge alone trial."
      },
      {
        term: "Perjury",
        simple: "A witness lying under oath",
        detailed: "The criminal offence of making false statements while under oath in court. If discovered after trial, perjured evidence can be grounds for appeal as it undermines the fairness of the proceedings.",
        example: "The main witness later admitted they made up their testimony."
      },
      {
        term: "Quash",
        simple: "To overturn or cancel a conviction",
        detailed: "When an appeal court sets aside a conviction, it 'quashes' it. The conviction is treated as if it never happened. A new trial may or may not be ordered depending on the circumstances.",
        example: "The Court of Criminal Appeal quashed the conviction due to the trial judge's misdirection."
      },
      {
        term: "Remit",
        simple: "To send back for reconsideration",
        detailed: "When an appeal court sends a matter back to a lower court for further hearing or a new trial. Often occurs when a conviction is quashed but a retrial is warranted.",
        example: "The matter was remitted for a new trial before a different judge."
      },
      {
        term: "Resentence",
        simple: "To give a new sentence",
        detailed: "When an appeal court finds a sentence was wrong, it may resentence the offender itself or send the matter back for resentencing. The new sentence can be higher or lower.",
        example: "The CCA found the sentence manifestly excessive and resentenced to 8 years."
      }
    ]
  },
  {
    id: "defences",
    name: "Defences",
    icon: Shield,
    color: "emerald",
    image: "https://images.unsplash.com/photo-1589307904488-7d60ff29c975?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=200&fit=crop",
    terms: [
      {
        term: "Self-Defence",
        simple: "Using force to protect yourself from harm",
        detailed: "Under s.418-420 Crimes Act 1900 (NSW), you're not criminally responsible if you believed your conduct was necessary to defend yourself and the response was reasonable in the circumstances.",
        example: "Punching someone who was about to stab you would likely be self-defence."
      },
      {
        term: "Duress",
        simple: "Being forced to commit a crime under threat",
        detailed: "A defence where you were forced to commit a crime because of threats of death or serious injury. The threat must be immediate and there must be no reasonable opportunity to escape or seek help.",
        example: "Being forced to drive a getaway car while your family is held at gunpoint."
      },
      {
        term: "Necessity",
        simple: "Breaking the law to prevent greater harm",
        detailed: "A defence where you committed an offence to prevent a greater evil. The harm avoided must be greater than the harm caused, and there must be no lawful alternative.",
        example: "Breaking into a car to rescue a child locked inside on a hot day."
      },
      {
        term: "Provocation",
        simple: "Being pushed to act by extreme circumstances",
        detailed: "A partial defence that can reduce murder to manslaughter. It requires the accused to have lost self-control due to conduct of the deceased that would cause an ordinary person to lose control.",
        example: "Discovering your partner in bed with someone else and reacting violently."
      },
      {
        term: "Diminished Responsibility",
        simple: "Mental condition affected your ability to understand or control your actions",
        detailed: "A partial defence under s.23A Crimes Act 1900 (NSW). If you had an abnormality of mind that substantially impaired your capacity to understand, judge right from wrong, or control yourself, murder can be reduced to manslaughter.",
        example: "Severe PTSD from war service substantially impaired judgment during the offence."
      },
      {
        term: "Mental Illness Defence",
        simple: "Not guilty because of mental illness",
        detailed: "Under s.38 Mental Health and Cognitive Impairment Forensic Provisions Act 2020 (NSW), if you didn't know the nature of your act, or didn't know it was wrong, due to mental illness, you may be found not guilty by reason of mental illness.",
        example: "Believing you were defending against aliens due to schizophrenia."
      },
      {
        term: "Automatism",
        simple: "Acting without conscious control",
        detailed: "A defence where the accused acted involuntarily, without conscious control of their actions. Can arise from sleepwalking, concussion, diabetic episodes, or other causes of involuntary conduct.",
        example: "Causing injury while sleepwalking and completely unconscious."
      },
      {
        term: "Intoxication",
        simple: "Being drunk or drugged affected your mental state",
        detailed: "Generally not a defence, but may be relevant to whether you formed the required intent for specific intent crimes. Voluntary intoxication is treated differently from involuntary intoxication (e.g., drink spiking).",
        example: "Being so drunk you couldn't form the specific intent to steal."
      },
      {
        term: "Alibi",
        simple: "You weren't there - you were somewhere else",
        detailed: "Evidence that you were in a different place when the crime occurred, making it impossible for you to have committed it. Must generally be disclosed to prosecution before trial.",
        example: "CCTV showing you at work in Sydney when the crime happened in Melbourne."
      },
      {
        term: "Honest and Reasonable Mistake",
        simple: "You genuinely believed something that turned out to be wrong",
        detailed: "A defence where you held an honest belief based on reasonable grounds. Common in consent cases - if you honestly and reasonably believed consent was given, you may have a defence.",
        example: "Reasonably believing you had permission to take property that wasn't yours."
      }
    ]
  },
  {
    id: "offences",
    name: "Criminal Offences",
    icon: AlertTriangle,
    color: "purple",
    image: "https://images.unsplash.com/photo-1764113697577-b5899b9a339d?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=200&fit=crop",
    terms: [
      {
        term: "Murder",
        simple: "Intentionally killing someone, or killing with reckless indifference to life",
        detailed: "Under s.18 Crimes Act 1900 (NSW), murder is the unlawful killing of another person with intent to kill, intent to cause grievous bodily harm, or with reckless indifference to human life. Carries life imprisonment.",
        example: "Shooting someone intending to kill them is murder."
      },
      {
        term: "Manslaughter",
        simple: "Killing someone without the intent required for murder",
        detailed: "Unlawful killing that lacks the intent for murder. Can be voluntary (killing with intent but with a partial defence) or involuntary (killing by an unlawful and dangerous act, or criminal negligence).",
        example: "A punch that unexpectedly causes death may be manslaughter."
      },
      {
        term: "Assault",
        simple: "Intentionally or recklessly causing someone to fear immediate violence",
        detailed: "Under s.61 Crimes Act 1900 (NSW), assault is any act that intentionally or recklessly causes another person to apprehend immediate and unlawful violence. Physical contact is not required.",
        example: "Raising your fist threateningly can be assault even without contact."
      },
      {
        term: "Grievous Bodily Harm (GBH)",
        simple: "Really serious injury - permanent or life-threatening",
        detailed: "Includes any permanent or serious disfiguring, destruction of a foetus, or any grievous bodily disease. Under s.33 Crimes Act 1900 (NSW), causing GBH with intent carries maximum 25 years.",
        example: "Breaking someone's spine, causing permanent paralysis."
      },
      {
        term: "Actual Bodily Harm (ABH)",
        simple: "An injury that interferes with health or comfort",
        detailed: "Any hurt or injury that interferes with health or comfort, more than merely transient or trifling. Bruises, scratches, and psychological harm can constitute ABH.",
        example: "A black eye or broken nose would be ABH."
      },
      {
        term: "Sexual Assault",
        simple: "Sexual intercourse without consent",
        detailed: "Under s.61I Crimes Act 1900 (NSW), sexual assault occurs when a person has sexual intercourse with another without their consent, knowing they don't consent. Maximum penalty life imprisonment.",
        example: "Any sexual penetration without free and voluntary consent."
      },
      {
        term: "Robbery",
        simple: "Stealing using force or fear",
        detailed: "Theft accompanied by violence or threat of violence. Under s.94 Crimes Act 1900 (NSW), robbery with wounding or armed robbery carry severe penalties up to 25 years imprisonment.",
        example: "Threatening someone with a knife to take their wallet."
      },
      {
        term: "Larceny (Theft)",
        simple: "Taking someone's property without permission, intending to keep it",
        detailed: "The unlawful taking and carrying away of property belonging to another with intent to permanently deprive them of it. Under s.117 Crimes Act 1900 (NSW), maximum penalty is 5 years.",
        example: "Shoplifting goods from a store."
      },
      {
        term: "Break and Enter",
        simple: "Breaking into a building to commit a crime",
        detailed: "Entering a dwelling-house or building with intent to commit a serious indictable offence. Under s.112 Crimes Act 1900 (NSW), aggravated break and enter carries up to 20 years imprisonment.",
        example: "Breaking a window to enter a house and steal items."
      },
      {
        term: "Drug Supply",
        simple: "Giving, selling, or distributing drugs",
        detailed: "Under the Drug Misuse and Trafficking Act 1985 (NSW), supply includes selling, giving, distributing, or agreeing to supply. Penalties depend on drug type and quantity - up to life for commercial quantities.",
        example: "Selling cocaine to another person."
      },
      {
        term: "Fraud",
        simple: "Deceiving someone to get money or property",
        detailed: "Under s.192E Crimes Act 1900 (NSW), fraud involves dishonestly obtaining property or financial advantage by deception. Maximum penalty is 10 years imprisonment.",
        example: "Using fake documents to obtain a bank loan."
      },
      {
        term: "Domestic Violence",
        simple: "Violence or abuse against a family member or partner",
        detailed: "Includes physical, sexual, emotional, psychological, and economic abuse within a domestic relationship. Domestic violence offences often carry aggravated penalties.",
        example: "Assaulting a spouse or partner in a relationship."
      },
      {
        term: "Coercive Control",
        simple: "A pattern of behaviour used to dominate and control someone",
        detailed: "Behaviour that is abusive and seeks to control a partner through intimidation, isolation, and restrictions. Now a criminal offence in NSW, carrying up to 7 years imprisonment.",
        example: "Monitoring someone's movements, isolating them from friends, controlling their money."
      }
    ]
  },
  {
    id: "evidence",
    name: "Evidence Rules",
    icon: FileText,
    color: "blue",
    image: "https://images.unsplash.com/photo-1619771914272-e3c1e5e4e5e3?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=200&fit=crop",
    terms: [
      {
        term: "Hearsay Evidence",
        simple: "Secondhand information - 'someone told me that...'",
        detailed: "Evidence of what someone else said, offered to prove the truth of what was said. Generally inadmissible because the original speaker can't be cross-examined. If wrongly admitted, may be grounds for appeal.",
        example: "'John told me he saw the defendant at the scene' - John should testify himself."
      },
      {
        term: "Circumstantial Evidence",
        simple: "Evidence that suggests something happened, but doesn't directly prove it",
        detailed: "Indirect evidence that requires the jury to draw inferences. The circumstances must exclude any reasonable hypothesis consistent with innocence. Used when there's no direct evidence.",
        example: "Finding the defendant's fingerprints and DNA at the crime scene."
      },
      {
        term: "Direct Evidence",
        simple: "Evidence that directly proves a fact",
        detailed: "Evidence that, if believed, directly establishes a fact without inference. Contrasted with circumstantial evidence which requires reasoning to reach a conclusion.",
        example: "An eyewitness saying 'I saw the defendant stab the victim.'"
      },
      {
        term: "Admissibility",
        simple: "Whether evidence is allowed in court",
        detailed: "Whether evidence can be presented to the jury. Evidence must be relevant, not unfairly prejudicial, and comply with rules excluding hearsay, opinion evidence, and improperly obtained evidence.",
        example: "A confession obtained through torture would be inadmissible."
      },
      {
        term: "Exclusionary Rule",
        simple: "Keeping out evidence that was obtained unfairly",
        detailed: "Under s.138 Evidence Act 1995 (NSW), evidence obtained improperly or illegally may be excluded if its admission would be unfair or bring the administration of justice into disrepute.",
        example: "Evidence from an illegal search of your home may be excluded."
      },
      {
        term: "Voir Dire",
        simple: "A 'trial within a trial' to decide if evidence is allowed",
        detailed: "A hearing held in the absence of the jury to determine whether certain evidence should be admitted. Common for confessions, identification evidence, and disputed evidence.",
        example: "The judge hears arguments about whether the confession was voluntary."
      },
      {
        term: "Cross-Examination",
        simple: "Questioning the other side's witnesses",
        detailed: "The right to question witnesses called by the opposing party. Essential for testing reliability and credibility of evidence. Denial of cross-examination can be grounds for appeal.",
        example: "The defence lawyer questions the prosecution's key witness."
      },
      {
        term: "Expert Evidence",
        simple: "Evidence from someone with specialised knowledge",
        detailed: "Opinion evidence from a person with specialised knowledge based on training, study, or experience. Must be based on specialised knowledge and relevant to the case.",
        example: "A forensic scientist explaining DNA matching procedures."
      },
      {
        term: "Corroboration",
        simple: "Supporting evidence that confirms other evidence",
        detailed: "Independent evidence that supports or confirms other evidence in the case. Particularly important for identification evidence, accomplice evidence, and complainant evidence.",
        example: "CCTV footage that supports an eyewitness account."
      },
      {
        term: "Propensity Evidence",
        simple: "Evidence about your past behaviour or character",
        detailed: "Evidence of previous conduct used to suggest you're the type of person who would commit the offence. Generally inadmissible but with exceptions for showing system, pattern, or motive.",
        example: "Past fraud convictions being used to suggest you committed this fraud."
      }
    ]
  },
  {
    id: "court_process",
    name: "Court Process",
    icon: Clock,
    color: "slate",
    image: "https://images.unsplash.com/photo-1769092992534-f2d0210162b9?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=200&fit=crop",
    terms: [
      {
        term: "Bail",
        simple: "Being released from custody while waiting for your trial",
        detailed: "Under the Bail Act 2013 (NSW), bail allows release from custody with conditions. Courts consider flight risk, danger to community, and offence seriousness. Some offences have 'show cause' requirements.",
        example: "Released on bail with conditions to report to police weekly."
      },
      {
        term: "Remand",
        simple: "Being held in custody while waiting for trial",
        detailed: "When bail is refused, you're held on remand until your trial. Time on remand is usually counted as time served if convicted.",
        example: "Spending 6 months in custody awaiting trial counts toward your sentence."
      },
      {
        term: "Committal Hearing",
        simple: "A hearing to decide if there's enough evidence for trial",
        detailed: "A preliminary hearing in the Local Court to determine if there's sufficient evidence for a person to stand trial in a higher court. The magistrate decides if a reasonable jury could convict.",
        example: "The magistrate finds there's enough evidence to commit you to trial."
      },
      {
        term: "Indictment",
        simple: "The formal document setting out the charges against you",
        detailed: "A written accusation charging a person with a serious criminal offence. For serious crimes tried in higher courts, the indictment lists the specific charges and particulars.",
        example: "The indictment charges you with one count of murder."
      },
      {
        term: "Arraignment",
        simple: "When you're formally asked to plead guilty or not guilty",
        detailed: "The formal reading of charges and recording of the accused's plea. This typically occurs at the start of the trial in higher courts.",
        example: "The charges are read and you plead 'not guilty.'"
      },
      {
        term: "Sentencing Remarks",
        simple: "The judge's explanation of why they gave you that sentence",
        detailed: "The reasons the judge provides for the sentence imposed. Important for appeals as they show what the judge considered and may reveal errors.",
        example: "The judge explains why a custodial sentence is necessary."
      },
      {
        term: "Notice of Intention to Appeal",
        simple: "Telling the court you want to appeal",
        detailed: "The formal document you must file within 28 days of conviction or sentence to start the appeal process. Filing this preserves your right to appeal.",
        example: "Filing notice within 28 days to appeal against conviction."
      },
      {
        term: "Court of Criminal Appeal (CCA)",
        simple: "The court that hears criminal appeals in NSW",
        detailed: "The division of the Supreme Court of NSW that hears appeals against conviction and sentence from the District and Supreme Courts. Usually heard by 3 judges.",
        example: "Your appeal will be heard by three judges in the CCA."
      },
      {
        term: "Special Leave to Appeal",
        simple: "Permission to appeal to the High Court",
        detailed: "To appeal to the High Court of Australia, you must first obtain special leave. The High Court grants leave only for cases involving important questions of law.",
        example: "The High Court grants special leave because your case raises constitutional issues."
      },
      {
        term: "Double Jeopardy",
        simple: "You can't be tried twice for the same crime",
        detailed: "A fundamental principle protecting against being prosecuted multiple times for the same offence. However, there are limited exceptions for fresh and compelling evidence in serious cases.",
        example: "After acquittal, you generally cannot be retried for that offence."
      }
    ]
  },
  {
    id: "sentencing",
    name: "Sentencing",
    icon: Users,
    color: "orange",
    image: "https://images.unsplash.com/photo-1589578527966-fdac0f44566c?crop=entropy&cs=srgb&fm=jpg&q=85&w=400&h=200&fit=crop",
    terms: [
      {
        term: "Non-Parole Period (NPP)",
        simple: "The minimum time you must serve before you can apply for parole",
        detailed: "The part of your sentence you must serve in prison before being eligible for release on parole. For example, an 18-year sentence with 12-year NPP means earliest parole at 12 years.",
        example: "You're sentenced to 10 years with a 6-year non-parole period."
      },
      {
        term: "Standard Non-Parole Period (SNPP)",
        simple: "The 'starting point' sentence for serious crimes",
        detailed: "A reference point set by parliament for sentencing certain serious offences. Judges must consider the SNPP but can depart from it based on circumstances.",
        example: "The SNPP for murder is 20 years, but the judge may vary this."
      },
      {
        term: "Mitigating Factors",
        simple: "Things that might reduce your sentence",
        detailed: "Circumstances that reduce the seriousness of the offence or offender's culpability. Includes early guilty plea, remorse, good character, mental health issues, and assistance to authorities.",
        example: "Your early guilty plea and genuine remorse may reduce your sentence."
      },
      {
        term: "Aggravating Factors",
        simple: "Things that might increase your sentence",
        detailed: "Circumstances that increase the seriousness of the offence. Includes previous convictions, vulnerability of victim, use of weapons, breach of trust, and offences committed while on bail.",
        example: "The use of a weapon and the victim's age increase your sentence."
      },
      {
        term: "Intensive Correction Order (ICO)",
        simple: "A sentence served in the community instead of prison",
        detailed: "An alternative to imprisonment where you serve your sentence in the community under strict supervision. May include home detention, electronic monitoring, and community service.",
        example: "Instead of prison, you're given an ICO with home detention."
      },
      {
        term: "Community Correction Order (CCO)",
        simple: "A supervised order in the community",
        detailed: "A sentence that allows you to remain in the community while completing certain conditions. Can include supervision, community service, drug testing, and treatment programmes.",
        example: "You're sentenced to a 2-year CCO with 200 hours community service."
      },
      {
        term: "Concurrent Sentences",
        simple: "Multiple sentences served at the same time",
        detailed: "When convicted of multiple offences, sentences can be served concurrently (at the same time) rather than consecutively. The total time served is the longest individual sentence.",
        example: "Your two 3-year sentences run concurrently, so you serve 3 years total."
      },
      {
        term: "Consecutive Sentences",
        simple: "Multiple sentences served one after another",
        detailed: "When convicted of multiple offences, sentences can be served consecutively (one after the other). Also called cumulative sentences. Increases total time in custody.",
        example: "Your two 3-year sentences run consecutively, so you serve 6 years."
      },
      {
        term: "Time Served",
        simple: "Credit for time already spent in custody",
        detailed: "Time spent in custody on remand awaiting trial or sentence is usually credited against the sentence imposed. You don't serve the same time twice.",
        example: "You've been on remand for 6 months, which counts toward your sentence."
      },
      {
        term: "Parole",
        simple: "Early release from prison under supervision",
        detailed: "Release from prison before the end of the sentence, subject to conditions and supervision. If you breach parole conditions, you can be returned to custody.",
        example: "Released on parole after serving your non-parole period with good behaviour."
      }
    ]
  }
];

const LegalGlossary = () => {
  const { theme, toggleTheme } = useTheme();
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedTerms, setExpandedTerms] = useState({});
  const [activeCategory, setActiveCategory] = useState("all");
  const [viewDensity, setViewDensity] = useState("compact");

  const getAllTerms = () => {
    let allTerms = [];
    glossaryCategories.forEach(cat => {
      cat.terms.forEach(term => {
        allTerms.push({ ...term, category: cat.name, categoryId: cat.id, color: cat.color });
      });
    });
    return allTerms;
  };

  const getFilteredTerms = () => {
    let terms = activeCategory === "all" 
      ? getAllTerms() 
      : glossaryCategories.find(c => c.id === activeCategory)?.terms.map(t => ({
          ...t,
          category: glossaryCategories.find(c => c.id === activeCategory).name,
          categoryId: activeCategory,
          color: glossaryCategories.find(c => c.id === activeCategory).color
        })) || [];
    
    if (searchTerm) {
      terms = terms.filter(item =>
        item.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.simple.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.detailed.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return terms;
  };

  const toggleExpand = (term) => {
    setExpandedTerms(prev => ({ ...prev, [term]: !prev[term] }));
  };

  const colorClasses = {
    amber: "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800",
    red: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800",
    emerald: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800",
    purple: "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-800",
    blue: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800",
    slate: "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700",
    orange: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 border-orange-200 dark:border-orange-800",
  };

  const filteredTerms = getFilteredTerms();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-slate-900 dark:bg-slate-950 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Appeal Case Manager
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <Link to="/">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section with Image */}
      <section className="relative py-16 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1589578527966-fdac0f44566c?crop=entropy&cs=srgb&fm=jpg&q=85&w=1920" 
            alt="Lady Justice"
            className="w-full h-full object-cover opacity-10 dark:opacity-5"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-amber-500/30">
            <BookOpen className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Legal Terms Explained
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Don't know your mens rea from your actus reus? No worries. Here's what all the legal jargon means in <strong>plain English</strong>.
          </p>
          <p className="text-sm text-muted-foreground mt-4">
            <strong>{getAllTerms().length} terms</strong> across {glossaryCategories.length} categories
          </p>
        </div>
      </section>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 pb-16">
        <section className="mb-6" data-testid="glossary-content-intro">
          <p className="text-xs uppercase tracking-widest text-amber-600 dark:text-amber-500 font-semibold mb-1">Glossary Navigator</p>
          <h2 className="text-xl font-bold text-foreground" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Scan terms quickly or read in full detail
          </h2>
        </section>

        {/* Search Bar */}
        <div className="relative mb-8 max-w-xl mx-auto">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search for any legal term..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-12 py-6 text-base rounded-xl border-2 focus:border-amber-500"
            data-testid="glossary-search"
          />
        </div>

        <div className="flex items-center justify-center gap-2 mb-8" data-testid="glossary-density-toggle">
          <button
            onClick={() => setViewDensity("compact")}
            className={`px-4 py-2 rounded-lg text-xs font-semibold border transition-colors ${
              viewDensity === "compact"
                ? "bg-amber-600 text-white border-amber-600"
                : "bg-card text-muted-foreground border-border hover:border-amber-500"
            }`}
            data-testid="glossary-density-compact"
          >
            Compact View
          </button>
          <button
            onClick={() => setViewDensity("expanded")}
            className={`px-4 py-2 rounded-lg text-xs font-semibold border transition-colors ${
              viewDensity === "expanded"
                ? "bg-amber-600 text-white border-amber-600"
                : "bg-card text-muted-foreground border-border hover:border-amber-500"
            }`}
            data-testid="glossary-density-expanded"
          >
            Expanded View
          </button>
        </div>

        {/* Category Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <button
            onClick={() => setActiveCategory("all")}
            className={`p-4 rounded-xl border-2 transition-all ${
              activeCategory === "all" 
                ? "border-amber-500 bg-amber-50 dark:bg-amber-900/20" 
                : "border-border hover:border-amber-500/50"
            }`}
          >
            <BookOpen className={`w-6 h-6 mx-auto mb-2 ${activeCategory === "all" ? "text-amber-600" : "text-muted-foreground"}`} />
            <p className={`font-semibold text-sm ${activeCategory === "all" ? "text-amber-700 dark:text-amber-400" : "text-foreground"}`}>
              All Terms
            </p>
            <p className="text-xs text-muted-foreground">{getAllTerms().length} terms</p>
          </button>
          
          {glossaryCategories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`p-4 rounded-xl border-2 transition-all ${
                activeCategory === cat.id 
                  ? `border-amber-500 bg-amber-50 dark:bg-amber-900/20` 
                  : "border-border hover:border-amber-500/50"
              }`}
            >
              <cat.icon className={`w-6 h-6 mx-auto mb-2 ${activeCategory === cat.id ? "text-amber-600" : "text-muted-foreground"}`} />
              <p className={`font-semibold text-sm ${activeCategory === cat.id ? "text-amber-700 dark:text-amber-400" : "text-foreground"}`}>
                {cat.name}
              </p>
              <p className="text-xs text-muted-foreground">{cat.terms.length} terms</p>
            </button>
          ))}
        </div>

        {/* Active Category Image Banner */}
        {activeCategory !== "all" && (
          <div className="mb-8 rounded-2xl overflow-hidden relative h-40">
            <img 
              src={glossaryCategories.find(c => c.id === activeCategory)?.image}
              alt={glossaryCategories.find(c => c.id === activeCategory)?.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-slate-900/90 to-slate-900/50 flex items-center px-8">
              <div>
                <h2 className="text-2xl font-bold text-white" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  {glossaryCategories.find(c => c.id === activeCategory)?.name}
                </h2>
                <p className="text-slate-300 text-sm mt-1">
                  {glossaryCategories.find(c => c.id === activeCategory)?.terms.length} legal terms explained
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Terms List */}
        <div className={viewDensity === "compact" ? "grid xl:grid-cols-2 gap-3" : "space-y-4"} data-testid="glossary-terms-list">
          {filteredTerms.map((item, index) => (
            <div 
              key={`${item.term}-${index}`}
              className="bg-card border border-border rounded-xl overflow-hidden hover:shadow-lg hover:border-amber-500/30 transition-all"
            >
              <button
                onClick={() => toggleExpand(item.term)}
                className={`w-full text-left flex items-start justify-between gap-4 ${viewDensity === "compact" ? "p-4" : "p-5"}`}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className={`font-bold text-foreground ${viewDensity === "compact" ? "text-base" : "text-lg"}`} style={{ fontFamily: 'Crimson Pro, serif' }}>
                      {item.term}
                    </h3>
                    {item.latin && (
                      <span className="text-xs italic text-muted-foreground">({item.latin})</span>
                    )}
                    {activeCategory === "all" && (
                      <span className={`text-xs px-2 py-0.5 rounded-lg border ${colorClasses[item.color]}`}>
                        {item.category}
                      </span>
                    )}
                  </div>
                  <p className={`text-muted-foreground ${viewDensity === "compact" ? "text-sm" : "text-base"}`}>{item.simple}</p>
                </div>
                <div className={`p-2 rounded-lg transition-colors ${expandedTerms[item.term] ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-muted'}`}>
                  {expandedTerms[item.term] ? (
                    <ChevronDown className="w-5 h-5 text-amber-600" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-muted-foreground" />
                  )}
                </div>
              </button>
              
              {expandedTerms[item.term] && (
                <div className={`${viewDensity === "compact" ? "px-4 pb-4" : "px-5 pb-5"}`}>
                  <div className={`bg-muted/50 rounded-xl border-l-4 border-amber-500 space-y-4 ${viewDensity === "compact" ? "p-4" : "p-5"}`}>
                    <div>
                      <h4 className="text-sm font-semibold text-foreground mb-2">Detailed Explanation</h4>
                      <p className="text-muted-foreground text-sm leading-relaxed">{item.detailed}</p>
                    </div>
                    {item.example && (
                      <div className="pt-3 border-t border-border">
                        <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                          <span className="w-5 h-5 rounded bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-amber-600 text-xs">Ex</span>
                          Example
                        </h4>
                        <p className="text-muted-foreground text-sm italic">"{item.example}"</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {filteredTerms.length === 0 && (
          <div className="text-center py-16">
            <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-foreground font-semibold">No terms found matching "{searchTerm}"</p>
            <p className="text-muted-foreground text-sm mt-2">Try a different search term or browse categories above</p>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-12 p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-800 dark:text-red-300">Important Disclaimer</h3>
              <p className="text-red-700 dark:text-red-400 text-sm mt-1">
                This glossary is for <strong>educational purposes only</strong> and does not constitute legal advice. 
                Laws vary by jurisdiction and change over time. Always consult a qualified legal professional for advice about your specific situation.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LegalGlossary;
