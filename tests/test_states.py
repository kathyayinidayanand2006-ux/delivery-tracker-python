import itertools

import pytest

from app import states


def test_all_36_status_pairs_match_transition_table():
    assert len(states.STATUSES) == 6
    for current, target in itertools.product(states.STATUSES, repeat=2):
        expected = target in states.TRANSITIONS[current]
        assert states.can_move(current, target) is expected


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (states.PLACED, states.ACCEPTED),
        (states.PLACED, states.CANCELLED),
        (states.ACCEPTED, states.COOKING),
        (states.ACCEPTED, states.CANCELLED),
        (states.COOKING, states.OUT_FOR_DELIVERY),
        (states.OUT_FOR_DELIVERY, states.DELIVERED),
    ],
)
def test_legal_transitions(current, target):
    assert states.can_move(current, target) is True
    assert states.assert_move(current, target) == target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (states.PLACED, states.COOKING),
        (states.PLACED, states.OUT_FOR_DELIVERY),
        (states.ACCEPTED, states.DELIVERED),
        (states.DELIVERED, states.COOKING),
        (states.CANCELLED, states.ACCEPTED),
        (states.COOKING, states.CANCELLED),
        (states.ACCEPTED, states.PLACED),
        (states.COOKING, states.COOKING),
    ],
)
def test_illegal_transitions(current, target):
    assert states.can_move(current, target) is False
    with pytest.raises(states.TransitionError):
        states.assert_move(current, target)


def test_transition_error_contains_both_statuses():
    with pytest.raises(states.TransitionError) as error:
        states.assert_move(states.PLACED, states.DELIVERED)
    assert states.PLACED in str(error.value)
    assert states.DELIVERED in str(error.value)


def test_repeating_same_status_is_a_conflict():
    with pytest.raises(states.TransitionError) as error:
        states.assert_move(states.COOKING, states.COOKING)
    assert error.value.conflict is True


@pytest.mark.parametrize("status", [states.PLACED, states.ACCEPTED])
def test_orders_can_be_cancelled(status):
    assert states.is_cancellable(status) is True
    assert states.assert_cancel(status) == states.CANCELLED


@pytest.mark.parametrize(
    "status",
    [
        states.COOKING,
        states.OUT_FOR_DELIVERY,
        states.DELIVERED,
        states.CANCELLED,
    ],
)
def test_later_orders_cannot_be_cancelled(status):
    assert states.is_cancellable(status) is False
    with pytest.raises(states.TransitionError):
        states.assert_cancel(status)


def test_cancelling_already_cancelled_order_is_a_conflict():
    with pytest.raises(states.TransitionError) as error:
        states.assert_cancel(states.CANCELLED)
    assert error.value.conflict is True


def test_cooking_to_accepted_is_backwards():
    assert states.is_backwards(states.COOKING, states.ACCEPTED) is True


def test_cooking_to_cancelled_is_illegal_but_not_backwards():
    assert states.is_backwards(states.COOKING, states.CANCELLED) is False
    with pytest.raises(states.TransitionError) as error:
        states.assert_move(states.COOKING, states.CANCELLED)
    assert error.value.conflict is True
    assert "too late to cancel" in str(error.value)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (states.ACCEPTED, states.COOKING),
        (states.COOKING, states.OUT_FOR_DELIVERY),
        (states.OUT_FOR_DELIVERY, states.DELIVERED),
    ],
)
def test_expected_status_allows_valid_update(current, target):
    assert states.apply_update(current, target, expected=current) == target


def test_stale_expected_status_is_a_conflict():
    with pytest.raises(states.TransitionError) as error:
        states.apply_update(
            current=states.COOKING,
            target=states.OUT_FOR_DELIVERY,
            expected=states.ACCEPTED,
        )
    assert error.value.conflict is True
    assert "cooking" in str(error.value)
    assert "accepted" in str(error.value)


def test_update_without_expected_status():
    assert states.apply_update(states.PLACED, states.ACCEPTED) == states.ACCEPTED


def test_invalid_status_is_rejected():
    with pytest.raises(states.TransitionError):
        states.check_status("flying")


def test_status_is_normalized():
    assert states.check_status("  COOKING ") == states.COOKING


@pytest.mark.parametrize(
    ("status", "expected_progress"),
    [
        (states.PLACED, 0.0),
        (states.ACCEPTED, 0.25),
        (states.COOKING, 0.5),
        (states.OUT_FOR_DELIVERY, 0.75),
        (states.DELIVERED, 1.0),
        (states.CANCELLED, 0.0),
    ],
)
def test_progress(status, expected_progress):
    assert states.progress(status) == expected_progress


def test_cancelled_order_has_no_remaining_stages():
    assert states.remaining_stages(states.CANCELLED) == []


def test_remaining_stages_for_placed_order():
    assert states.remaining_stages(states.PLACED) == [
        states.ACCEPTED,
        states.COOKING,
        states.OUT_FOR_DELIVERY,
        states.DELIVERED,
    ]


def test_describe_returns_order_information():
    result = states.describe(states.ACCEPTED)
    assert result["status"] == states.ACCEPTED
    assert result["progress"] == 0.25
    assert result["terminal"] is False
    assert result["cancellable"] is True
    assert result["next"] == [states.COOKING, states.CANCELLED]


def test_terminal_statuses():
    assert states.is_terminal(states.DELIVERED) is True
    assert states.is_terminal(states.CANCELLED) is True
    assert states.is_terminal(states.COOKING) is False


def test_next_states():
    assert states.next_states(states.PLACED) == [
        states.ACCEPTED,
        states.CANCELLED,
    ]
    assert states.next_states(states.DELIVERED) == []


def test_replay_applies_valid_events():
    final_status, applied, rejected = states.replay(
        [
            states.ACCEPTED,
            states.COOKING,
            states.OUT_FOR_DELIVERY,
        ]
    )
    assert final_status == states.OUT_FOR_DELIVERY
    assert applied == [
        states.ACCEPTED,
        states.COOKING,
        states.OUT_FOR_DELIVERY,
    ]
    assert rejected == []


def test_replay_rejects_invalid_event_and_continues():
    final_status, applied, rejected = states.replay(
        [
            states.ACCEPTED,
            states.COOKING,
            states.DELIVERED,
            states.ACCEPTED,
        ]
    )
    assert final_status == states.COOKING
    assert applied == [states.ACCEPTED, states.COOKING]
    assert len(rejected) == 2
