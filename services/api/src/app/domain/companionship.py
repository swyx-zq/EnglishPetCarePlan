"""Pure, server-owned companionship state rules.

This module deliberately contains no HTTP, persistence, authentication, or client
time concerns. API and worker adapters must supply an authenticated pet aggregate,
an idempotency store scoped to the authenticated user, and a server clock.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from hashlib import sha256
from threading import Lock
from typing import Protocol
from uuid import UUID

REMINDER_AFTER = timedelta(hours=36)
RESTING_AFTER = timedelta(hours=72)
MAX_IDEMPOTENCY_KEY_LENGTH = 255


class Clock(Protocol):
    """A server-clock boundary that tests and workers can replace."""

    def now(self) -> datetime:
        """Return the current server time as a timezone-aware instant."""


class SystemClock:
    """Default production clock; callers should inject a fixed clock in tests."""

    def now(self) -> datetime:
        return datetime.now(UTC)


class CompanionshipStatus(StrEnum):
    NORMAL = "normal"
    REMINDER = "reminder"
    RESTING = "resting"


class CompanionshipAction(StrEnum):
    FEED = "feed"
    WATER = "water"
    TIDY = "tidy"
    REUNION = "reunion"

    @property
    def is_basic_care(self) -> bool:
        return self in {
            CompanionshipAction.FEED,
            CompanionshipAction.WATER,
            CompanionshipAction.TIDY,
        }


class CompanionshipErrorCode(StrEnum):
    ACTION_NOT_ALLOWED = "companionship_action_not_allowed"
    IDEMPOTENCY_KEY_REUSED = "idempotency_key_reused"
    INVALID_TIMESTAMP = "invalid_companionship_timestamp"
    PET_MISMATCH = "companionship_pet_mismatch"
    INVALID_IDEMPOTENCY_KEY = "invalid_idempotency_key"
    INVALID_STATE = "invalid_companionship_state"


class CompanionshipDomainError(Exception):
    """Base error that future API adapters can map to a stable public code."""

    code: CompanionshipErrorCode

    def __init__(self, code: CompanionshipErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ActionNotAllowedError(CompanionshipDomainError):
    def __init__(
        self,
        *,
        action: CompanionshipAction,
        status: CompanionshipStatus,
    ) -> None:
        allowed = (
            CompanionshipAction.REUNION.value
            if status is CompanionshipStatus.RESTING
            else "feed, water, tidy"
        )
        super().__init__(
            CompanionshipErrorCode.ACTION_NOT_ALLOWED,
            f"Action '{action.value}' is not allowed while the pet is '{status.value}'. "
            f"Allowed action(s): {allowed}.",
        )
        self.action = action
        self.status = status


class IdempotencyConflictError(CompanionshipDomainError):
    def __init__(self, idempotency_key: str) -> None:
        super().__init__(
            CompanionshipErrorCode.IDEMPOTENCY_KEY_REUSED,
            "The idempotency key was already used with a different companionship command.",
        )
        self.idempotency_key = idempotency_key


class InvalidTimestampError(CompanionshipDomainError):
    def __init__(self, message: str) -> None:
        super().__init__(CompanionshipErrorCode.INVALID_TIMESTAMP, message)


class PetMismatchError(CompanionshipDomainError):
    def __init__(self) -> None:
        super().__init__(
            CompanionshipErrorCode.PET_MISMATCH,
            "The companionship command does not target the supplied pet state.",
        )


class InvalidIdempotencyKeyError(CompanionshipDomainError):
    def __init__(self) -> None:
        super().__init__(
            CompanionshipErrorCode.INVALID_IDEMPOTENCY_KEY,
            "The idempotency key must contain between 1 and 255 non-whitespace characters.",
        )


class InvalidCompanionshipStateError(CompanionshipDomainError):
    def __init__(self, message: str) -> None:
        super().__init__(CompanionshipErrorCode.INVALID_STATE, message)


@dataclass(frozen=True, slots=True)
class PetCompanionshipState:
    """Persistable state required to settle a single pet's companionship status."""

    pet_id: UUID
    adopted_at: datetime
    last_companionship_at: datetime
    status: CompanionshipStatus

    def __post_init__(self) -> None:
        adopted_at = _as_utc(self.adopted_at, "adopted_at")
        last_companionship_at = _as_utc(
            self.last_companionship_at,
            "last_companionship_at",
        )
        if last_companionship_at < adopted_at:
            raise InvalidCompanionshipStateError(
                "last_companionship_at cannot be earlier than adopted_at.",
            )

        object.__setattr__(self, "adopted_at", adopted_at)
        object.__setattr__(self, "last_companionship_at", last_companionship_at)


