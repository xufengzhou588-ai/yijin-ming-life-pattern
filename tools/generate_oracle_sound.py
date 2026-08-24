from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 44_100
DURATION = 2.72
OUTPUT = Path(__file__).resolve().parents[1] / "web" / "assets" / "oracle-cast-v3.wav"


def add_impact(
    left: list[float],
    right: list[float],
    *,
    start: float,
    level: float,
    pan: float,
    modes: tuple[tuple[float, float, float], ...],
    click: float,
    seed: int,
) -> None:
    rng = random.Random(seed)
    start_index = int(start * SAMPLE_RATE)
    duration = max(decay for _, _, decay in modes) * 7
    frame_count = min(int(duration * SAMPLE_RATE), len(left) - start_index)
    phases = [rng.uniform(0, math.tau) for _ in modes]

    for offset in range(max(0, frame_count)):
        age = offset / SAMPLE_RATE
        value = rng.uniform(-1.0, 1.0) * click * math.exp(-age / 0.0025)
        for (frequency, weight, decay), phase in zip(modes, phases):
            value += (
                math.sin(age * math.tau * frequency + phase)
                * weight
                * math.exp(-age / decay)
            )
        value *= level
        index = start_index + offset
        left[index] += value * (1.0 - pan)
        right[index] += value * (1.0 + pan)


def add_roll(
    left: list[float],
    right: list[float],
    *,
    start: float,
    duration: float,
    level: float,
    pan_start: float,
    pan_end: float,
    seed: int,
) -> None:
    rng = random.Random(seed)
    start_index = int(start * SAMPLE_RATE)
    frame_count = min(int(duration * SAMPLE_RATE), len(left) - start_index)
    next_tick = 0

    for offset in range(max(0, frame_count)):
        progress = offset / max(1, frame_count - 1)
        age = offset / SAMPLE_RATE
        pan = pan_start + (pan_end - pan_start) * progress
        value = 0.0
        if offset >= next_tick:
            speed = 42 - 27 * progress
            next_tick = offset + max(90, int(SAMPLE_RATE / speed))
            value += rng.uniform(0.55, 1.0)
        value *= math.exp(-age / max(0.08, duration * 0.68)) * level
        index = start_index + offset
        left[index] += value * (1.0 - pan)
        right[index] += value * (1.0 + pan)


def add_wood_thump(
    left: list[float],
    right: list[float],
    *,
    start: float,
    level: float,
    pan: float,
    seed: int,
) -> None:
    add_impact(
        left,
        right,
        start=start,
        level=level,
        pan=pan,
        modes=(
            (118, 0.42, 0.055),
            (214, 0.3, 0.043),
            (386, 0.17, 0.028),
            (720, 0.06, 0.018),
        ),
        click=0.08,
        seed=seed,
    )


def main() -> None:
    frame_count = int(SAMPLE_RATE * DURATION)
    left = [0.0] * frame_count
    right = [0.0] * frame_count

    shell_modes = (
        (275, 0.34, 0.026),
        (530, 0.27, 0.035),
        (920, 0.16, 0.028),
        (1_680, 0.07, 0.018),
    )
    coin_modes = (
        (1_340, 0.34, 0.042),
        (2_180, 0.26, 0.036),
        (3_260, 0.15, 0.026),
        (4_720, 0.06, 0.017),
    )

    shell_events = (
        (0.08, 0.23, -0.34),
        (0.16, 0.16, 0.18),
        (0.27, 0.24, 0.38),
        (0.39, 0.28, -0.08),
        (0.51, 0.17, -0.4),
        (0.62, 0.25, 0.27),
        (0.76, 0.29, 0.04),
        (0.88, 0.18, -0.29),
        (0.99, 0.24, 0.34),
    )
    for event_index, (start, level, pan) in enumerate(shell_events):
        add_impact(
            left,
            right,
            start=start,
            level=level,
            pan=pan,
            modes=coin_modes if event_index % 3 == 1 else shell_modes,
            click=0.045,
            seed=100 + event_index,
        )

    for event_index, (start, pan) in enumerate(((1.13, -0.3), (1.22, 0.02), (1.3, 0.31))):
        add_impact(
            left,
            right,
            start=start,
            level=0.14,
            pan=pan,
            modes=coin_modes,
            click=0.035,
            seed=220 + event_index,
        )

    landing_times = (1.57, 1.69, 1.84)
    landing_pans = (-0.4, 0.03, 0.39)
    landing_levels = (0.84, 0.72, 0.78)
    for coin_index, (start, pan) in enumerate(zip(landing_times, landing_pans)):
        add_wood_thump(
            left,
            right,
            start=start,
            level=landing_levels[coin_index],
            pan=pan,
            seed=280 + coin_index,
        )
        add_impact(
            left,
            right,
            start=start + 0.004,
            level=(0.28, 0.22, 0.25)[coin_index],
            pan=pan,
            modes=coin_modes,
            click=0.11,
            seed=300 + coin_index,
        )
        bounce_delay = (0.145, 0.19, 0.13)[coin_index]
        add_wood_thump(
            left,
            right,
            start=start + bounce_delay,
            level=(0.2, 0.14, 0.18)[coin_index],
            pan=pan * 0.82,
            seed=320 + coin_index,
        )
        add_impact(
            left,
            right,
            start=start + bounce_delay + 0.003,
            level=(0.09, 0.065, 0.08)[coin_index],
            pan=pan * 0.8,
            modes=coin_modes,
            click=0.03,
            seed=340 + coin_index,
        )
        add_roll(
            left,
            right,
            start=start + bounce_delay + 0.06,
            duration=(0.42, 0.28, 0.36)[coin_index],
            level=(0.025, 0.018, 0.022)[coin_index],
            pan_start=pan,
            pan_end=pan * 0.55,
            seed=380 + coin_index,
        )

    peak = max(max(abs(value) for value in left), max(abs(value) for value in right), 1e-9)
    gain = 0.76 / peak

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT), "wb") as target:
        target.setnchannels(2)
        target.setsampwidth(2)
        target.setframerate(SAMPLE_RATE)
        target.writeframes(
            b"".join(
                struct.pack(
                    "<hh",
                    int(max(-1.0, min(1.0, l_value * gain)) * 32_767),
                    int(max(-1.0, min(1.0, r_value * gain)) * 32_767),
                )
                for l_value, r_value in zip(left, right)
            )
        )


if __name__ == "__main__":
    main()
