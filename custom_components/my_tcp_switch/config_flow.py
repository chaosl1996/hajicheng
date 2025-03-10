"""
配置流处理实现
"""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from . import DOMAIN

class TCPSwitchConfigFlow(config_entries.ConfigFlow, domain="my_tcp_switch"):
    """处理配置流程"""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """处理用户初始步骤"""
        errors = {}
        if user_input is not None:
            # 验证TCP连接
            from . import TCPClient
            client = TCPClient(user_input["host"], user_input["port"])
            if await client.connect():
                return self.async_create_entry(
                    title=f"TCP Switch {user_input['host']}:{user_input['port']}",
                    data=user_input
                )
            errors["base"] = "connection_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="192.168.1.100"): str,
                vol.Required("port", default=8080): int,
                vol.Required("channels", default=8): vol.All(int, vol.Range(min=1, max=16))
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """获取选项流"""
        return TCPSwitchOptionsFlow(config_entry)


class TCPSwitchOptionsFlow(config_entries.OptionsFlow):
    """处理选项配置流"""

    def __init__(self, config_entry):
        """初始化选项流"""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """管理选项配置"""
        errors = {}
        if user_input is not None:
            # 更新配置并触发重新加载
            new_data = {**self.config_entry.data, **user_input}
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    "channels",
                    default=self.config_entry.data.get("channels", 8)
                ): vol.All(int, vol.Range(min=1, max=16))
            }),
            errors=errors
        )