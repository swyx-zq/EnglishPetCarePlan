from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.domain.companionship import (
    ActionNotAllowedError,
    CompanionshipAction,
    CompanionshipCommand,
    CompanionshipErrorCode,
    CompanionshipService,
    CompanionshipStatus,
    IdempotencyConflictError,
    InMemoryIdempotencyStore,
    InvalidTimestampError,
    PetMismatchError,
    adopt_pet,
    companionship_status_at,
    settle_companionship,
)

ADOPTED_AT = datetime(2026, 8, 23, 9, tzinfo=UTC)


@dataclass
class FixedClock:
    current_time: datetime

    def now(self) -> datetime:
        return self.current_time


def service_at(current_time: datetime) -> tuple[CompanionshipService, FixedClock]:
    clock = FixedClock(current_time=current_time)
    service = CompanionshipService(
        clock=clock,
        idempotency_store=InMemoryIdempotencyStore(),
    )
    return service, clock


def command(
    *,
    pet_id: UUID,
    action: CompanionshipAction,
    key: str = "request-1",
) -> CompanionshipCommand:
    return CompanionshipCommand(
        pet_id=pet_id,
        action=action,
        idempotency_key=key,
    )


def test_adoption_creates_the_first_companionship_event_and_grace_period() -> None:
    pet_id = uuid4()

    state = adopt_pet(pet_id=pet_id, adopted_at=ADOPTED_AT)

    assert state.pet_id == pet_id
    assert state.adopted_at == ADOPTED_AT
    assert state.last_companionship_at == ADOPTED_AT
    assert state.status is CompanionshipStatus.NORMAL
    assert (
        companionship_status_at(
            last_companionship_at=state.last_companionship_at,
            now=ADOPTED_AT + timedelta(hours=35, minutes=59, seconds=59),
        )
        is CompanionshipStatus.NORMAL
    )


@pytest.mark.parametrize(
    ("elapsed", "expected_status"),
    [
        (timedelta(hours=36), CompanionshipStatus.REMINDER),
        (timedelta(hours=71, minutes=59, seconds=59), CompanionshipStatus.REMINDER),
        (timedelta(hours=72), CompanionshipStatus.RESTING),
    ],
)
def test_status_thresholds_use_greater_than_or_equal_boundaries(
    elapsed: timedelta,
    expected_status: CompanionshipStatus,
) -> None:
    state = adopt_pet(pet_id=uuid4(), adopted_at=ADOPTED_AT)

    settlement = settle_companionship(state, ADOPTED_AT + elapsed)

    assert settlement.state.status is expected_status


def test_settling_directly_to_resting_records_both_elapsed_transitions() -> None:
    state = adopt_pet(pet_id=uuid4(), adopted_at=ADOPTED_AT)

    settlement = settle_companionship(state, ADOPTED_AT + timedelta(hours=72))

    assert [transition.to_status for transition in settlement.transitions] == [
        CompanionshipStatus.REMINDER,
        CompanionshipStatus.RESTING,
    ]
    assert [transition.occurred_at for transition in settlement.transitions] == [
        ADOPTED_AT + timedelta(hours=36),
        ADOPTED_AT + timedelta(hours=72),
    ]


@pytest.mark.parametrize(
    ("elapsed", "action"),
    [
        (timedelta(hours=1), CompanionshipAction.FEED),
        (timedelta(hours=36), CompanionshipAction.WATER),
        (timedelta(hours=71, minutes=59), CompanionshipAction.TIDY),
    ],
)
def test_basic_care_is_allowed_in_normal_or_reminder_and_refreshes_time(
    elapsed: timedelta,
    action: CompanionshipAction,
) -> None:
    pet_id = uuid4()
    state = adopt_pet(pet_id=pet_id, adopted_at=ADOPTED_AT)
    service, clock = service_at(ADOPTED_AT + elapsed)

    result = service.handle(state, command(pet_id=pet_id, action=action))

    assert result.state.status is CompanionshipStatus.NORMAL
    assert result.state.last_companionship_at == clock.current_time
    assert result.previous_status is (
        CompanionshipStatus.NORMAL
        if elapsed < timedelta(hours=36)
        else CompanionshipStatus.REMINDER
    )


