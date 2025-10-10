"""Command line interface for Mario."""

from __future__ import annotations

import argparse
import logging
import random
import sys
from typing import Iterable, Mapping, Optional

from .api import TassomaiClient
from .config import resolve_config
from .spinner import spinner
from .timing import FAST_PROFILE, NORMAL_PROFILE, STEALTH_PROFILE, TimingProfile, build_custom_profile
from .utils import QuizChoice, QuizQuestion, Subject, masked_input

PROFILE_LOOKUP = {
    "normal": NORMAL_PROFILE,
    "fast": FAST_PROFILE,
    "stealth": STEALTH_PROFILE,
}


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mario - Tassomai automation client")
    parser.add_argument("--config", help="Path to configuration file", default=None)
    parser.add_argument("--subject", help="Subject identifier to auto select", default=None)
    parser.add_argument(
        "--profile",
        choices=list(PROFILE_LOOKUP.keys()),
        help="Timing profile to use",
        default=None,
    )
    parser.add_argument("--once", action="store_true", help="Run a single quiz and exit")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def setup_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level), format="[%(levelname)s] %(message)s")


def prompt_email() -> str:
    return input("Email: ")


def prompt_subject(subjects: Iterable[Subject]) -> Subject:
    subjects = list(subjects)
    print("\nAvailable subjects:")
    print("===================")
    for idx, subject in enumerate(subjects, start=1):
        print(f"{idx:>2}. {subject.id:<15} {subject.name}")
    while True:
        choice = input("Select subject by index: ")
        if not choice.isdigit():
            print("Please enter a number")
            continue
        index = int(choice) - 1
        if 0 <= index < len(subjects):
            return subjects[index]
        print("Invalid selection")


def prompt_timing_profile() -> TimingProfile:
    print("Choose timing profile:")
    print("  [1] Normal")
    print("  [2] Fast")
    print("  [3] Stealth")
    print("  [4] Custom")
    while True:
        choice = input("Selection: ")
        if choice == "1":
            return NORMAL_PROFILE
        if choice == "2":
            return FAST_PROFILE
        if choice == "3":
            return STEALTH_PROFILE
        if choice == "4":
            return prompt_custom_profile()
        print("Invalid selection")


def prompt_custom_profile() -> TimingProfile:
    def ask_range(label: str) -> tuple[float, float]:
        lower = float(input(f"Minimum {label} delay (seconds): "))
        upper = float(input(f"Maximum {label} delay (seconds): "))
        if lower > upper:
            lower, upper = upper, lower
        return lower, upper

    between_questions = ask_range("question")
    between_quizzes = ask_range("quiz")
    mistake_chance = float(input("Chance to intentionally miss an answer (0-1): "))
    return build_custom_profile(between_questions, between_quizzes, mistake_chance)


def choose_answer(question: QuizQuestion, profile: TimingProfile) -> QuizChoice:
    wrong_answers = [choice for choice in question.choices if not choice.is_correct]
    correct_answers = [choice for choice in question.choices if choice.is_correct]
    make_mistake = profile.should_make_mistake() and wrong_answers
    pool = wrong_answers if make_mistake else (correct_answers or wrong_answers)
    if not pool:
        raise RuntimeError("Question did not contain any answer choices")
    return random.choice(pool)


def run_quiz(client: TassomaiClient, quiz_meta: Mapping[str, str], profile: TimingProfile) -> None:
    course_id_value = quiz_meta.get("courseId") or quiz_meta.get("course_id")
    playlist_id_value = quiz_meta.get("playlistId") or quiz_meta.get("playlist_id")
    if not course_id_value or not playlist_id_value:
        print("Quiz metadata missing identifiers")
        return
    course_id = str(course_id_value)
    playlist_id = str(playlist_id_value)
    with spinner("Fetching quiz"):
        quiz = client.fetch_quiz(course_id, playlist_id)
    print(f"Loaded quiz {quiz.id} with {len(quiz.questions)} questions")
    client.bypass_captcha(quiz.id)
    for idx, question in enumerate(quiz.questions, start=1):
        print(f"Question {idx}: {question.prompt}")
        try:
            answer = choose_answer(question, profile)
        except RuntimeError as exc:
            print(str(exc))
            continue
        is_correct = answer.is_correct
        client.post_answer(
            answer_id=answer.id,
            question_id=question.id,
            quiz_id=quiz.id,
            is_correct=is_correct,
        )
        status = "correct" if is_correct else "incorrect"
        print(f"  -> answered {status}")
        profile.sleep_between_questions()
    profile.sleep_between_quizzes()


def run(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    setup_logging(args.log_level)
    config = resolve_config(args.config)
    client = TassomaiClient(config)

    email = prompt_email()
    password = masked_input("Password: ")

    with spinner("Authenticating"):
        client.authenticate(email, password)
        client.refresh_token()
        client.update_last_login()

    subjects = client.get_subjects()
    if not subjects:
        print("No subjects available")
        return 1

    subject: Subject
    if args.subject:
        subject = next((s for s in subjects if s.id == args.subject), subjects[0])
    else:
        subject = prompt_subject(subjects)
    print(f"Using subject {subject.name} ({subject.id})")

    profile = PROFILE_LOOKUP.get(args.profile)
    if not profile:
        profile = prompt_timing_profile()
    print(f"Using profile {profile.name}")

    while True:
        with spinner("Requesting quiz"):
            quiz_meta = client.get_next_quiz(subject.id)
        if not quiz_meta:
            print("No quizzes available, sleeping")
            profile.sleep_between_quizzes()
            continue
        run_quiz(client, quiz_meta, profile)
        if args.once:
            break

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
