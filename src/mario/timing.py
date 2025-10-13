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


HUMAN_LIKE_SETTINGS = TimingSettings(
    min_step=1.5,
    max_step=4.0,
    min_cycle=3.0,
    max_cycle=8.0,
    percent_correct=75,
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


def choose_accuracy() -> int:
    """Prompt user to choose accuracy percentage."""
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ ACCURACY SELECTION                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
Choose your desired accuracy percentage:
  • 100% - Perfect answers (may be detectable)
  • 85-95% - Very high accuracy
  • 70-84% - Good accuracy
  • 50-69% - Average accuracy
  • 1-49% - Low accuracy (slow progress)
┌─────────────────────────────────────────────────────────────────────────────┐""")
    
    while True:
        try:
            accuracy = int(input("Enter accuracy percentage (1-100): ").strip())
            if 1 <= accuracy <= 100:
                print(f"└─────────────────────────────────────────────────────────────────────────────┘\nSelected accuracy: {accuracy}%")
                return accuracy
            else:
                print("Please enter a value between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")


def choose_timing_settings() -> TimingSettings:
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ TIMING PROFILE SELECTION                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
  [1] HUMAN-LIKE - Realistic human timing (1.5-4.0s delays)
  [2] FAST       - Minimal delays (0.1-0.2s delays)
  [3] CUSTOM     - Custom timing settings
┌─────────────────────────────────────────────────────────────────────────────┐""")

    choice = input("Enter choice (1, 2, or 3): ").strip()
    if choice:
        choice = choice[0]

    accuracy = choose_accuracy()

    if choice == "1":
        print("""Selected: HUMAN-LIKE timing""")
        settings = HUMAN_LIKE_SETTINGS
        return TimingSettings(
            min_step=settings.min_step,
            max_step=settings.max_step,
            min_cycle=settings.min_cycle,
            max_cycle=settings.max_cycle,
            percent_correct=accuracy,
            stop_after_seconds=settings.stop_after_seconds,
        )

    if choice == "2":
        print("""Selected: FAST timing""")
        settings = FAST_SETTINGS
        return TimingSettings(
            min_step=settings.min_step,
            max_step=settings.max_step,
            min_cycle=settings.min_cycle,
            max_cycle=settings.max_cycle,
            percent_correct=accuracy,
            stop_after_seconds=settings.stop_after_seconds,
        )

    if choice == "3":
        print("""CUSTOM TIMING CONFIGURATION
┌─────────────────────────────────────────────────────────────────────────────┐""")
        min_step = float(input("Min delay between questions (sec): "))
        max_step = float(input("Max delay between questions (sec): "))
        min_cycle = float(input("Min delay between quizzes (sec): "))
        max_cycle = float(input("Max delay between quizzes (sec): "))
        print("Note: Mario runs continuously until manually stopped (Ctrl+C)")
        stop_after_minutes = 0
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
            percent_correct=accuracy,
            stop_after_seconds=stop_after_minutes * 60,
        )

    print("[-] Invalid choice. Defaulting to Human-like.")
    settings = HUMAN_LIKE_SETTINGS
    return TimingSettings(
        min_step=settings.min_step,
        max_step=settings.max_step,
        min_cycle=settings.min_cycle,
        max_cycle=settings.max_cycle,
        percent_correct=accuracy,
        stop_after_seconds=settings.stop_after_seconds,
    )


