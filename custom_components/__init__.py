"""
实现TCP开关控制的自定义集成
"""
from __future__ import annotations

import logging
import asyncio
from homeassistant import config_entries, core
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.helpers import device_registry as dr

DOMAIN = "my_tcp_switch"
_LOGGER = logging.getLogger(__name__)

from .client import TCPClient
from .switch import async_setup_entry as setup_switch
from .sensor import async_setup_entry as setup_sensor

async def async_setup_entry(hass, config_entry):
    """设置集成配置入口"""
    host = config_entry.data["host"]
    port = config_entry.data["port"]
    
    client = TCPClient(host, port)
    if not await client.connect():
        return False
    
    device_info = DeviceInfo(
        identifiers={(DOMAIN, f"tcp_switch_{host}_{port}")},
        manufacturer="Custom TCP",
        name=f"TCP Switch {host}:{port}",
        model="TCP-8CH",
        sw_version="1.0"
    )
    
    await setup_switch(hass, config_entry, client, device_info)
    await setup_sensor(hass, config_entry, client, device_info)
    
    return True