@dataclass(frozen=True, slots=True)
class StatusTransition:
    from_status: CompanionshipStatus
    to_status: CompanionshipStatus
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class Settlement:
    state: PetCompanionshipState
    transitions: tuple[StatusTransition, ...]


@dataclass(frozen=True, slots=True)
class CompanionshipCommand:
    """A write command whose key must be scoped by the caller in persistence."""

    pet_id: UUID
    action: CompanionshipAction
    idempotency_key: str

    def __post_init__(self) -> None:
        if (
            not self.idempotency_key.strip()
            or len(self.idempotency_key) > MAX_IDEMPOTENCY_KEY_LENGTH
        ):
            raise InvalidIdempotencyKeyError()

    @property
    def fingerprint(self) -> str:
        """Stable payload identity used to reject key reuse with another command."""

        payload = f"{self.pet_id}:{self.action.value}".encode()
        return sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class InteractionResult:
    action: CompanionshipAction
    occurred_at: datetime
    previous_status: CompanionshipStatus
    settlement: Settlement
    state: PetCompanionshipState


class IdempotencyStore(Protocol):
    """Persistence adapter for idempotent companionship commands.

    A database implementation must execute this atomically with the aggregate write.
    The in-memory version exists only for pure-domain tests.
    """

    def execute(
        self,
        *,
        idempotency_key: str,
        fingerprint: str,
        operation: Callable[[], InteractionResult],
    ) -> InteractionResult:
        """Replay the recorded outcome or execute and record the first outcome."""


@dataclass(frozen=True, slots=True)
class _StoredOutcome:
    fingerprint: str
    result: InteractionResult | None = None
    error: CompanionshipDomainError | None = None


