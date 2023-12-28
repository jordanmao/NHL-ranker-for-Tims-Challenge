from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import timedelta
import json

@dataclass
class Player:
    '''Class for storing player data.'''
    # Personal info:
    id: int
    tims_player_id: str
    first_name: str
    last_name: str
    full_name: str = field(init=False, default='')
    jersey_number: int
    position: str
    team_abbr: str
    # Stats
    goals: int = field(init=False, default=0)
    recent_goals: int = field(init=False, default=0)
    points: int = field(init=False, default=0)
    shots: int = field(init=False, default=0)
    games_played: int = field(init=False, default=0)
    plus_minus: int = field(init=False, default=0)
    shot_percentage: float = field(init=False, default=0)
    time_on_ice: timedelta = field(init=False, default=0)
    goals_per_game: float = field(init=False, default=0)
    injured: bool = field(init=False, default=False)

    def __post_init__(self):
        self.full_name = self.first_name + ' ' + self.last_name

    def dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.full_name,
            'team': self.team_abbr,
            'position': self.position,
            'goals': self.goals,
            'recent goals': self.recent_goals,
            'goals/game': self.goals_per_game,
            'points': self.points,
            'shots': self.shots,
            'shot %': self.shot_percentage,
            '+/-': self.plus_minus,
            'time on ice': str(self.time_on_ice),
            'games played': self.games_played,
            'tims id': self.tims_player_id,
            'injured': self.injured
        }

    def __repr__(self) -> str:
        return json.dumps(self.dict(), indent=4)
