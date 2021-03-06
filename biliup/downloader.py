import logging
import re
import time
from urllib.error import HTTPError

from .engine.decorators import Plugin
from .plugins import general, BatchCheckBase

logger = logging.getLogger('log01')


def download(fname, url):
    for plugin in Plugin.download_plugins:
        if re.match(plugin.VALID_URL_BASE, url):
            plugin(fname, url).start()
            return
    general.__plugin__(fname, url).start()


def check_url(plugin):
    try:
        if isinstance(plugin, BatchCheckBase):
            return (yield from plugin.check())
        for url in plugin.url_list:
            if plugin(f'检测{url}', url).check_stream():
                yield url
            if url != plugin.url_list[-1]:
                logger.debug('歇息会')
                time.sleep(15)
    except HTTPError as e:
        logger.error(f'{plugin.__module__} {e.url} => {e}')
    except IOError:
        logger.exception("IOError")
