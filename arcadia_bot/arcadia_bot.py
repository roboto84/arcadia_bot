# Arcadia data sender
import os
import logging.config
from typing import Any
from dotenv import load_dotenv
from arcadia.library.arcadia import Arcadia
from arcadia_bot_utils import ArcadiaBotUtils
from wh00t_core.library.client_network import ClientNetwork


class ArcadiaBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int, sql_lite_db_path: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._chat_key: str = '/arc'
        self._arcadia: Arcadia = Arcadia(sql_lite_db_path, logging_object)
        self._socket_network: ClientNetwork = ClientNetwork(socket_host, socket_port, 'arcadia_bot', 'app', logging)

    def run_bot(self) -> None:
        try:
            self._socket_network.sock_it()
            self._socket_network.receive(self._receive_message_callback)
        except KeyboardInterrupt:
            self._logger.info('Received a KeyboardInterrupt... closing bot')
            exit()

    def _receive_message_callback(self, package: dict) -> bool:
        if ('id' in package) and (package['id'] not in ['wh00t_server', 'arcadia_bot']) and ('message' in package):
            if 'category' in package and package['category'] == 'chat_message' and \
                    isinstance(package['message'], str) and package['message'].find(self._chat_key) == 0:
                search_term: str = package['message'].replace(self._chat_key, '').rstrip()
                if search_term != '':
                    self._send_chat_data(search_term.strip())
                else:
                    self._socket_network.send_message('chat_message', ArcadiaBotUtils.arcadia_bot_help_message())
        return True

    def _send_chat_data(self, search_term: str):
        self._socket_network.send_message('chat_message', f'Ok, searching "{search_term}" 🤔')
        arcadia_summary: str = self._arcadia.get_summary(search_term)
        self._socket_network.send_message('chat_message', f'\n{arcadia_summary}')


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('arcadia_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))
        SQL_LITE_DB: str = os.getenv('SQL_LITE_DB')

        print(f'\nLexicon data sender will now continuously run')
        arcadia_bot: ArcadiaBot = ArcadiaBot(
            logging,
            HOST_SERVER_ADDRESS,
            SOCKET_SERVER_PORT,
            SQL_LITE_DB
        )
        arcadia_bot.run_bot()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
