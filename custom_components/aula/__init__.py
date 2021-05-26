from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .client import Client
from .const import DOMAIN, CONF_SELENIUM

async def async_setup(hass, config):
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    client  = Client(conf.get(CONF_SELENIUM), conf.get(CONF_USERNAME), conf.get(CONF_PASSWORD))
    hass.data[DOMAIN] = {
        "client": client
    }

    # Add sensors
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform('sensor', DOMAIN, conf, config)
    )

    # Initialization was successful.
    return True