"""Command line interface replicating the Solvuria workflow."""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
import urllib.error
import urllib.request
from typing import Iterable, Mapping, Optional

from .api import TassomaiClient
from .config import resolve_config
from .spinner import spinner
from .timing import TimingSettings, choose_timing_settings
from .utils import ApiResponseError, AuthenticationError, determine_answer, masked_input, random_user_agent

VERSION = 150


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mario - Enhance your learning experience!")
    parser.add_argument("--config", help="Path to configuration file", default=None)
    parser.add_argument("--subject", help="Subject identifier to auto select", default=None)
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
    return input("[>] Enter your email for signing into tassomai: ")


def fetch_latest_version() -> Optional[int]:
    request = urllib.request.Request(
        "https://api.github.com/repos/corey-truscott/Solvuria/releases/latest",
        headers={"Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf8"))
    except (urllib.error.URLError, ValueError):
        return None
    tag = str(payload.get("tag_name", ""))
    digits = tag.replace("v", "").replace(".", "")
    return int(digits) if digits.isdigit() else None


def present_intro() -> None:
    print("[>] Solvuria - Enhance your learning experience!")
    print("[+] Improvements and fixes contributed by Fonch")
    latest = fetch_latest_version()
    if latest and latest > VERSION:
        print(
            "[+] Newer release of solvuria is available on github: v"
            + ".".join(list(str(latest)))
            + " > v"
            + ".".join(list(str(VERSION)))
            + "\n    Proceeding regardless may result in bans\n"
        )
    print("[~] https://github.com/corey-truscott/Solvuria\n    " + ("-" * 42 + "\n"))


def prompt_subject(subjects: Iterable[Mapping[str, object]]) -> Mapping[str, object]:
    subjects = list(subjects)
    if not subjects:
        raise RuntimeError("No subjects available")
    if len(subjects) == 1:
        subject = subjects[0]
        print(f"[>] Selected {subject.get('name', '').lower()} as it is the only available subject!")
        return subject
    for idx, subject in enumerate(subjects, start=1):
        print(f"[{idx}] Found subject with name: {subject.get('name', '')}")
    while True:
        try:
            choice = int(input("[>] Enter the number next to the subject which you would like to do: ")) - 1
        except ValueError:
            print("[-] Please enter a valid number")
            continue
        if 0 <= choice < len(subjects):
            subject = subjects[choice]
            print(f"[>] Selected {subject.get('name', '').lower()}!")
            return subject
        print("[-] Invalid selection")


def sleep_with_spinner(seconds: float, message: str) -> None:
    seconds = max(0.0, float(seconds))
    end = time.time() + seconds
    with spinner(message):
        while time.time() < end:
            time.sleep(0.1)


def ensure_percentage(value: int) -> int:
    try:
        percentage = int(value)
    except ValueError:
        return 80 + random.randint(0, 5)
    if 0 <= percentage <= 100:
        return percentage
    return 80 + random.randint(0, 5)