@pytest.mark.parametrize("action", list(CompanionshipAction))
def test_only_reunion_is_allowed_while_resting(action: CompanionshipAction) -> None:
    pet_id = uuid4()
    state = adopt_pet(pet_id=pet_id, adopted_at=ADOPTED_AT)
    service, _ = service_at(ADOPTED_AT + timedelta(hours=72))

    if action is CompanionshipAction.REUNION:
        result = service.handle(state, command(pet_id=pet_id, action=action))
        assert result.previous_status is CompanionshipStatus.RESTING
        assert result.state.status is CompanionshipStatus.NORMAL
    else:
        with pytest.raises(ActionNotAllowedError) as error:
            service.handle(state, command(pet_id=pet_id, action=action))
        assert error.value.code is CompanionshipErrorCode.ACTION_NOT_ALLOWED
        assert error.value.status is CompanionshipStatus.RESTING


@pytest.mark.parametrize(
    "elapsed",
    [timedelta(0), timedelta(hours=36), timedelta(hours=71, minutes=59, seconds=59)],
)
def test_reunion_is_rejected_outside_resting(elapsed: timedelta) -> None:
    pet_id = uuid4()
    state = adopt_pet(pet_id=pet_id, adopted_at=ADOPTED_AT)
    service, _ = service_at(ADOPTED_AT + elapsed)

    with pytest.raises(ActionNotAllowedError) as error:
        service.handle(
            state,
            command(pet_id=pet_id, action=CompanionshipAction.REUNION),
        )

    assert error.value.code is CompanionshipErrorCode.ACTION_NOT_ALLOWED


def test_same_idempotency_key_replays_the_first_successful_result() -> None:
    pet_id = uuid4()
    state = adopt_pet(pet_id=pet_id, adopted_at=ADOPTED_AT)
    service, clock = service_at(ADOPTED_AT + timedelta(hours=1))
    first_command = command(pet_id=pet_id, action=CompanionshipAction.FEED)

    first = service.handle(state, first_command)
    clock.current_time = ADOPTED_AT + timedelta(hours=80)
    replay = service.handle(first.state, first_command)

    assert replay == first
    assert replay.state.last_companionship_at == ADOPTED_AT + timedelta(hours=1)


def test_same_idempotency_key_with_a_different_payload_is_rejected() -> None:
    pet_id = uuid4()
    state = adopt_pet(pet_id=pet_id, adopted_at=ADOPTED_AT)
    service, _ = service_at(ADOPTED_AT + timedelta(hours=1))

    service.handle(state, command(pet_id=pet_id, action=CompanionshipAction.FEED, key="same"))

    with pytest.raises(IdempotencyConflictError) as error:
        service.handle(state, command(pet_id=pet_id, action=CompanionshipAction.WATER, key="same"))

    assert error.value.code is CompanionshipErrorCode.IDEMPOTENCY_KEY_REUSED


def test_same_idempotency_key_replays_the_first_rejection() -> None:
    pet_id = uuid4()
    state = adopt_pet(pet_id=pet_id, adopted_at=ADOPTED_AT)
    service, clock = service_at(ADOPTED_AT)
    reunion = command(pet_id=pet_id, action=CompanionshipAction.REUNION, key="rejected")

    with pytest.raises(ActionNotAllowedError) as first_error:
        service.handle(state, reunion)

    clock.current_time = ADOPTED_AT + timedelta(hours=72)
    with pytest.raises(ActionNotAllowedError) as replay_error:
        service.handle(state, reunion)

    assert replay_error.value is first_error.value
    assert replay_error.value.status is CompanionshipStatus.NORMAL


def test_command_for_a_different_pet_is_rejected_before_any_state_change() -> None:
    state = adopt_pet(pet_id=uuid4(), adopted_at=ADOPTED_AT)
    service, _ = service_at(ADOPTED_AT + timedelta(hours=1))

    with pytest.raises(PetMismatchError) as error:
        service.handle(
            state,
            command(pet_id=uuid4(), action=CompanionshipAction.FEED),
        )

    assert error.value.code is CompanionshipErrorCode.PET_MISMATCH


def test_naive_timestamps_are_rejected() -> None:
    naive_time = datetime(2026, 8, 23, 9)

    with pytest.raises(InvalidTimestampError):
        adopt_pet(pet_id=uuid4(), adopted_at=naive_time)
