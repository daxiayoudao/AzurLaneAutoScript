from module.base.timer import Timer
from module.campaign.assets import OCR_OIL
from module.combat.assets import *
from module.combat.combat import Combat
from module.exception import CampaignEnd
from module.logger import logger
from module.map.map_operation import MapOperation
from module.ocr.ocr import Digit

OCR_OIL = Digit(OCR_OIL, name='OCR_OIL', letter=(247, 247, 247), threshold=128)


class AutoSearchCombat(MapOperation, Combat):
    _auto_search_in_stage_timer = Timer(3, count=6)
    _auto_search_status_confirm = False
    auto_search_oil_limit_triggered = False

    def _handle_auto_search_menu_missing(self):
        """
        Sometimes game is bugged, auto search menu is not shown.
        After BOSS battle, it enters campaign directly.
        To handle this, if game in campaign for a certain time, it means auto search ends.

        Returns:
            bool: If triggered
        """
        if self.is_in_stage():
            if self._auto_search_in_stage_timer.reached():
                logger.info('Catch auto search menu missing')
                return True
        else:
            self._auto_search_in_stage_timer.reset()

        return False

    def auto_search_watch_fleet(self, checked=False):
        """
        Watch fleet index and ship level.

        Args:
            checked (bool): Watchers are only executed or logged once during fleet moving.
                            Set True to skip executing again.

        Returns:
            bool: If executed.
        """
        prev = self.fleet_current_index
        self.get_fleet_show_index()
        self.get_fleet_current_index()
        if self.fleet_current_index == prev:
            # Same as current, only print once
            if not checked:
                logger.info(f'Fleet: {self.fleet_show_index}, fleet_current_index: {self.fleet_current_index}')
                checked = True
                self.lv_get(after_battle=True)
        else:
            # Fleet changed
            logger.info(f'Fleet: {self.fleet_show_index}, fleet_current_index: {self.fleet_current_index}')
            checked = True
            self.lv_get(after_battle=False)

        return checked

    def auto_search_watch_oil(self, checked=False):
        """
        Watch oil.
        This will set auto_search_oil_limit_triggered.
        """
        if not checked:
            oil = OCR_OIL.ocr(self.device.image)
            if oil == 0:
                logger.warning('Oil not found')
            else:
                if oil < self.config.StopCondition_OilLimit:
                    logger.info('Reach oil limit')
                    self.auto_search_oil_limit_triggered = True
                checked = True

        return checked

    def _wait_until_in_map(self, skip_first_screenshot=True):
        """
        To handle a bug in Azur Lane game client.
        Auto search icon shows it's running but it's doing nothing
        when Alas exited from retirement and turned it on immediately.

        Pages:
            in: Exiting from retirement or enhancement
            out: in_map()
        """
        timeout = Timer(3, count=6).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.is_in_map():
                break
            if timeout.reached():
                logger.warning('Wait in_map after retirement timeout, assume it is in_map')
                break

    def auto_search_moving(self, skip_first_screenshot=True):
        """
        Pages:
            in: map
            out: is_combat_loading()
        """
        logger.info('Auto search moving')
        self.device.stuck_record_clear()
        checked_fleet = False
        checked_oil = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.is_auto_search_running():
                checked_fleet = self.auto_search_watch_fleet(checked_fleet)
                checked_oil = self.auto_search_watch_oil(checked_oil)
            if self.handle_retirement():
                self.map_offensive()
                self._auto_search_status_confirm = True
                continue
            if self.handle_auto_search_map_option():
                continue
            if self.handle_combat_low_emotion():
                self._auto_search_status_confirm = True
                continue
            if self.handle_story_skip():
                continue
            if self.handle_map_cat_attack():
                continue
            if self.handle_vote_popup():
                continue

            # End
            if self.is_combat_loading():
                break
            if self.is_in_auto_search_menu() or self._handle_auto_search_menu_missing():
                raise CampaignEnd

    def auto_search_combat_execute(self, emotion_reduce, fleet_index):
        """
        Args:
            emotion_reduce (bool):
            fleet_index (int):

        Pages:
            in: is_combat_loading()
            out: combat status
        """
        logger.info('Auto search combat loading')
        self.device.screenshot_interval_set('combat')
        while 1:
            self.device.screenshot()

            if self.handle_combat_automation_confirm():
                continue
            if self.handle_story_skip():
                continue
            if self.handle_vote_popup():
                continue

            # End
            if self.is_in_auto_search_menu() or self._handle_auto_search_menu_missing():
                raise CampaignEnd
            if self.is_combat_executing():
                break

        logger.info('Auto Search combat execute')
        self.submarine_call_reset()
        submarine_mode = 'do_not_use'
        if self.config.Submarine_Fleet:
            submarine_mode = self.config.Submarine_Mode
        self.combat_auto_reset()
        self.combat_manual_reset()
        if emotion_reduce:
            self.emotion.reduce(fleet_index)
        auto = self.config.Fleet_Fleet1Mode if fleet_index == 1 else self.config.Fleet_Fleet2Mode

        while 1:
            self.device.screenshot()

            if self.handle_submarine_call(submarine_mode):
                continue
            if self.handle_combat_auto(auto):
                continue
            if self.handle_combat_manual(auto):
                continue
            if auto != 'combat_auto' and self.auto_mode_checked and self.is_combat_executing():
                if self.handle_combat_weapon_release():
                    continue
            if self.handle_popup_confirm('AUTO_SEARCH_COMBAT_EXECUTE'):
                continue
            if self.handle_story_skip():
                continue
            if self.handle_vote_popup():
                continue

            # End
            if self.is_in_auto_search_menu() or self._handle_auto_search_menu_missing():
                self.device.screenshot_interval_set()
                raise CampaignEnd
            if self.is_combat_executing():
                continue
            if self.appear(BATTLE_STATUS_S) or self.appear(BATTLE_STATUS_A) or self.appear(BATTLE_STATUS_B) \
                    or self.appear(EXP_INFO_S) or self.appear(EXP_INFO_A) or self.appear(EXP_INFO_B) \
                    or self.is_auto_search_running():
                self.device.screenshot_interval_set()
                break

    def auto_search_combat_status(self, skip_first_screenshot=True):
        """
        Pages:
            in: any
            out: is_auto_search_running()
        """
        logger.info('Auto Search combat status')
        exp_info = False  # This is for the white screen bug in game

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if self.is_auto_search_running():
                self._auto_search_status_confirm = False
                break
            if self.is_in_auto_search_menu() or self._handle_auto_search_menu_missing():
                raise CampaignEnd

            # Combat status
            if self.handle_get_ship():
                continue
            if self.handle_popup_confirm('AUTO_SEARCH_COMBAT_STATUS'):
                continue
            if self.handle_auto_search_map_option():
                self._auto_search_status_confirm = False
                continue
            if self.handle_urgent_commission():
                continue
            if self.handle_story_skip():
                continue
            if self.handle_guild_popup_cancel():
                continue
            if self.handle_vote_popup():
                continue

            # Handle low emotion combat
            # Combat status
            if self._auto_search_status_confirm:
                if not exp_info and self.handle_get_ship():
                    continue
                if self.handle_get_items():
                    continue
                if self.handle_battle_status():
                    continue
                if self.handle_popup_confirm('combat_status'):
                    continue
                if self.handle_exp_info():
                    exp_info = True
                    continue

    def auto_search_combat(self, emotion_reduce=None, fleet_index=1):
        """
        Execute a combat.

        Note that fleet index == 1 is mob fleet, 2 is boss fleet.
        It's not the fleet index in fleet preparation or auto search setting.
        """
        emotion_reduce = emotion_reduce if emotion_reduce is not None else self.config.Emotion_CalculateEmotion

        self.device.stuck_record_clear()
        self.auto_search_combat_execute(emotion_reduce=emotion_reduce, fleet_index=fleet_index)
        self.auto_search_combat_status()

        logger.info('Combat end.')