def run_quiz(client: TassomaiClient, quiz: Mapping[str, object], settings: TimingSettings) -> bool:
    course_id = quiz.get("courseId") or quiz.get("course")
    playlist_id = quiz.get("playlistId") or quiz.get("playlist")
    if not course_id or not playlist_id:
        print("[-] Quiz metadata missing course/playlist identifiers")
        return False

    delay = random.uniform(*settings.quiz_delay)
    sleep_with_spinner(delay, f"[~] Waiting {delay:.1f}s before starting quiz…")

    with spinner("[~] Fetching quiz…"):
        quiz_data = client.fetch_quiz(str(course_id), str(playlist_id))
    if not quiz_data:
        print("[-] Failed to fetch quiz data. Retrying...")
        return False

    delay = random.uniform(*settings.quiz_delay)
    sleep_with_spinner(delay, f"[~] Waiting {delay:.1f}s before captcha bypass…")
    quiz_data = client.bypass_captcha(quiz_data)

    questions = quiz_data.get("questions")
    if not isinstance(questions, list):
        nested_quiz = quiz_data.get("quiz") if isinstance(quiz_data, Mapping) else None
        if isinstance(nested_quiz, Mapping):
            questions = nested_quiz.get("questions")
    if not isinstance(questions, list):
        print("[-] Could not locate questions in quiz data. Retrying...")
        return False

    print(f"[>] Solving {len(questions)} questions...\n")
    for entry in questions:
        if not isinstance(entry, Mapping):
            continue
        asking_id = entry.get("asking_id") or entry.get("question_id") or entry.get("id")
        answers = entry.get("answers")
        if not asking_id or not isinstance(answers, list):
            print("[-] Skipping malformed question")
            continue
        answer_ids = [str(answer.get("id")) for answer in answers if isinstance(answer, Mapping) and answer.get("id")]
        if not answer_ids:
            print("[-] Question missing answer identifiers")
            continue
        answer_id, is_correct = determine_answer(answer_ids, settings.percent_correct)
        time.sleep(settings.next_question_delay())
        if client.post_answer(answer_id=answer_id, asking_id=str(asking_id)):
            status = "correct" if is_correct else "incorrect"
            print(f"[+] Answered question {status}ly, selected answer is ""{answer_id}""")
        else:
            print("[-] Failed to answer question, sleeping 20 seconds!")
            time.sleep(20)

    return True


def run(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    setup_logging(args.log_level)
    present_intro()

    config = resolve_config(args.config)
    client = TassomaiClient(config, user_agent=random_user_agent())

    email = prompt_email()
    password = masked_input("[>] Enter your password: ")

    try:
        with spinner("[~] Signing in…"):
            client.authenticate(email, password)
        with spinner("[~] Updating last login…"):
            client.update_last_login()
        with spinner("[~] Refreshing token…"):
            client.refresh_token()
    except AuthenticationError as exc:
        print(f"[-] Authentication failed: {exc}")
        time.sleep(5)
        return 1
    except ApiResponseError as exc:
        print(f"[-] API error during sign-in: {exc}")
        time.sleep(5)
        return 1

    subjects = list(client.get_subjects())
    if not subjects:
        print("[-] No subjects returned by Tassomai")
        return 1

    if args.subject:
        subject = next((s for s in subjects if str(s.get("id")) == args.subject), subjects[0])
        print(f"[>] Selected {subject.get('name', '').lower()} via command line argument")
    else:
        subject = prompt_subject(subjects)

    settings = choose_timing_settings()
    settings.percent_correct = ensure_percentage(settings.percent_correct)
    if settings.stop_after_seconds:
        settings.stop_after_seconds += random.randint(0, 19)

    start_time = time.time()

    while True:
        quizzes = client.get_quizzes(str(subject.get("id")))
        if not quizzes:
            print("[-] No quizzes returned. Will retry in 10 seconds...")
            time.sleep(10)
            continue

        quiz_to_run = None
        for quiz in quizzes:
            if isinstance(quiz, Mapping) and quiz.get("type") == "normal":
                quiz_to_run = quiz
                break
        if not quiz_to_run:
            print("[-] Could not find any 'normal' quizzes to complete! Retrying in 60 seconds...")
            time.sleep(60)
            continue

        print(
            f"\n[>] Completing quiz on \"{quiz_to_run.get('playlistName', 'unknown')}\" "
            f"({quiz_to_run.get('courseId')}-{quiz_to_run.get('playlistId')})"
        )

        if not run_quiz(client, quiz_to_run, settings):
            sleep_with_spinner(10, "[~] Retrying in 10s…")
            continue

        if settings.stop_after_seconds and time.time() - start_time > settings.stop_after_seconds:
            minutes = int(settings.stop_after_seconds / 60)
            print(f"[!] The program will now close as {minutes} minute(s) have passed!")
            break

        if args.once:
            break

    time.sleep(5)
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
