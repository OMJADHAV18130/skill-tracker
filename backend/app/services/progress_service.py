"""Progress calculation helpers.

Every number in the application is derived from persisted rows - there are no
hardcoded progress values anywhere.

Rules
-----
* Topic completion   = completed topics / total topics
* Phase completion   = completed topics in phase / total topics in phase
* Overall completion = completed topics / all roadmap topics
* Project completion = completed milestones / total milestones
* Study hours        = sum(study session minutes) / 60
* Streak             = consecutive *active days* (a day with at least one study
                       session or one completed task that logged minutes).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, timedelta

from app.models.roadmap import TopicStatus


def percentage(part: int, total: int) -> float:
    """Safe percentage helper - returns 0.0 for an empty denominator."""
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 2)


@dataclass(slots=True)
class PhaseStats:
    phase_id: str
    key: str
    title: str
    month_label: str
    order_index: int
    total_topics: int = 0
    completed_topics: int = 0
    in_progress_topics: int = 0
    completion_percentage: float = 0.0
    estimated_minutes: int = 0

    @property
    def status(self) -> str:
        if self.total_topics == 0:
            return "not_started"
        if self.completed_topics == self.total_topics:
            return "completed"
        if self.completed_topics or self.in_progress_topics:
            return "in_progress"
        return "not_started"


@dataclass(slots=True)
class RoadmapStats:
    total_topics: int = 0
    completed_topics: int = 0
    in_progress_topics: int = 0
    completion_percentage: float = 0.0
    phases: list[PhaseStats] = field(default_factory=list)

    @property
    def completed_percentage(self) -> float:
        return percentage(self.completed_topics, self.total_topics)


@dataclass(slots=True)
class StreakStats:
    current_streak: int = 0
    longest_streak: int = 0
    total_active_days: int = 0
    last_active_date: date | None = None


def build_roadmap_stats(
    *,
    phases: Iterable,
    topics: Iterable,
    progress_by_topic: dict,
) -> RoadmapStats:
    """Build the aggregate roadmap statistics.

    ``phases``   - sequence of ``RoadmapPhase`` rows
    ``topics``   - sequence of ``Topic`` rows
    ``progress_by_topic`` - mapping of topic id -> ``TopicProgress``
    """
    phase_list = list(phases)
    topic_list = list(topics)

    topics_by_phase: dict = {}
    for topic in topic_list:
        topics_by_phase.setdefault(topic.phase_id, []).append(topic)

    stats = RoadmapStats(total_topics=len(topic_list))
    completed = 0
    in_progress = 0

    for phase in phase_list:
        phase_topics = topics_by_phase.get(phase.id, [])
        phase_stats = PhaseStats(
            phase_id=str(phase.id),
            key=phase.key,
            title=phase.title,
            month_label=phase.month_label,
            order_index=phase.order_index,
            total_topics=len(phase_topics),
        )
        for topic in phase_topics:
            progress = progress_by_topic.get(topic.id)
            status = progress.status if progress else TopicStatus.NOT_STARTED
            if status == TopicStatus.COMPLETED:
                phase_stats.completed_topics += 1
                completed += 1
            elif status == TopicStatus.IN_PROGRESS:
                phase_stats.in_progress_topics += 1
                in_progress += 1
            phase_stats.estimated_minutes += topic.estimated_minutes
        phase_stats.completion_percentage = percentage(
            phase_stats.completed_topics, phase_stats.total_topics
        )
        stats.phases.append(phase_stats)

    stats.completed_topics = completed
    stats.in_progress_topics = in_progress
    stats.completion_percentage = percentage(completed, len(topic_list))
    return stats


def compute_streak(active_dates: set[date], *, today: date | None = None) -> StreakStats:
    """Compute the current and longest streak from a set of active days.

    The current streak counts backwards from today. If today has no activity
    yet, yesterday is used as the anchor so that the streak is not reported as
    zero before the first session of the day.
    """
    today = today or date.today()
    if not active_dates:
        return StreakStats()

    ordered = sorted(active_dates)
    last_active = ordered[-1]

    longest = 1
    run = 1
    for previous, current in zip(ordered, ordered[1:], strict=False):
        if current - previous == timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)

    current_streak = 0
    anchor = today
    if anchor not in active_dates:
        anchor = today - timedelta(days=1)
    while anchor in active_dates:
        current_streak += 1
        anchor -= timedelta(days=1)

    return StreakStats(
        current_streak=current_streak,
        longest_streak=longest,
        total_active_days=len(active_dates),
        last_active_date=last_active,
    )
