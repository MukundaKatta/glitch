"""Physical world model glitch probes.

Tests whether LLMs maintain consistent physical intuitions about
conservation laws, gravity, motion, scale, and material properties.
"""

from __future__ import annotations

from glitch.probes import BaseProbe, ProbeDomain, ProbeItem


class PhysicalProbe(BaseProbe):
    """Probes for physical world model consistency."""

    domain = ProbeDomain.PHYSICAL

    def get_probes(self) -> list[ProbeItem]:
        return [
            # --- Conservation laws ---
            ProbeItem(
                id="physical-001",
                domain=self.domain,
                category="conservation_mass",
                setup=(
                    "You have a sealed container with 1 kg of ice. "
                    "The ice completely melts into water."
                ),
                question="What is the mass of the water in the sealed container?",
                expected_answer="1 kg. Mass is conserved when ice melts into water.",
                explanation="Conservation of mass: phase change does not alter mass.",
                difficulty=1,
                consistency_checks=[
                    "If the water then evaporates into steam (still sealed), what is the mass?",
                    "Does the volume change when ice melts?",
                    "If the container is on a scale, does the reading change during melting?",
                ],
            ),
            ProbeItem(
                id="physical-002",
                domain=self.domain,
                category="conservation_energy",
                setup=(
                    "A ball is dropped from a height of 10 meters in a vacuum (no air resistance). "
                    "It hits the ground and bounces back up."
                ),
                question=(
                    "Can the ball bounce higher than 10 meters? Assume no external energy is added."
                ),
                expected_answer=(
                    "No. The ball cannot bounce higher than 10 meters without external energy input. "
                    "Conservation of energy dictates that the ball can at most return to its original "
                    "height, and in practice it bounces lower due to energy lost as heat and sound."
                ),
                explanation="Conservation of energy: kinetic + potential energy is constant or decreasing.",
                difficulty=1,
                consistency_checks=[
                    "If the ball bounces to exactly 10 meters, what does that imply about the collision?",
                    "Where does the 'lost' energy go in a real bounce?",
                ],
            ),
            ProbeItem(
                id="physical-003",
                domain=self.domain,
                category="conservation_momentum",
                setup=(
                    "A 2 kg ball moving at 3 m/s collides head-on with a stationary 2 kg ball. "
                    "The collision is perfectly elastic."
                ),
                question="What are the velocities of both balls after the collision?",
                expected_answer=(
                    "In a perfectly elastic collision between equal masses where one is stationary, "
                    "the moving ball stops and the stationary ball moves at the original velocity. "
                    "Ball 1: 0 m/s. Ball 2: 3 m/s."
                ),
                explanation="Conservation of momentum and kinetic energy with equal masses.",
                difficulty=2,
                consistency_checks=[
                    "Is total momentum conserved? (Before: 6 kg*m/s, After: 6 kg*m/s?)",
                    "Is total kinetic energy conserved?",
                ],
            ),
            # --- Gravity and motion ---
            ProbeItem(
                id="physical-004",
                domain=self.domain,
                category="gravity",
                setup=(
                    "A feather and a bowling ball are dropped simultaneously "
                    "from the same height in a perfect vacuum."
                ),
                question="Which hits the ground first?",
                expected_answer=(
                    "They hit the ground at the same time. In a vacuum, all objects fall "
                    "at the same rate regardless of mass. Galileo demonstrated this principle."
                ),
                explanation="In vacuum, gravitational acceleration is independent of mass.",
                difficulty=1,
                consistency_checks=[
                    "Would the answer change if we added air resistance?",
                    "Does the bowling ball exert more force on the ground when it lands?",
                ],
            ),
            ProbeItem(
                id="physical-005",
                domain=self.domain,
                category="gravity",
                setup=(
                    "An astronaut on the International Space Station releases a wrench. "
                    "The ISS is orbiting Earth at about 400 km altitude."
                ),
                question="Does the wrench float away or fall to Earth?",
                expected_answer=(
                    "The wrench appears to float near the astronaut. Both the wrench and the "
                    "ISS are in free fall (orbit) together, so there is no relative motion. "
                    "The wrench is actually falling toward Earth at the same rate as the station, "
                    "but its forward velocity keeps it in orbit."
                ),
                explanation="Objects in orbit are in free fall; microgravity is the absence of a support force.",
                difficulty=2,
                consistency_checks=[
                    "Is there gravity on the ISS?",
                    "If the astronaut threw the wrench backward relative to the orbit, what would happen?",
                ],
            ),
            ProbeItem(
                id="physical-006",
                domain=self.domain,
                category="motion",
                setup=(
                    "You are in a car moving at a constant 60 km/h. You throw a ball "
                    "straight up in the air inside the car."
                ),
                question="Where does the ball land — in your hand, in front of you, or behind you?",
                expected_answer=(
                    "The ball lands back in your hand (assuming constant velocity and no air effects "
                    "inside the car). The ball retains the car's forward velocity when thrown."
                ),
                explanation="Galilean relativity: the ball shares the car's inertial frame.",
                difficulty=2,
                consistency_checks=[
                    "What if the car suddenly brakes while the ball is in the air?",
                    "Would an observer outside the car see the ball go straight up?",
                ],
            ),
            # --- Scale reasoning ---
            ProbeItem(
                id="physical-007",
                domain=self.domain,
                category="scale",
                setup=(
                    "An ant can carry 50 times its own body weight. "
                    "An ant weighs about 1 mg."
                ),
                question=(
                    "If you scaled an ant up to human size (say 70 kg), "
                    "could it carry 50 times 70 kg = 3,500 kg?"
                ),
                expected_answer=(
                    "No. The square-cube law prevents this. When you scale up an organism, "
                    "its volume (and mass) grows with the cube of the scaling factor, but the "
                    "cross-sectional area of its muscles (which determines strength) only grows "
                    "with the square. A human-sized ant would be crushed under its own weight."
                ),
                explanation="Square-cube law: strength scales as L^2 but weight as L^3.",
                difficulty=3,
                consistency_checks=[
                    "Why can small animals survive falls that would kill large ones?",
                    "Does the square-cube law apply to buildings and bridges too?",
                ],
            ),
            ProbeItem(
                id="physical-008",
                domain=self.domain,
                category="scale",
                setup=(
                    "A flea can jump 150 times its own body length. "
                    "A flea is about 2 mm long."
                ),
                question="If a human could jump 150 times their body length, how far could they jump?",
                expected_answer=(
                    "Numerically, 150 x 1.7 m = 255 m, but this is physically impossible for "
                    "the same square-cube law reason. Larger animals cannot jump proportionally "
                    "as far as smaller ones because muscle power scales with cross-section (L^2) "
                    "while body mass scales with volume (L^3)."
                ),
                explanation="While the arithmetic gives 255 m, the physics prevents proportional scaling.",
                difficulty=3,
                consistency_checks=[
                    "Do larger animals generally jump farther in absolute terms or relative terms?",
                    "Why does the scaling break down?",
                ],
            ),
            # --- Material properties ---
            ProbeItem(
                id="physical-009",
                domain=self.domain,
                category="material",
                setup=(
                    "You place a steel ball and a wooden ball of the same size into a pool of water."
                ),
                question="Which ball sinks and which floats?",
                expected_answer=(
                    "The steel ball sinks (steel density ~7,800 kg/m^3 > water 1,000 kg/m^3). "
                    "The wooden ball floats (most wood density ~500 kg/m^3 < water 1,000 kg/m^3)."
                ),
                explanation="Objects denser than water sink; less dense objects float.",
                difficulty=1,
                consistency_checks=[
                    "If the steel ball were hollow, could it float?",
                    "Would the answer change in saltwater?",
                    "A steel ship floats — how is that possible given steel is denser than water?",
                ],
            ),
            ProbeItem(
                id="physical-010",
                domain=self.domain,
                category="material",
                setup=(
                    "You have two cups of water, both at 50 degrees Celsius. "
                    "You pour them into one large container."
                ),
                question="What is the temperature of the combined water?",
                expected_answer=(
                    "50 degrees Celsius. Combining equal-temperature liquids does not "
                    "change the temperature — it only changes the volume."
                ),
                explanation="Temperature is an intensive property, not additive like mass or volume.",
                difficulty=1,
                consistency_checks=[
                    "If one cup were 40C and the other 60C, what would the mix be?",
                    "Does the total amount of thermal energy double?",
                ],
            ),
            # --- Thermodynamics ---
            ProbeItem(
                id="physical-011",
                domain=self.domain,
                category="thermodynamics",
                setup=(
                    "A perfectly insulated room contains only a running refrigerator "
                    "with its door open."
                ),
                question="Does the room get cooler, warmer, or stay the same temperature?",
                expected_answer=(
                    "The room gets warmer. A refrigerator moves heat from inside to outside "
                    "itself, but the motor also generates waste heat. In a closed system, "
                    "the total entropy increases and the net effect is warming."
                ),
                explanation="Second law of thermodynamics: refrigerator motor adds net heat to the room.",
                difficulty=3,
                consistency_checks=[
                    "Where does the extra heat come from?",
                    "Would a perfectly efficient refrigerator keep the room the same temperature?",
                ],
            ),
            ProbeItem(
                id="physical-012",
                domain=self.domain,
                category="thermodynamics",
                setup=(
                    "A metal spoon and a wooden spoon are both sitting on a kitchen counter "
                    "at room temperature (22 degrees C) for a long time."
                ),
                question="Which spoon is at a higher temperature?",
                expected_answer=(
                    "They are at the same temperature — both at room temperature (22 C). "
                    "The metal spoon feels colder because metal conducts heat away from your "
                    "hand faster, but the actual temperature is identical."
                ),
                explanation="Thermal equilibrium means all objects reach the same temperature. Perceived coldness relates to thermal conductivity, not temperature.",
                difficulty=2,
                consistency_checks=[
                    "Why does the metal spoon feel colder to the touch?",
                    "If you measured both with a thermometer, would the readings differ?",
                ],
            ),
            # --- Relativity and light ---
            ProbeItem(
                id="physical-013",
                domain=self.domain,
                category="relativity",
                setup=(
                    "A spaceship is traveling at 0.9c (90% the speed of light) "
                    "relative to Earth. The pilot turns on headlights."
                ),
                question="How fast does the light from the headlights travel relative to Earth?",
                expected_answer=(
                    "The light travels at c (the speed of light) relative to Earth, not 1.9c. "
                    "According to special relativity, the speed of light is constant in all "
                    "reference frames. Velocities do not add linearly near the speed of light."
                ),
                explanation="Einstein's second postulate: the speed of light is invariant across inertial frames.",
                difficulty=3,
                consistency_checks=[
                    "How fast does the light travel relative to the pilot?",
                    "Does the speed of the ship affect the color of the light seen from Earth?",
                ],
            ),
            # --- Everyday physics ---
            ProbeItem(
                id="physical-014",
                domain=self.domain,
                category="everyday",
                setup=(
                    "You have a helium balloon on a string inside a sealed car. "
                    "The car accelerates forward sharply."
                ),
                question="Which direction does the balloon move — forward, backward, or no movement?",
                expected_answer=(
                    "The balloon moves forward (toward the front of the car). When the car "
                    "accelerates, the denser air is pushed to the back, creating a pressure "
                    "gradient. The lighter helium balloon moves toward the lower-pressure region "
                    "at the front. This is the opposite of what happens to normal objects."
                ),
                explanation="Buoyancy in a non-inertial frame: light objects move opposite to pseudo-forces.",
                difficulty=4,
                consistency_checks=[
                    "What happens to a regular (non-helium) object when the car accelerates?",
                    "Is this related to why hot air rises?",
                ],
            ),
            ProbeItem(
                id="physical-015",
                domain=self.domain,
                category="everyday",
                setup=(
                    "You stand on a bathroom scale inside an elevator. "
                    "The scale normally reads 70 kg when stationary."
                ),
                question=(
                    "What does the scale read when the elevator accelerates upward? "
                    "What about when it moves upward at constant velocity?"
                ),
                expected_answer=(
                    "Accelerating upward: the scale reads MORE than 70 kg (you feel heavier). "
                    "Moving up at constant velocity: the scale reads exactly 70 kg (same as stationary). "
                    "It is the acceleration, not the velocity, that changes apparent weight."
                ),
                explanation="Apparent weight depends on acceleration, not velocity. Newton's second law in a non-inertial frame.",
                difficulty=2,
                consistency_checks=[
                    "What does the scale read if the elevator is in free fall?",
                    "Does moving downward at constant velocity change the reading?",
                ],
            ),
        ]
