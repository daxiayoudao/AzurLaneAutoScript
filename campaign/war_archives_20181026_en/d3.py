from ..campaign_war_archives.campaign_base import CampaignBase
from module.map.map_base import CampaignMap
from module.map.map_grids import SelectedGrids, RoadGrids
from module.logger import logger
from .d1 import Config as ConfigBase

MAP = CampaignMap('D3')
MAP.shape = 'L9'
MAP.camera_data = ['D2', 'D6', 'D7', 'I2', 'I6', 'I7']
MAP.camera_data_spawn_point = ['D7']
MAP.map_data = """
    -- -- -- ++ ++ ++ ME -- ME -- ++ ++
    -- -- -- -- MB ME -- Me ++ ME ++ ++
    -- -- Me -- -- -- -- __ -- MS -- ME
    -- -- -- MS -- -- ME -- -- -- MM --
    -- ME MB ++ -- Me ++ -- -- ME -- --
    ++ ++ ++ ME -- -- ME -- ++ -- MB --
    SP -- -- -- -- -- -- __ ++ -- -- --
    -- SP -- -- -- Me MS -- -- -- ME --
    -- -- SP -- -- ++ ME -- -- ME -- ++
"""
MAP.weight_data = """
    50 50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50 50
"""
MAP.spawn_data = [
    {'battle': 0, 'enemy': 4, 'siren': 2},
    {'battle': 1, 'enemy': 1, 'siren': 1},
    {'battle': 2, 'enemy': 1, 'mystery': 1},
    {'battle': 3, 'enemy': 1},
    {'battle': 4, 'enemy': 1},
    {'battle': 5},
    {'battle': 6, 'boss': 1},
]
A1, B1, C1, D1, E1, F1, G1, H1, I1, J1, K1, L1, \
A2, B2, C2, D2, E2, F2, G2, H2, I2, J2, K2, L2, \
A3, B3, C3, D3, E3, F3, G3, H3, I3, J3, K3, L3, \
A4, B4, C4, D4, E4, F4, G4, H4, I4, J4, K4, L4, \
A5, B5, C5, D5, E5, F5, G5, H5, I5, J5, K5, L5, \
A6, B6, C6, D6, E6, F6, G6, H6, I6, J6, K6, L6, \
A7, B7, C7, D7, E7, F7, G7, H7, I7, J7, K7, L7, \
A8, B8, C8, D8, E8, F8, G8, H8, I8, J8, K8, L8, \
A9, B9, C9, D9, E9, F9, G9, H9, I9, J9, K9, L9, \
    = MAP.flatten()


class Config(ConfigBase):
    # ===== Start of generated config =====
    MAP_SIREN_TEMPLATE = ['DD', 'CL', 'CA']
    MOVABLE_ENEMY_TURN = (2, 3)
    MAP_HAS_SIREN = True
    MAP_HAS_MOVABLE_ENEMY = True
    MAP_HAS_MAP_STORY = False
    MAP_HAS_FLEET_STEP = True
    MAP_HAS_AMBUSH = False
    MAP_HAS_MYSTERY = True
    # ===== End of generated config =====


class Campaign(CampaignBase):
    MAP = MAP
    ENEMY_FILTER = '1L > 1M > 1E > 1C > 2L > 2M > 2E > 2C > 3L > 3M > 3E > 3C'

    def battle_0(self):
        if self.clear_siren():
            return True
        if self.clear_filter_enemy(self.ENEMY_FILTER, preserve=1):
            return True

        return self.battle_default()

    def battle_5(self):
        if self.clear_siren():
            return True
        if self.clear_filter_enemy(self.ENEMY_FILTER, preserve=0):
            return True

        return self.battle_default()

    def battle_6(self):
        return self.fleet_boss.clear_boss()
