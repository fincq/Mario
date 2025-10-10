"""Timing profiles and helpers."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class TimingProfile:
    name: str
    between_questions: Tuple[float, float]
    between_quizzes: Tuple[float, float]
    mistake_chance: float

    def sleep_between_questions(self) -> None:
        time.sleep(random.uniform(*self.between_questions))

    def sleep_between_quizzes(self) -> None:
        time.sleep(random.uniform(*self.between_quizzes))

    def should_make_mistake(self) -> bool:
        return random.random() < self.mistake_chance


NORMAL_PROFILE = TimingProfile(
    name="Normal",
    between_questions=(4.0, 8.0),
    between_quizzes=(15.0, 25.0),
    mistake_chance=0.05,
)

FAST_PROFILE = TimingProfile(
    name="Fast",
    between_questions=(1.5, 3.0),
    between_quizzes=(5.0, 10.0),
    mistake_chance=0.02,
)

STEALTH_PROFILE = TimingProfile(
    name="Stealth",
    between_questions=(7.0, 14.0),
    between_quizzes=(20.0, 45.0),
    mistake_chance=0.08,
)


def iter_profiles() -> Iterable[TimingProfile]:
    yield NORMAL_PROFILE
    yield FAST_PROFILE
    yield STEALTH_PROFILE


def build_custom_profile(
    between_questions: Tuple[float, float],
    between_quizzes: Tuple[float, float],
    mistake_chance: float,
) -> TimingProfile:
    return TimingProfile(
        name="Custom",
        between_questions=between_questions,
        between_quizzes=between_quizzes,
        mistake_chance=mistake_chance,
    )
