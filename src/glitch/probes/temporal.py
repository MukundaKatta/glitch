"""Temporal reasoning glitch probes.

Tests whether LLMs maintain consistent temporal representations across
event ordering, duration estimation, temporal transitivity, and time-zone reasoning.
"""

from __future__ import annotations

from glitch.probes import BaseProbe, ProbeDomain, ProbeItem


class TemporalProbe(BaseProbe):
    """Probes for temporal reasoning consistency."""

    domain = ProbeDomain.TEMPORAL

    def get_probes(self) -> list[ProbeItem]:
        return [
            # --- Event ordering ---
            ProbeItem(
                id="temporal-001",
                domain=self.domain,
                category="event_ordering",
                setup=(
                    "Alice woke up, then ate breakfast, then drove to work, "
                    "then attended a meeting, then ate lunch."
                ),
                question="What did Alice do immediately before attending the meeting?",
                expected_answer="Alice drove to work immediately before attending the meeting.",
                explanation="The sequence is: woke up -> breakfast -> drove -> meeting -> lunch.",
                difficulty=1,
                consistency_checks=[
                    "What did Alice do immediately after eating breakfast?",
                    "Did Alice eat lunch before or after the meeting?",
                    "What was the third thing Alice did?",
                ],
            ),
            ProbeItem(
                id="temporal-002",
                domain=self.domain,
                category="event_ordering",
                setup=(
                    "Events occurred in this order: The Berlin Wall fell (1989), "
                    "the World Wide Web was invented (1991), the Euro was introduced (1999), "
                    "the iPhone was released (2007), and COVID-19 was declared a pandemic (2020)."
                ),
                question=(
                    "A person was born the year the Euro was introduced. Were they old enough "
                    "to legally drive (age 16) when COVID-19 was declared a pandemic?"
                ),
                expected_answer=(
                    "A person born in 1999 would have been 20 or 21 in 2020. "
                    "Yes, they were old enough to drive."
                ),
                explanation="2020 - 1999 = 21 years, which is greater than 16.",
                difficulty=2,
                consistency_checks=[
                    "How old were they when the iPhone was released?",
                    "Were they alive when the Berlin Wall fell?",
                ],
            ),
            ProbeItem(
                id="temporal-003",
                domain=self.domain,
                category="event_ordering",
                setup=(
                    "In a story: First, the knight found a sword. Then, the knight slayed "
                    "a dragon. Later, the knight rescued a princess. Finally, the knight "
                    "returned to the kingdom. Now, I want you to tell this story in reverse."
                ),
                question="In the reversed story, what happens immediately after the knight is in the kingdom?",
                expected_answer=(
                    "In the reversed story, after starting in the kingdom, "
                    "the knight un-rescues (or leaves) the princess."
                ),
                explanation=(
                    "Reversed order: kingdom -> princess -> dragon -> sword. "
                    "After the kingdom event, the princess event comes next in reverse."
                ),
                difficulty=3,
                consistency_checks=[
                    "In the reversed story, what is the last event?",
                    "In the reversed story, does the dragon event come before or after the princess event?",
                ],
            ),
            # --- Duration estimation ---
            ProbeItem(
                id="temporal-004",
                domain=self.domain,
                category="duration",
                setup=(
                    "A flight from New York to London takes about 7 hours. "
                    "A flight from London to Tokyo takes about 12 hours."
                ),
                question=(
                    "If someone flies from New York to London, has a 3-hour layover, "
                    "and then flies to Tokyo, roughly how long is the total journey?"
                ),
                expected_answer="Approximately 22 hours (7 + 3 + 12).",
                explanation="Sum the flight times and layover.",
                difficulty=1,
                consistency_checks=[
                    "If they left New York at 6 PM, approximately what time (in total elapsed hours) would they arrive in Tokyo?",
                    "Is the London-to-Tokyo leg longer than the New York-to-London leg?",
                ],
            ),
            ProbeItem(
                id="temporal-005",
                domain=self.domain,
                category="duration",
                setup=(
                    "A task takes Alice 6 hours to complete alone. "
                    "The same task takes Bob 3 hours to complete alone."
                ),
                question="If Alice and Bob work together, how long does the task take?",
                expected_answer=(
                    "2 hours. Alice does 1/6 per hour, Bob does 1/3 per hour. "
                    "Together: 1/6 + 1/3 = 1/2 per hour, so 2 hours total."
                ),
                explanation="Combined rate: 1/6 + 1/3 = 1/6 + 2/6 = 3/6 = 1/2 per hour.",
                difficulty=2,
                consistency_checks=[
                    "In 1 hour of working together, what fraction of the task is done?",
                    "Does it make sense that together they are faster than either alone?",
                ],
            ),
            ProbeItem(
                id="temporal-006",
                domain=self.domain,
                category="duration",
                setup=(
                    "A train leaves Station A at 9:00 AM traveling at 60 km/h. "
                    "Another train leaves Station B (300 km away) at 10:00 AM traveling "
                    "toward Station A at 90 km/h."
                ),
                question="At what time do the two trains meet?",
                expected_answer=(
                    "At 11:36 AM. By 10:00 AM, the first train has traveled 60 km, "
                    "leaving 240 km between them. Combined closing speed is 150 km/h. "
                    "240/150 = 1.6 hours = 1 hour 36 minutes after 10:00 AM = 11:36 AM."
                ),
                explanation=(
                    "Train A travels 60 km in the first hour. Remaining gap is 240 km. "
                    "Closing speed: 60 + 90 = 150 km/h. Time: 240/150 = 1.6 hours = 1h 36min. "
                    "They meet at 11:36 AM."
                ),
                difficulty=3,
                consistency_checks=[
                    "How far from Station A do they meet?",
                    "How far has each train traveled when they meet?",
                ],
            ),
            # --- Temporal transitivity ---
            ProbeItem(
                id="temporal-007",
                domain=self.domain,
                category="transitivity",
                setup=(
                    "Event A happened before Event B. Event B happened before Event C. "
                    "Event C happened before Event D."
                ),
                question="Did Event A happen before Event D?",
                expected_answer="Yes, Event A happened before Event D.",
                explanation="Temporal precedence is transitive: A < B < C < D.",
                difficulty=1,
                consistency_checks=[
                    "Did Event D happen before Event A?",
                    "Which event happened most recently?",
                    "How many events happened between A and D?",
                ],
            ),
            ProbeItem(
                id="temporal-008",
                domain=self.domain,
                category="transitivity",
                setup=(
                    "Tom is older than Sarah. Sarah is older than Mike. "
                    "Mike is older than Jenny. Jenny is 20 years old."
                ),
                question="Is Tom older or younger than Jenny?",
                expected_answer="Tom is older than Jenny.",
                explanation="Tom > Sarah > Mike > Jenny in age, so Tom is the oldest.",
                difficulty=1,
                consistency_checks=[
                    "Is Tom at least 21 years old?",
                    "Could Sarah be 19 years old?",
                    "Who is the youngest?",
                ],
            ),
            # --- Temporal impossibilities ---
            ProbeItem(
                id="temporal-009",
                domain=self.domain,
                category="impossibility",
                setup=(
                    "A biography states: 'Professor Smith published her groundbreaking paper in 1985. "
                    "She received her PhD in 1990. She began her undergraduate studies in 1995.'"
                ),
                question="Is there anything temporally inconsistent in this biography?",
                expected_answer=(
                    "Yes. The events are in reverse chronological order but presented as a "
                    "forward narrative. One typically begins undergrad studies, then earns a PhD, "
                    "then publishes. The biography has her publishing before getting her PhD "
                    "and starting undergrad after both."
                ),
                explanation="The normal order is: undergrad (1995?) -> PhD -> publication, but dates are reversed.",
                difficulty=2,
                consistency_checks=[
                    "In what year would you expect her undergrad to start if she got her PhD in 1990?",
                    "Could someone publish a paper before getting a PhD?",
                ],
            ),
            ProbeItem(
                id="temporal-010",
                domain=self.domain,
                category="impossibility",
                setup=(
                    "A detective's case notes read: 'The victim was last seen alive at 3 PM on Tuesday. "
                    "The coroner estimates time of death at 1 PM on Tuesday. A witness reports hearing "
                    "a gunshot at 4 PM on Tuesday.'"
                ),
                question="What temporal inconsistencies exist in these case notes?",
                expected_answer=(
                    "The victim was last seen alive at 3 PM but the coroner says death occurred "
                    "at 1 PM — the victim could not have been alive at 3 PM if they died at 1 PM. "
                    "The gunshot at 4 PM is also after the estimated time of death, so if the "
                    "gunshot was the cause of death, the time of death estimate is wrong."
                ),
                explanation="Alive at 3 PM contradicts death at 1 PM on the same day.",
                difficulty=2,
                consistency_checks=[
                    "If the coroner is correct, could the 3 PM sighting be accurate?",
                    "What is the minimum number of errors in the case notes?",
                ],
            ),
            # --- Scheduling and time zones ---
            ProbeItem(
                id="temporal-011",
                domain=self.domain,
                category="scheduling",
                setup=(
                    "A meeting is scheduled for 3 PM Eastern Time. "
                    "Participant A is in New York (Eastern). "
                    "Participant B is in Chicago (Central, 1 hour behind Eastern). "
                    "Participant C is in London (GMT, 5 hours ahead of Eastern)."
                ),
                question="What local time is the meeting for each participant?",
                expected_answer=(
                    "Participant A (New York): 3 PM. "
                    "Participant B (Chicago): 2 PM. "
                    "Participant C (London): 8 PM."
                ),
                explanation="Central is ET-1, GMT is ET+5.",
                difficulty=2,
                consistency_checks=[
                    "If the meeting runs 2 hours, what time does it end for Participant C?",
                    "Who has the earliest local time for the meeting?",
                ],
            ),
            ProbeItem(
                id="temporal-012",
                domain=self.domain,
                category="scheduling",
                setup=(
                    "It is Monday 11 PM in Tokyo (GMT+9)."
                ),
                question="What day and time is it in New York (GMT-5)?",
                expected_answer=(
                    "Monday 9 AM in New York. Tokyo is 14 hours ahead of New York. "
                    "Monday 11 PM minus 14 hours is Monday 9 AM."
                ),
                explanation="GMT+9 to GMT-5 is a 14-hour difference. 23:00 - 14 = 9:00 same day.",
                difficulty=3,
                consistency_checks=[
                    "What day and time is it in London (GMT)?",
                    "If someone in Tokyo calls New York at this time, is it a reasonable hour?",
                ],
            ),
            # --- Sequences and patterns ---
            ProbeItem(
                id="temporal-013",
                domain=self.domain,
                category="sequence",
                setup=(
                    "A plant grows 2 cm in the first week, 4 cm in the second week, "
                    "and 8 cm in the third week."
                ),
                question="If the pattern continues, how tall will the plant have grown in total after 5 weeks?",
                expected_answer=(
                    "The growth doubles each week: 2, 4, 8, 16, 32. "
                    "Total growth: 2 + 4 + 8 + 16 + 32 = 62 cm."
                ),
                explanation="Geometric sequence with ratio 2. Sum = 2(2^5 - 1)/(2-1) = 62.",
                difficulty=2,
                consistency_checks=[
                    "How much does the plant grow in just the 5th week?",
                    "After how many weeks does total growth exceed 100 cm?",
                ],
            ),
            ProbeItem(
                id="temporal-014",
                domain=self.domain,
                category="sequence",
                setup=(
                    "A medication is taken every 8 hours starting at 6 AM on Monday."
                ),
                question="When is the 7th dose taken?",
                expected_answer=(
                    "The 7th dose is at 6 AM + (6 x 8) hours = 6 AM + 48 hours = "
                    "6 AM on Wednesday."
                ),
                explanation="Doses at 6AM, 2PM, 10PM Mon; 6AM, 2PM, 10PM Tue; 6AM Wed (7th).",
                difficulty=2,
                consistency_checks=[
                    "How many doses are taken on Monday?",
                    "What time is the 4th dose?",
                ],
            ),
            ProbeItem(
                id="temporal-015",
                domain=self.domain,
                category="paradox",
                setup=(
                    "Consider a grandfather paradox scenario: A time traveler goes back in time "
                    "and prevents their own grandfather from meeting their grandmother."
                ),
                question=(
                    "Set aside the physical possibility. Just logically: if the time traveler "
                    "succeeds, can they have existed to make the trip? What is the logical structure "
                    "of this paradox?"
                ),
                expected_answer=(
                    "This is a causal loop paradox. If the traveler succeeds, they were never born, "
                    "so they could not have traveled back, so their grandfather would have met their "
                    "grandmother, so the traveler would be born and travel back — creating an "
                    "irresolvable logical contradiction. The paradox has the structure of a "
                    "self-referential negation."
                ),
                explanation="Classic logical paradox demonstrating temporal consistency requirements.",
                difficulty=4,
                consistency_checks=[
                    "Does the Novikov self-consistency principle resolve this paradox?",
                    "How does the many-worlds interpretation handle this?",
                ],
            ),
        ]
