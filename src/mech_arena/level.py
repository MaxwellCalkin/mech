"""Placeholder for game level logic."""

from dataclasses import dataclass


@dataclass
class Level:
    name: str
    description: str

    def start(self) -> None:
        print(f"Starting level: {self.name}")