class InMemoryIdempotencyStore:
    """Thread-safe test implementation; never use as a production source of truth."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._outcomes: dict[str, _StoredOutcome] = {}

    def execute(
        self,
        *,
        idempotency_key: str,
        fingerprint: str,
        operation: Callable[[], InteractionResult],
    ) -> InteractionResult:
        with self._lock:
            stored = self._outcomes.get(idempotency_key)
            if stored is not None:
                if stored.fingerprint != fingerprint:
                    raise IdempotencyConflictError(idempotency_key)
                if stored.error is not None:
                    raise stored.error
                if stored.result is None:
                    raise InvalidCompanionshipStateError(
                        "Stored idempotency outcome did not contain a result or error.",
                    )
                return stored.result

            try:
                result = operation()
            except CompanionshipDomainError as error:
                self._outcomes[idempotency_key] = _StoredOutcome(
                    fingerprint=fingerprint,
                    error=error,
                )
                raise

            self._outcomes[idempotency_key] = _StoredOutcome(
                fingerprint=fingerprint,
                result=result,
            )
            return result


class CompanionshipService:
    """Handles state settlement and the allowed free companionship interactions."""

    def __init__(self, *, clock: Clock, idempotency_store: IdempotencyStore) -> None:
        self._clock = clock
        self._idempotency_store = idempotency_store

    def handle(
        self,
        state: PetCompanionshipState,
        command: CompanionshipCommand,
    ) -> InteractionResult:
        if command.pet_id != state.pet_id:
            raise PetMismatchError()

        return self._idempotency_store.execute(
            idempotency_key=command.idempotency_key,
            fingerprint=command.fingerprint,
            operation=lambda: self._handle_first_attempt(state, command),
        )

    def _handle_first_attempt(
        self,
        state: PetCompanionshipState,
        command: CompanionshipCommand,
    ) -> InteractionResult:
        occurred_at = _as_utc(self._clock.now(), "clock.now()")
        settlement = settle_companionship(state, occurred_at)
        current_state = settlement.state

        if command.action.is_basic_care:
            if current_state.status is CompanionshipStatus.RESTING:
                raise ActionNotAllowedError(
                    action=command.action,
                    status=current_state.status,
                )
        elif current_state.status is not CompanionshipStatus.RESTING:
            raise ActionNotAllowedError(
                action=command.action,
                status=current_state.status,
            )

        next_state = replace(
            current_state,
            last_companionship_at=occurred_at,
            status=CompanionshipStatus.NORMAL,
        )
        return InteractionResult(
            action=command.action,
            occurred_at=occurred_at,
            previous_status=current_state.status,
            settlement=settlement,
            state=next_state,
        )


def adopt_pet(*, pet_id: UUID, adopted_at: datetime) -> PetCompanionshipState:
    """Create the first companionship event and its complete 36-hour grace period."""

    adopted_at_utc = _as_utc(adopted_at, "adopted_at")
    return PetCompanionshipState(
        pet_id=pet_id,
        adopted_at=adopted_at_utc,
        last_companionship_at=adopted_at_utc,
        status=CompanionshipStatus.NORMAL,
    )


def companionship_status_at(
    *, last_companionship_at: datetime, now: datetime
) -> CompanionshipStatus:
    """Determine the server-authoritative status without mutating any aggregate."""

    last_event = _as_utc(last_companionship_at, "last_companionship_at")
    current_time = _as_utc(now, "now")
    if current_time < last_event:
        raise InvalidTimestampError("now cannot be earlier than last_companionship_at.")

    elapsed = current_time - last_event
    if elapsed >= RESTING_AFTER:
        return CompanionshipStatus.RESTING
    if elapsed >= REMINDER_AFTER:
        return CompanionshipStatus.REMINDER
    return CompanionshipStatus.NORMAL


def settle_companionship(state: PetCompanionshipState, now: datetime) -> Settlement:
    """Apply elapsed server time and return auditable status transitions.

    Calling this more than once for the same state and time is safe: once the state
    contains the calculated status, no further transition is emitted.
    """

    current_time = _as_utc(now, "now")
    target_status = companionship_status_at(
        last_companionship_at=state.last_companionship_at,
        now=current_time,
    )
    if target_status is state.status:
        return Settlement(state=state, transitions=())

    if _status_rank(target_status) < _status_rank(state.status):
        raise InvalidCompanionshipStateError(
            "A companionship status cannot move backwards without a confirmed interaction.",
        )

    transitions = _transitions_to(
        state=state,
        target_status=target_status,
    )
    return Settlement(
        state=replace(state, status=target_status),
        transitions=transitions,
    )


def _transitions_to(
    *,
    state: PetCompanionshipState,
    target_status: CompanionshipStatus,
) -> tuple[StatusTransition, ...]:
    if state.status is CompanionshipStatus.NORMAL and target_status is CompanionshipStatus.REMINDER:
        return (
            StatusTransition(
                from_status=CompanionshipStatus.NORMAL,
                to_status=CompanionshipStatus.REMINDER,
                occurred_at=state.last_companionship_at + REMINDER_AFTER,
            ),
        )
    if state.status is CompanionshipStatus.NORMAL and target_status is CompanionshipStatus.RESTING:
        reminder_at = state.last_companionship_at + REMINDER_AFTER
        resting_at = state.last_companionship_at + RESTING_AFTER
        return (
            StatusTransition(
                from_status=CompanionshipStatus.NORMAL,
                to_status=CompanionshipStatus.REMINDER,
                occurred_at=reminder_at,
            ),
            StatusTransition(
                from_status=CompanionshipStatus.REMINDER,
                to_status=CompanionshipStatus.RESTING,
                occurred_at=resting_at,
            ),
        )
    if (
        state.status is CompanionshipStatus.REMINDER
        and target_status is CompanionshipStatus.RESTING
    ):
        return (
            StatusTransition(
                from_status=CompanionshipStatus.REMINDER,
                to_status=CompanionshipStatus.RESTING,
                occurred_at=state.last_companionship_at + RESTING_AFTER,
            ),
        )
    raise InvalidCompanionshipStateError(
        "No valid companionship transition exists for the requested state change.",
    )


def _status_rank(status: CompanionshipStatus) -> int:
    return {
        CompanionshipStatus.NORMAL: 0,
        CompanionshipStatus.REMINDER: 1,
        CompanionshipStatus.RESTING: 2,
    }[status]


def _as_utc(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidTimestampError(f"{field_name} must be timezone-aware.")
    return value.astimezone(UTC)
