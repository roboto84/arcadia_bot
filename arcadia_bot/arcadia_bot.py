# Arcadia data sender
import os
import logging.config
from typing import Any

from arcadia.library.db.db_types import ItemPackage, ArcadiaDataType, AddDbItemResponse
from dotenv import load_dotenv
from arcadia.library.arcadia import Arcadia
from arcadia_bot_utils import ArcadiaBotUtils
from wh00t_core.library.client_network import ClientNetwork
from wh00t_core.library.network_commons import NetworkCommons


class ArcadiaBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int, sql_lite_db_path: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._chat_key: str = '/arc'
        self._arcadia: Arcadia = Arcadia(logging_object, sql_lite_db_path, True)
        self._socket_network: ClientNetwork = ClientNetwork(socket_host, socket_port, 'arcadia_bot', 'app', logging)
        self._network_commons: NetworkCommons = NetworkCommons()

    def run_bot(self) -> None:
        try:
            self._socket_network.sock_it()
            self._socket_network.receive(self._receive_message_callback)
        except KeyboardInterrupt:
            self._logger.info('Received a KeyboardInterrupt... closing bot')
            exit()

    def _receive_message_callback(self, package: dict) -> bool:
        if ('id' in package) and (package['id'] not in ['wh00t_server', 'arcadia_bot']) and ('message' in package):
            if 'category' in package and package['category'] == self._network_commons.get_chat_message_category() and \
                    isinstance(package['message'], str) and package['message'].find(self._chat_key) == 0:
                command_term: str = package['message'].replace(self._chat_key, '').rstrip()
                if command_term != '':
                    self._command_handler(command_term.strip())
                else:
                    self._socket_network.send_message(
                        self._network_commons.get_chat_message_category(),
                        ArcadiaBotUtils.arcadia_bot_help_message()
                    )
        return True

    def _command_handler(self, command_sequence: str) -> None:
        command_list: list[str] = command_sequence.split(' ')

        if len(command_list) == 1:
            if command_list[0].strip() == 'tags':
                self._get_arc_tags()
            else:
                self._search_arc_data(command_list[0].strip())
        elif len(command_list) == 2:
            if command_list[0].strip() == 'tags':
                self._get_arc_tags(command_list[1])
            else:
                self._add_arc_data(command_list)
        else:
            self._socket_network.send_message(
                self._network_commons.get_chat_message_category(),
                ArcadiaBotUtils.arcadia_bot_help_message()
            )

    def _get_arc_tags(self, search_tag: str = '') -> None:
        if search_tag:
            subjects_list: list[str] = self._arcadia.get_subjects().split(',')
            arcadia_subjects: str = ''.join(
                (f'{tag}, ' if search_tag in tag else '') for tag in subjects_list
            ).rstrip(', ')
            arcadia_subjects_view: str = f'*\'{search_tag}\' is in the following tags:*\n\n' \
                                         f'     [{arcadia_subjects}]'
        else:
            arcadia_subjects: str = ArcadiaBotUtils.arcadia_subjects_dictionary_view(
                self._arcadia.get_subjects_dictionary()
            )
            arcadia_subjects_view: str = f'*Arcadia Tags Dictionary*\n\n{arcadia_subjects}'
        self._socket_network.send_message(
            self._network_commons.get_chat_message_category(),
            f'{arcadia_subjects_view}'
        )

    def _search_arc_data(self, search_term: str) -> None:
        arcadia_summary: str = self._arcadia.get_summary(search_term)
        self._socket_network.send_message(
            self._network_commons.get_chat_message_category(),
            f'{arcadia_summary}'
        )

    def _add_arc_data(self, add_term: list[str]) -> None:
        possible_url: str = add_term[1]
        tags: str = add_term[0]
        if ArcadiaBotUtils.validate_url(possible_url):
            arc_package: ItemPackage = {
                'data_type': ArcadiaDataType.URL,
                'content': possible_url,
                'tags': tags.split(',')
            }

            add_item_result: AddDbItemResponse = self._arcadia.add_item(arc_package)
            print(add_item_result['added_item'], add_item_result['reason'])
            if add_item_result['added_item']:
                self._socket_network.send_message(
                    self._network_commons.get_chat_message_category(),
                    f'Added record "{arc_package["content"]}" '
                    f'successfully under [{"".join(f"{tag}, " for tag in arc_package["tags"]).rstrip(", ")}]')
            elif not add_item_result['added_item'] and add_item_result['reason'] == 'item_duplicate':
                self._socket_network.send_message(
                    self._network_commons.get_chat_message_category(),
                    f'Failed to add duplicate record "{arc_package["content"]}"\nRecord already under tags '
                    f'{add_item_result["data"][0][1]}'
                )
            elif not add_item_result['added_item'] and add_item_result['reason'] == 'empty_string_tag':
                self._socket_network.send_message(
                    self._network_commons.get_chat_message_category(),
                    f'Failed to add record "{arc_package["content"]}"\nLooks like empty string in tags: '
                    f'{add_item_result["data"]}'
                )
            else:
                self._socket_network.send_message(
                    self._network_commons.get_chat_message_category(),
                    f'Failed to add record "{arc_package["content"]}" '
                    f'{ArcadiaBotUtils.arcadia_bot_help_message()}')
        else:
            data_type_not_found_message: str = f'\nLooks like "{possible_url}" is not an acceptable URL.\n' \
                                               f'Please make sure you give a complete URL.\n\n' \
                                               f'{ArcadiaBotUtils.arcadia_bot_help_message()}'
            self._socket_network.send_message(
                self._network_commons.get_chat_message_category(),
                data_type_not_found_message
            )


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('arcadia_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))
        SQL_LITE_DB: str = os.getenv('SQL_LITE_DB')

        print(f'\nArcadia bot will now run continuously...')
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
