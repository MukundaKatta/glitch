"""Spatial reasoning glitch probes.

Tests whether LLMs maintain consistent spatial representations across
transitive relations, container logic, rotations, and perspective shifts.
"""

from __future__ import annotations

from glitch.probes import BaseProbe, ProbeDomain, ProbeItem


class SpatialProbe(BaseProbe):
    """Probes for spatial reasoning consistency."""

    domain = ProbeDomain.SPATIAL

    def get_probes(self) -> list[ProbeItem]:
        return [
            # --- Transitive spatial relations ---
            ProbeItem(
                id="spatial-001",
                domain=self.domain,
                category="transitive_relation",
                setup=(
                    "Consider three objects arranged in a line from left to right. "
                    "Object A is to the left of Object B. Object B is to the left of Object C."
                ),
                question="Is Object A to the left of Object C?",
                expected_answer="Yes, Object A is to the left of Object C.",
                explanation="Left-of is transitive: A left-of B and B left-of C implies A left-of C.",
                difficulty=1,
                consistency_checks=[
                    "Is Object C to the right of Object A?",
                    "Which object is in the middle?",
                    "If you face Object C, which direction is Object A?",
                ],
            ),
            ProbeItem(
                id="spatial-002",
                domain=self.domain,
                category="transitive_relation",
                setup=(
                    "In a vertical stack, Block D is above Block E. Block E is above Block F. "
                    "Block F is above Block G."
                ),
                question="How many blocks are between Block D and Block G?",
                expected_answer="Two blocks (E and F) are between Block D and Block G.",
                explanation="D > E > F > G, so E and F are between D and G.",
                difficulty=2,
                consistency_checks=[
                    "Is Block G above Block D?",
                    "Which block is directly below Block D?",
                    "If you remove Block E, which block is now directly below Block D?",
                ],
            ),
            ProbeItem(
                id="spatial-003",
                domain=self.domain,
                category="transitive_relation",
                setup=(
                    "Five people stand in a line. Alice is to the right of Bob. "
                    "Carol is to the right of Alice. Dave is to the left of Bob. "
                    "Eve is between Alice and Carol."
                ),
                question="List all five people in order from left to right.",
                expected_answer="Dave, Bob, Alice, Eve, Carol.",
                explanation=(
                    "Dave < Bob < Alice, Eve is between Alice and Carol, "
                    "Carol is right of Alice, so: Dave, Bob, Alice, Eve, Carol."
                ),
                difficulty=3,
                consistency_checks=[
                    "Who is the second person from the right?",
                    "How many people are to the left of Eve?",
                    "Is Dave to the left of Carol?",
                ],
            ),
            # --- Container logic ---
            ProbeItem(
                id="spatial-004",
                domain=self.domain,
                category="container_logic",
                setup=(
                    "A marble is inside a small box. The small box is inside a large box. "
                    "The large box is inside a closet."
                ),
                question="Is the marble inside the closet?",
                expected_answer="Yes, the marble is inside the closet.",
                explanation="Containment is transitive: marble in small box, small box in large box, large box in closet.",
                difficulty=1,
                consistency_checks=[
                    "If you open the closet but not the large box, can you see the marble?",
                    "If you take the small box out of the large box, is the marble still in the closet?",
                    "How many containers is the marble inside of?",
                ],
            ),
            ProbeItem(
                id="spatial-005",
                domain=self.domain,
                category="container_logic",
                setup=(
                    "Room A contains Box 1 and Box 2. Box 1 contains a red ball. "
                    "Box 2 contains a blue ball. You move Box 1 from Room A to Room B."
                ),
                question="Is the red ball still in Room A?",
                expected_answer="No, the red ball is now in Room B (inside Box 1).",
                explanation="Moving the container moves its contents.",
                difficulty=2,
                consistency_checks=[
                    "Where is the blue ball?",
                    "How many balls are in Room A?",
                    "If you open Box 1 in Room B, what do you find?",
                ],
            ),
            ProbeItem(
                id="spatial-006",
                domain=self.domain,
                category="container_logic",
                setup=(
                    "A Russian nesting doll has 5 layers. The outermost is red, "
                    "then blue, then green, then yellow, and the innermost is white. "
                    "You remove the blue layer."
                ),
                question=(
                    "After removing the blue doll, what is directly inside the red doll?"
                ),
                expected_answer="The green doll is now directly inside the red doll.",
                explanation="Removing blue means green (the next layer) is exposed inside red.",
                difficulty=3,
                consistency_checks=[
                    "How many layers remain in the nesting doll?",
                    "Is the yellow doll still inside the green doll?",
                    "What is the outermost layer?",
                ],
            ),
            # --- Spatial transformations and rotations ---
            ProbeItem(
                id="spatial-007",
                domain=self.domain,
                category="rotation",
                setup=(
                    "You are facing north. A tree is directly to your right."
                ),
                question="In which compass direction is the tree?",
                expected_answer="The tree is to the east.",
                explanation="When facing north, right is east.",
                difficulty=1,
                consistency_checks=[
                    "If you turn to face the tree, which direction are you now facing?",
                    "After turning to face the tree, what is now to your left?",
                ],
            ),
            ProbeItem(
                id="spatial-008",
                domain=self.domain,
                category="rotation",
                setup=(
                    "You are standing in the center of a room facing a clock on the north wall. "
                    "There is a painting on the east wall, a window on the south wall, "
                    "and a door on the west wall. You turn 180 degrees clockwise."
                ),
                question="What are you now facing, and what is to your left?",
                expected_answer="You are facing the window (south wall). The painting (east wall) is to your left.",
                explanation="180 degrees from north is south. When facing south, your left is east (painting) and your right is west (door).",
                difficulty=3,
                consistency_checks=[
                    "What is behind you now?",
                    "What is to your right?",
                    "If you turn 90 degrees counterclockwise from your current position, what do you face?",
                ],
            ),
            ProbeItem(
                id="spatial-009",
                domain=self.domain,
                category="rotation",
                setup=(
                    "A square piece of paper has the letter 'R' written on it, "
                    "oriented normally (readable). You flip the paper over by rotating "
                    "it around its vertical axis (like turning a page)."
                ),
                question="How does the letter 'R' appear when viewed from the other side?",
                expected_answer="The 'R' appears as a mirror image — reversed left to right (like looking at it in a mirror).",
                explanation="Flipping around the vertical axis reverses left and right but not top and bottom.",
                difficulty=3,
                consistency_checks=[
                    "If you then flip it around the horizontal axis, how does it look?",
                    "If instead you had rotated the original paper 180 degrees in the plane, how would the R look?",
                ],
            ),
            # --- Perspective shifts ---
            ProbeItem(
                id="spatial-010",
                domain=self.domain,
                category="perspective",
                setup=(
                    "Two people sit across from each other at a table. A salt shaker "
                    "is on the left side of the table from Person A's perspective."
                ),
                question="From Person B's perspective, which side of the table is the salt shaker on?",
                expected_answer="From Person B's perspective, the salt shaker is on the right side.",
                explanation="Sitting opposite reverses left and right.",
                difficulty=2,
                consistency_checks=[
                    "If Person A reaches for the salt with their left hand, which side does Person B see them reaching?",
                    "If a third person stands at the head of the table, which side do they see the salt on?",
                ],
            ),
            ProbeItem(
                id="spatial-011",
                domain=self.domain,
                category="perspective",
                setup=(
                    "You are looking at a building from the front. The main entrance is on your left. "
                    "You walk around to look at the building from the back."
                ),
                question="Looking at the back of the building, which side is the main entrance on?",
                expected_answer="The main entrance is now on your right side.",
                explanation="Walking around reverses left-right orientation relative to the viewer.",
                difficulty=2,
                consistency_checks=[
                    "If you go back to the front, is the entrance on the left again?",
                    "Looking at the building from the right side, where is the entrance relative to you?",
                ],
            ),
            # --- Distance and scale ---
            ProbeItem(
                id="spatial-012",
                domain=self.domain,
                category="distance",
                setup=(
                    "City A is 100 km north of City B. City C is 100 km east of City B."
                ),
                question="Approximately how far is City A from City C?",
                expected_answer="Approximately 141 km (the diagonal of a right triangle with legs of 100 km each, i.e. 100 * sqrt(2)).",
                explanation="Pythagorean theorem: sqrt(100^2 + 100^2) = 141.4 km.",
                difficulty=2,
                consistency_checks=[
                    "Is City A closer to City B or to City C?",
                    "In which direction would you travel to go directly from City A to City C?",
                ],
            ),
            ProbeItem(
                id="spatial-013",
                domain=self.domain,
                category="distance",
                setup=(
                    "You walk 3 blocks north, then 4 blocks east."
                ),
                question="How far are you from your starting point in a straight line?",
                expected_answer="5 blocks (3-4-5 right triangle).",
                explanation="Pythagorean theorem: sqrt(9 + 16) = 5.",
                difficulty=2,
                consistency_checks=[
                    "In which general direction is your starting point from where you are now?",
                    "If you then walk 5 blocks in a straight line back to start, which direction do you walk?",
                ],
            ),
            # --- Spatial impossibilities ---
            ProbeItem(
                id="spatial-014",
                domain=self.domain,
                category="impossibility",
                setup=(
                    "Object X is directly north of Object Y. Object Y is directly "
                    "north of Object Z. Object Z is directly north of Object X."
                ),
                question="Is this spatial arrangement possible? Explain.",
                expected_answer=(
                    "No, this is impossible. If X is north of Y and Y is north of Z, "
                    "then X must be north of Z, but we are told Z is north of X — a contradiction."
                ),
                explanation="Transitivity of 'north of' makes a cycle impossible on a flat surface.",
                difficulty=3,
                consistency_checks=[
                    "Could this arrangement work on the surface of a sphere?",
                    "What if we relaxed 'directly north' to 'generally north'?",
                ],
            ),
            ProbeItem(
                id="spatial-015",
                domain=self.domain,
                category="impossibility",
                setup=(
                    "A room has four walls. The north wall is 10 meters long. The south wall "
                    "is 10 meters long. The east wall is 8 meters long. The west wall is 12 meters long."
                ),
                question="Is this room geometry possible for a rectangular room? Explain.",
                expected_answer=(
                    "No. In a rectangular room, opposite walls must be the same length. "
                    "The east wall (8 m) and west wall (12 m) are opposite walls with different lengths, "
                    "which is impossible for a rectangle."
                ),
                explanation="Opposite walls of a rectangle are equal in length.",
                difficulty=2,
                consistency_checks=[
                    "What shape could have these wall lengths?",
                    "If the room is rectangular, what must the east wall length be?",
                ],
            ),
        ]
