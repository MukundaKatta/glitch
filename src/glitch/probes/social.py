"""Social reasoning glitch probes.

Tests whether LLMs maintain consistent social models including
character consistency, theory of mind, social norms, and group dynamics.
"""

from __future__ import annotations

from glitch.probes import BaseProbe, ProbeDomain, ProbeItem


class SocialProbe(BaseProbe):
    """Probes for social reasoning consistency."""

    domain = ProbeDomain.SOCIAL

    def get_probes(self) -> list[ProbeItem]:
        return [
            # --- Character consistency ---
            ProbeItem(
                id="social-001",
                domain=self.domain,
                category="character_consistency",
                setup=(
                    "Maria is described as an extremely frugal person who clips coupons, "
                    "never eats out, drives a 20-year-old car, and carefully tracks every penny. "
                    "She earns $50,000/year and has saved $400,000 over 15 years."
                ),
                question=(
                    "Maria just impulsively bought a $80,000 luxury sports car. "
                    "Is this consistent with her character as described?"
                ),
                expected_answer=(
                    "No, this is highly inconsistent. An extremely frugal person who drives "
                    "a 20-year-old car and tracks every penny would be very unlikely to "
                    "impulsively buy an $80,000 luxury car. This contradicts her established "
                    "personality traits and financial behavior patterns."
                ),
                explanation="Established character traits should predict future behavior; sudden reversals need explanation.",
                difficulty=1,
                consistency_checks=[
                    "What would need to change for this purchase to be consistent with Maria's character?",
                    "Is it possible for frugal people to make exceptions? Under what circumstances?",
                ],
            ),
            ProbeItem(
                id="social-002",
                domain=self.domain,
                category="character_consistency",
                setup=(
                    "In a story, Detective Chen is established as meticulous, methodical, "
                    "and someone who never jumps to conclusions. He insists on hard evidence "
                    "and has reprimanded subordinates for making assumptions."
                ),
                question=(
                    "In the next chapter, Detective Chen sees a suspect near the crime scene "
                    "and immediately arrests them based on a 'gut feeling,' ignoring that "
                    "the suspect has an alibi. Is this consistent writing?"
                ),
                expected_answer=(
                    "No. This directly contradicts Chen's established character. A meticulous "
                    "detective who insists on evidence and reprimands others for assumptions "
                    "would not arrest someone on a gut feeling while ignoring an alibi. "
                    "This is a character consistency glitch."
                ),
                explanation="Character actions should follow from established traits unless motivated by plot.",
                difficulty=2,
                consistency_checks=[
                    "What plot development could justify this out-of-character behavior?",
                    "Would the reader find this believable without explanation?",
                ],
            ),
            ProbeItem(
                id="social-003",
                domain=self.domain,
                category="character_consistency",
                setup=(
                    "Alex is described as: deathly afraid of heights, claustrophobic, "
                    "and allergic to cats. Alex works as an accountant and prefers routine."
                ),
                question=(
                    "A story has Alex enthusiastically sign up for skydiving, then go spelunking "
                    "in tight caves, and then adopt three cats. How many inconsistencies are there?"
                ),
                expected_answer=(
                    "Three inconsistencies: (1) Skydiving contradicts the fear of heights. "
                    "(2) Spelunking in tight caves contradicts the claustrophobia. "
                    "(3) Adopting cats contradicts the cat allergy. Each action directly "
                    "contradicts an established character trait."
                ),
                explanation="Each action violates a specific stated trait.",
                difficulty=1,
                consistency_checks=[
                    "Could Alex do any of these things if they were getting therapy for their phobias?",
                    "Which inconsistency is the most problematic (health risk vs. fear)?",
                ],
            ),
            # --- Theory of mind ---
            ProbeItem(
                id="social-004",
                domain=self.domain,
                category="theory_of_mind",
                setup=(
                    "Sally puts a marble in a basket and leaves the room. "
                    "While Sally is away, Anne moves the marble from the basket to a box. "
                    "Sally returns to the room."
                ),
                question="Where will Sally look for the marble?",
                expected_answer=(
                    "Sally will look in the basket. She doesn't know Anne moved the marble "
                    "because she was out of the room. Sally has a false belief that the "
                    "marble is still where she left it."
                ),
                explanation="Classic Sally-Anne false belief test for theory of mind.",
                difficulty=1,
                consistency_checks=[
                    "Where is the marble actually?",
                    "Does Anne know where Sally thinks the marble is?",
                    "If Sally watched through a window, where would she look?",
                ],
            ),
            ProbeItem(
                id="social-005",
                domain=self.domain,
                category="theory_of_mind",
                setup=(
                    "Bob tells Carol: 'I love the gift you gave me!' while smiling broadly. "
                    "However, earlier Bob privately told Dave: 'I hate the gift Carol gave me "
                    "but I don't want to hurt her feelings.'"
                ),
                question="What does Carol believe about Bob's feelings toward the gift? What does Dave believe?",
                expected_answer=(
                    "Carol believes Bob loves the gift (she heard his enthusiastic statement "
                    "and saw his smile). Dave believes Bob hates the gift (he heard Bob's "
                    "private confession). They have different beliefs about the same situation "
                    "based on different information."
                ),
                explanation="Different agents have different mental models based on available information.",
                difficulty=2,
                consistency_checks=[
                    "If Dave tells Carol what Bob said privately, how would Carol's belief change?",
                    "Does Bob know what both Carol and Dave believe?",
                ],
            ),
            ProbeItem(
                id="social-006",
                domain=self.domain,
                category="theory_of_mind",
                setup=(
                    "A poker game: Player 1 has a terrible hand but bets big with confidence. "
                    "Player 2 has a great hand and knows that Player 1 tends to bluff. "
                    "Player 3 is new and doesn't know Player 1's bluffing tendency."
                ),
                question=(
                    "How do Player 2 and Player 3 differently interpret Player 1's big bet?"
                ),
                expected_answer=(
                    "Player 2, knowing Player 1 bluffs, likely interprets the big bet as a bluff "
                    "and may call or raise with confidence. Player 3, without this knowledge, "
                    "likely interprets the big bet as a sign of a strong hand and may fold. "
                    "Their different knowledge about Player 1 leads to different inferences."
                ),
                explanation="Knowledge about others' behavioral patterns affects interpretation of actions.",
                difficulty=3,
                consistency_checks=[
                    "If Player 1 knows that Player 2 knows they bluff, how might Player 1 adjust?",
                    "This is what level of reasoning in game theory?",
                ],
            ),
            # --- Social norms ---
            ProbeItem(
                id="social-007",
                domain=self.domain,
                category="social_norms",
                setup=(
                    "At a formal business dinner at an upscale restaurant with the CEO "
                    "and potential investors."
                ),
                question=(
                    "Rate the social appropriateness of these behaviors at the dinner: "
                    "(A) Answering a phone call at the table. "
                    "(B) Using the correct fork for each course. "
                    "(C) Telling an off-color joke. "
                    "(D) Asking thoughtful questions about the business."
                ),
                expected_answer=(
                    "(A) Inappropriate — taking a call at a formal dinner is rude. "
                    "(B) Appropriate — demonstrates social awareness and etiquette. "
                    "(C) Very inappropriate — risky and unprofessional with investors and CEO. "
                    "(D) Appropriate — shows engagement and interest."
                ),
                explanation="Social norms vary by context; formal business dinners have strict expectations.",
                difficulty=1,
                consistency_checks=[
                    "Would answer (A) change if the caller was from the hospital about a family emergency?",
                    "Would these norms be different at a casual team lunch?",
                ],
            ),
            ProbeItem(
                id="social-008",
                domain=self.domain,
                category="social_norms",
                setup=(
                    "In Japan, it is customary to bow when greeting someone. "
                    "In the United States, a firm handshake is the norm. "
                    "In France, close acquaintances greet with cheek kisses (la bise)."
                ),
                question=(
                    "A Japanese businessperson meets a French colleague in New York. "
                    "What greeting would be most appropriate and least awkward?"
                ),
                expected_answer=(
                    "In a cross-cultural business context in New York, a handshake (the local norm) "
                    "is typically the safest common ground. Both parties are likely familiar with "
                    "handshakes in international business contexts. A slight bow with a handshake "
                    "could show cultural awareness without risk of misunderstanding."
                ),
                explanation="Cross-cultural interactions often default to the local norm or the most universally understood gesture.",
                difficulty=2,
                consistency_checks=[
                    "Would the answer change if the meeting were in Tokyo?",
                    "What if they had met many times before and were close friends?",
                ],
            ),
            # --- Emotional reasoning ---
            ProbeItem(
                id="social-009",
                domain=self.domain,
                category="emotional_reasoning",
                setup=(
                    "A child just won first place in a school art competition. "
                    "Their parent is smiling and hugging them."
                ),
                question=(
                    "How is the child most likely feeling? How about the parent? "
                    "How would the child who won second place likely feel?"
                ),
                expected_answer=(
                    "The winning child likely feels happy, proud, and excited. "
                    "The parent likely feels proud, happy, and loving. "
                    "The second-place child likely feels a mix: some pride in placing, "
                    "but also disappointment at not winning, and possibly some envy or "
                    "frustration — especially if the margin was close."
                ),
                explanation="Different roles and outcomes in the same event produce different emotional responses.",
                difficulty=1,
                consistency_checks=[
                    "If the second-place child's parent is angry at the judges, is that a typical response?",
                    "How might the winning child feel if their best friend came in second?",
                ],
            ),
            ProbeItem(
                id="social-010",
                domain=self.domain,
                category="emotional_reasoning",
                setup=(
                    "A manager publicly criticizes an employee's work in front of the entire team, "
                    "pointing out mistakes in a harsh, dismissive tone."
                ),
                question=(
                    "How does the employee likely feel? How do the observing coworkers likely feel?"
                ),
                expected_answer=(
                    "The employee likely feels humiliated, embarrassed, angry, and possibly anxious "
                    "about job security. Coworkers likely feel uncomfortable, anxious (wondering if "
                    "they could be next), sympathetic toward the employee, and may lose respect for "
                    "the manager. Some may feel relieved it wasn't them."
                ),
                explanation="Public criticism has cascading emotional effects beyond the target.",
                difficulty=2,
                consistency_checks=[
                    "Would private criticism produce the same emotional response?",
                    "How might this affect the employee's future work performance?",
                ],
            ),
            # --- Social dynamics and power ---
            ProbeItem(
                id="social-011",
                domain=self.domain,
                category="social_dynamics",
                setup=(
                    "In a group project, four people have these roles: "
                    "Anna is the team leader. Ben is a quiet expert who does most of the work. "
                    "Clara is socially dominant and talks the most. "
                    "Dave is new and deferential to everyone."
                ),
                question=(
                    "If Anna is absent from a meeting, who is most likely to take charge? "
                    "Why might this differ from who should take charge?"
                ),
                expected_answer=(
                    "Clara is most likely to take charge because she is socially dominant and "
                    "talks the most — people often default to the loudest voice. However, Ben "
                    "should arguably take charge as the most knowledgeable team member. "
                    "This highlights the common mismatch between social dominance and competence."
                ),
                explanation="Social dominance and technical competence are different dimensions of leadership.",
                difficulty=2,
                consistency_checks=[
                    "Would Dave challenge either Clara or Ben? Why not?",
                    "How could the team structure prevent this competence-dominance mismatch?",
                ],
            ),
            ProbeItem(
                id="social-012",
                domain=self.domain,
                category="social_dynamics",
                setup=(
                    "A group of six friends always eats together at lunch. "
                    "A new student asks to join. Four of the friends want the new student to join, "
                    "but two (including the most popular/influential friend) are against it."
                ),
                question="What is the most likely outcome?",
                expected_answer=(
                    "Despite the 4-2 majority in favor, the most likely outcome is that the "
                    "new student is not welcomed, or is only grudgingly accepted. Social groups "
                    "often follow the preferences of high-status members rather than majority rule. "
                    "The four might not push back against the popular friend."
                ),
                explanation="Social influence is not evenly distributed; high-status individuals have disproportionate sway.",
                difficulty=3,
                consistency_checks=[
                    "Would the outcome change if the four supporters strongly advocated?",
                    "What social dynamics make people defer to the popular friend?",
                ],
            ),
            # --- Deception and trust ---
            ProbeItem(
                id="social-013",
                domain=self.domain,
                category="deception",
                setup=(
                    "A car salesperson says: 'This car has never been in an accident.' "
                    "The buyer later discovers the car's frame has been repaired, which "
                    "indicates a significant collision."
                ),
                question=(
                    "Did the salesperson lie? What are the possible interpretations?"
                ),
                expected_answer=(
                    "Most likely, yes — the salesperson either lied outright or was being "
                    "deliberately misleading. Possible interpretations: (1) The salesperson "
                    "knowingly lied. (2) The salesperson didn't personally know about the accident "
                    "(less likely given their professional duty to check). (3) The salesperson "
                    "was using a technicality (e.g., 'this car' after a VIN swap). Interpretation "
                    "1 is most probable."
                ),
                explanation="Social reasoning about deception requires considering intent, knowledge, and incentives.",
                difficulty=2,
                consistency_checks=[
                    "Does the salesperson's financial incentive affect your assessment?",
                    "What would the salesperson need to have not known to be innocent?",
                ],
            ),
            # --- Motivation and incentives ---
            ProbeItem(
                id="social-014",
                domain=self.domain,
                category="motivation",
                setup=(
                    "A company CEO publicly announces a major charitable donation "
                    "of $10 million right before a product launch that has received "
                    "negative press for environmental concerns."
                ),
                question="What might be the CEO's motivations? Are they purely altruistic?",
                expected_answer=(
                    "Multiple motivations are likely: (1) Genuine altruism and desire to help. "
                    "(2) Strategic PR to counter negative press before the product launch. "
                    "(3) Tax benefits. (4) Personal reputation management. The timing strongly "
                    "suggests PR motivation is at least a significant factor, though it doesn't "
                    "necessarily exclude genuine altruism."
                ),
                explanation="Actions often have multiple motivations; timing provides evidence about intent.",
                difficulty=2,
                consistency_checks=[
                    "If the donation were made quietly with no press release, would your assessment change?",
                    "Is it possible for an action to be both self-interested and genuinely altruistic?",
                ],
            ),
            ProbeItem(
                id="social-015",
                domain=self.domain,
                category="motivation",
                setup=(
                    "An employee who has been vocally unhappy and looking for other jobs "
                    "suddenly becomes the most enthusiastic team member, volunteering for "
                    "extra projects and praising the company publicly on social media."
                ),
                question="What are the most likely explanations for this behavioral change?",
                expected_answer=(
                    "Possible explanations ranked by likelihood: (1) They received a competing "
                    "job offer and are leveraging it for a raise/promotion (strategic behavior). "
                    "(2) Something genuinely changed — new manager, new project, resolved grievance. "
                    "(3) They are building a visible track record before leaving (resume padding). "
                    "(4) They received a warning about their attitude. The abruptness of the change "
                    "suggests strategic motivation rather than genuine change of heart."
                ),
                explanation="Sudden behavioral reversals in social contexts often indicate strategic rather than genuine change.",
                difficulty=3,
                consistency_checks=[
                    "What additional information would help determine the true motivation?",
                    "If they had gradually become more enthusiastic over months, would your assessment differ?",
                ],
            ),
        ]
