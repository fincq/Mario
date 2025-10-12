"""Timing helpers for realistic quiz automation behavior."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class TimingSettings:
    min_step: float
    max_step: float
    min_cycle: float
    max_cycle: float
    percent_correct: int
    stop_after_seconds: int

    @property
    def question_delay(self) -> tuple[float, float]:
        return (self.min_step, self.max_step)

    @property
    def quiz_delay(self) -> tuple[float, float]:
        return (self.min_cycle / 3.0, self.max_cycle / 3.0)

    def next_question_delay(self) -> float:
        return random.uniform(*self.question_delay)

    def next_quiz_delay(self) -> float:
        return random.uniform(*self.quiz_delay)


NORMAL_SETTINGS = TimingSettings(
    min_step=0.5,
    max_step=1.0,
    min_cycle=1.5,
    max_cycle=3.0,
    percent_correct=80,
    stop_after_seconds=0,
)

FAST_SETTINGS = TimingSettings(
    min_step=0.1,
    max_step=0.2,
    min_cycle=0.5,
    max_cycle=1.0,
    percent_correct=100,
    stop_after_seconds=0,
)


def choose_timing_settings() -> TimingSettings:
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ TIMING PROFILE SELECTION                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
  [1] NORMAL - Balanced delays
  [2] FAST   - Minimal delays  
  [3] CUSTOM - Custom timings
┌─────────────────────────────────────────────────────────────────────────────┐""")

    choice = input("Enter choice (1, 2, or 3): ").strip()
    if choice:
        choice = choice[0]

    if choice == "1":
        print("""└─────────────────────────────────────────────────────────────────────────────┘
Selected: NORMAL""")
        return NORMAL_SETTINGS

    if choice == "2":
        print("""└─────────────────────────────────────────────────────────────────────────────┘
Selected: FAST""")
        return FAST_SETTINGS

    if choice == "3":
        print("""└─────────────────────────────────────────────────────────────────────────────┘
CUSTOM TIMING CONFIGURATION
┌─────────────────────────────────────────────────────────────────────────────┐""")
        min_step = float(input("Min delay between questions (sec): "))
        max_step = float(input("Max delay between questions (sec): "))
        min_cycle = float(input("Min delay between quizzes (sec): "))
        max_cycle = float(input("Max delay between quizzes (sec): "))
        percent_correct = int(input("Accuracy percentage (0–100): "))
        print("Note: Mario runs continuously until manually stopped (Ctrl+C)")
        stop_after_minutes = 0  # Always set to infinite
        if min_step > max_step:
            min_step, max_step = max_step, min_step
        if min_cycle > max_cycle:
            min_cycle, max_cycle = max_cycle, min_cycle
        print("[+] Selected profile: Custom")
        return TimingSettings(
            min_step=min_step,
            max_step=max_step,
            min_cycle=min_cycle,
            max_cycle=max_cycle,
            percent_correct=percent_correct,
            stop_after_seconds=stop_after_minutes * 60,
        )

    print("[-] Invalid choice. Defaulting to Normal.")
    return NORMAL_SETTINGS


