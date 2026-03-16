"""Causal reasoning glitch probes.

Tests whether LLMs maintain consistent causal models including
causal chains, counterfactuals, confounding variables, and interventions.
"""

from __future__ import annotations

from glitch.probes import BaseProbe, ProbeDomain, ProbeItem


class CausalProbe(BaseProbe):
    """Probes for causal reasoning consistency."""

    domain = ProbeDomain.CAUSAL

    def get_probes(self) -> list[ProbeItem]:
        return [
            # --- Causal chains ---
            ProbeItem(
                id="causal-001",
                domain=self.domain,
                category="causal_chain",
                setup=(
                    "A drought causes crops to fail. Failed crops cause food prices to rise. "
                    "Rising food prices cause public unrest."
                ),
                question="If the drought had not occurred, would there be public unrest (assuming no other causes)?",
                expected_answer=(
                    "No. Without the drought, crops would not fail, prices would not rise, "
                    "and there would be no unrest (given no other causes in this chain)."
                ),
                explanation="Removing the root cause eliminates all downstream effects in a simple chain.",
                difficulty=1,
                consistency_checks=[
                    "If the drought occurs but the government subsidizes food, would unrest still happen?",
                    "What is the most upstream cause of the unrest?",
                    "Is the drought a sufficient cause of unrest or merely a necessary one in this scenario?",
                ],
            ),
            ProbeItem(
                id="causal-002",
                domain=self.domain,
                category="causal_chain",
                setup=(
                    "Domino A knocks over Domino B. Domino B knocks over Domino C. "
                    "Domino C knocks over Domino D. Someone removes Domino C from the line."
                ),
                question="After removing Domino C, what happens when Domino A is pushed?",
                expected_answer=(
                    "A knocks over B, but the chain stops there. B cannot reach D "
                    "because C (the intermediary) has been removed. D stays standing."
                ),
                explanation="Breaking a link in a causal chain blocks downstream effects.",
                difficulty=1,
                consistency_checks=[
                    "Is Domino B still knocked over?",
                    "What if C is replaced and B had already fallen — would pushing B again knock over C?",
                ],
            ),
            ProbeItem(
                id="causal-003",
                domain=self.domain,
                category="causal_chain",
                setup=(
                    "In a factory, Machine 1 produces Part A. Machine 2 takes Part A and "
                    "adds Part B to make Component X. Machine 3 takes Component X and "
                    "Part C to make the Final Product. Machine 2 breaks down."
                ),
                question="Can the factory still produce the Final Product? What specifically is blocked?",
                expected_answer=(
                    "No. Without Machine 2, Component X cannot be made (even though Part A "
                    "is available from Machine 1). Without Component X, Machine 3 cannot make "
                    "the Final Product. Machine 1 can still produce Part A, but it accumulates unused."
                ),
                explanation="A broken intermediate step blocks the entire downstream process.",
                difficulty=2,
                consistency_checks=[
                    "Can Machine 1 still operate?",
                    "If someone manually assembles Component X, can Machine 3 resume?",
                ],
            ),
            # --- Counterfactual reasoning ---
            ProbeItem(
                id="causal-004",
                domain=self.domain,
                category="counterfactual",
                setup=(
                    "A student studied hard for an exam and scored 95%. "
                    "Historically, students who study hard score between 85-100%, "
                    "and students who don't study score between 40-65%."
                ),
                question="If the student had not studied, would they likely have scored 95%?",
                expected_answer=(
                    "No, very unlikely. Without studying, they would likely score between "
                    "40-65%, far below 95%. The studying was likely a crucial cause of the high score."
                ),
                explanation="The counterfactual (no studying) leads to a dramatically different expected outcome.",
                difficulty=1,
                consistency_checks=[
                    "Could the student have scored 95% without studying?",
                    "Does studying guarantee a score of 95%?",
                ],
            ),
            ProbeItem(
                id="causal-005",
                domain=self.domain,
                category="counterfactual",
                setup=(
                    "A bridge collapsed because (1) it was overloaded with traffic AND "
                    "(2) it had a structural defect. Both conditions were necessary — the bridge "
                    "would have survived either condition alone."
                ),
                question="If only the structural defect existed (no overloading), would the bridge collapse?",
                expected_answer=(
                    "No. Both conditions were stated as jointly necessary. "
                    "The structural defect alone would not cause collapse."
                ),
                explanation="When causes are jointly necessary, removing either prevents the effect.",
                difficulty=2,
                consistency_checks=[
                    "If only the overloading existed (no defect), would it collapse?",
                    "Are both causes equally 'responsible' for the collapse?",
                    "Is this an AND-gate or OR-gate causal structure?",
                ],
            ),
            ProbeItem(
                id="causal-006",
                domain=self.domain,
                category="counterfactual",
                setup=(
                    "Two assassins independently shoot at a target at the same time. "
                    "Both bullets hit. Either bullet alone would have been lethal."
                ),
                question=(
                    "If Assassin A had not fired, would the target still have died?"
                ),
                expected_answer=(
                    "Yes. Assassin B's bullet alone was lethal. The target would have died "
                    "regardless. This is a case of causal overdetermination."
                ),
                explanation="With overdetermination, each cause is individually sufficient.",
                difficulty=3,
                consistency_checks=[
                    "Is Assassin A a cause of death?",
                    "Is Assassin B a cause of death?",
                    "How does this differ from the bridge example where both causes were necessary?",
                ],
            ),
            # --- Confounding variables ---
            ProbeItem(
                id="causal-007",
                domain=self.domain,
                category="confounding",
                setup=(
                    "A study finds that cities with more ice cream sales have higher crime rates. "
                    "Someone concludes that ice cream causes crime."
                ),
                question="What is wrong with this causal conclusion?",
                expected_answer=(
                    "This is a spurious correlation caused by a confounding variable: temperature "
                    "(or season). Hot weather independently increases both ice cream sales and crime. "
                    "Ice cream does not cause crime."
                ),
                explanation="Classic confounding example where a third variable (heat) drives both observed variables.",
                difficulty=1,
                consistency_checks=[
                    "If we control for temperature, would the correlation likely disappear?",
                    "Does banning ice cream reduce crime?",
                    "What type of study design would establish actual causation?",
                ],
            ),
            ProbeItem(
                id="causal-008",
                domain=self.domain,
                category="confounding",
                setup=(
                    "A study finds that hospitals with more doctors have higher mortality rates. "
                    "A newspaper headlines: 'More Doctors = More Deaths.'"
                ),
                question="Why is this headline misleading? What confound explains the pattern?",
                expected_answer=(
                    "The confound is severity of illness. Hospitals with more doctors tend to "
                    "be large trauma centers and teaching hospitals that treat the most severe cases. "
                    "The sicker patients drive both the need for more doctors and the higher "
                    "mortality rates. This is a form of Simpson's paradox / selection bias."
                ),
                explanation="Patient acuity confounds the relationship between doctor count and outcomes.",
                difficulty=2,
                consistency_checks=[
                    "If we compare similar-severity patients, would more doctors likely help?",
                    "Is this an example of Simpson's paradox?",
                ],
            ),
            ProbeItem(
                id="causal-009",
                domain=self.domain,
                category="confounding",
                setup=(
                    "Observational data shows that people who take vitamin D supplements have "
                    "better health outcomes. However, people who take supplements also tend to "
                    "be wealthier, exercise more, and have better healthcare access."
                ),
                question=(
                    "Can we conclude that vitamin D supplements cause better health outcomes? "
                    "What would be needed to establish causation?"
                ),
                expected_answer=(
                    "No, we cannot conclude causation from this observational data. The confounds "
                    "(wealth, exercise, healthcare) could explain the association. A randomized "
                    "controlled trial (RCT) where participants are randomly assigned to supplement "
                    "vs. placebo would control for these confounds."
                ),
                explanation="Multiple confounders make causal inference from observational data unreliable.",
                difficulty=2,
                consistency_checks=[
                    "Why does randomization help with confounders?",
                    "Could there be confounders we haven't even thought of?",
                ],
            ),
            # --- Interventions vs. observations ---
            ProbeItem(
                id="causal-010",
                domain=self.domain,
                category="intervention",
                setup=(
                    "A barometer reading drops. Shortly after, it rains. "
                    "There is a strong correlation between low barometer readings and rain."
                ),
                question="If you artificially force the barometer reading down, will it rain?",
                expected_answer=(
                    "No. The barometer doesn't cause rain. Both the barometer reading and "
                    "the rain are caused by atmospheric pressure changes. Intervening on the "
                    "barometer (breaking the causal mechanism) doesn't affect the weather."
                ),
                explanation="Intervening on an effect doesn't change other effects of the same cause.",
                difficulty=2,
                consistency_checks=[
                    "What is the common cause of both the barometer reading and rain?",
                    "Is the barometer reading a cause, effect, or neither of rain?",
                ],
            ),
            ProbeItem(
                id="causal-011",
                domain=self.domain,
                category="intervention",
                setup=(
                    "In a town, rooster crowing always precedes sunrise. "
                    "A strict correlation holds: every day the rooster crows, then the sun rises."
                ),
                question="If you silence the rooster, will the sun fail to rise?",
                expected_answer=(
                    "No. The rooster's crowing does not cause the sunrise. The Earth's rotation "
                    "causes sunrise, and the approaching dawn causes the rooster to crow. "
                    "Silencing the rooster does not affect the sun."
                ),
                explanation="Temporal precedence alone does not establish causation.",
                difficulty=1,
                consistency_checks=[
                    "What logical fallacy is 'the rooster causes sunrise'?",
                    "What actually causes the rooster to crow?",
                ],
            ),
            # --- Causal reasoning under uncertainty ---
            ProbeItem(
                id="causal-012",
                domain=self.domain,
                category="probabilistic",
                setup=(
                    "Smoking increases the risk of lung cancer from about 1% to about 15% "
                    "over a lifetime. A specific smoker develops lung cancer."
                ),
                question="Did smoking cause this specific individual's lung cancer?",
                expected_answer=(
                    "We cannot say with certainty. Smoking greatly increased the probability "
                    "(from ~1% to ~15%), making it a likely contributing cause, but some "
                    "non-smokers also get lung cancer. For this individual, we can say smoking "
                    "substantially raised the risk, but we can't prove it was the specific cause."
                ),
                explanation="Individual causal attribution differs from population-level causal effects.",
                difficulty=3,
                consistency_checks=[
                    "If the person had not smoked, could they still have gotten lung cancer?",
                    "Is it accurate to say smoking 'caused' the cancer at a population level?",
                ],
            ),
            # --- Causal structure identification ---
            ProbeItem(
                id="causal-013",
                domain=self.domain,
                category="structure",
                setup=(
                    "Rain causes the sidewalk to be wet. A sprinkler also causes the sidewalk "
                    "to be wet. A wet sidewalk causes pedestrians to slip."
                ),
                question=(
                    "If we observe that the sidewalk is wet and a pedestrian slipped, "
                    "can we determine whether it rained or the sprinkler was on?"
                ),
                expected_answer=(
                    "No. The wet sidewalk has two possible causes (rain and sprinkler), "
                    "and observing the effect (slipping) doesn't tell us which cause was active. "
                    "This is a causal structure called a 'fork' or 'collider' depending on the "
                    "direction. Here wet sidewalk has two parents — we'd need additional evidence "
                    "to distinguish the cause."
                ),
                explanation="Multiple sufficient causes lead to ambiguity when only the effect is observed.",
                difficulty=3,
                consistency_checks=[
                    "If we know the sprinkler was off, can we infer it rained?",
                    "Does the slipping tell us anything about rain vs. sprinkler?",
                ],
            ),
            ProbeItem(
                id="causal-014",
                domain=self.domain,
                category="structure",
                setup=(
                    "A company observes: when they run ads, sales increase. "
                    "When sales increase, stock price goes up. "
                    "They also notice: when the economy is good, both ad spending "
                    "and sales increase independently."
                ),
                question="Draw out the causal relationships. Does the economy confound the ad-sales relationship?",
                expected_answer=(
                    "Yes. There are two paths from ads to sales: (1) ads -> sales (direct cause) "
                    "and (2) economy -> ads and economy -> sales (confound). The economy drives both "
                    "ad spending and sales independently, so the observed correlation between ads "
                    "and sales is partly causal and partly confounded."
                ),
                explanation="Both a direct causal path and a confounding path exist simultaneously.",
                difficulty=3,
                consistency_checks=[
                    "How could the company isolate the true causal effect of ads on sales?",
                    "If the economy is bad but they run ads, would sales still increase?",
                ],
            ),
            ProbeItem(
                id="causal-015",
                domain=self.domain,
                category="reversal",
                setup=(
                    "Every time a fire truck arrives at a location, there is significant property "
                    "damage observed. In 100% of cases where fire trucks are present, damage is found."
                ),
                question="Does the fire truck cause the property damage?",
                expected_answer=(
                    "No. The causal direction is reversed. The fire (not the fire truck) causes "
                    "the property damage. The fire truck arrives because of the fire. The fire "
                    "is a common cause of both the truck's presence and the damage. Reducing "
                    "fire trucks would increase damage, not decrease it."
                ),
                explanation="Correlation with reversed causal direction — classic fallacy.",
                difficulty=1,
                consistency_checks=[
                    "If we sent fewer fire trucks, would property damage decrease?",
                    "What is the actual cause of the property damage?",
                    "What type of causal error is being made here?",
                ],
            ),
        ]
