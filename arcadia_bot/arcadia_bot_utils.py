
class ArcadiaBotUtils:
    @staticmethod
    def arcadia_bot_help_message() -> str:
        return f'  🤔\n\nDoesn\'t look like you gave me a good command ...\n\n' \
               f'Commands are as follows:\n' \
               f'     /arc search {{term_to_search}} : gives summary of data on the term\n' \
               f'     /arc add {{data_type}} {{single_string_data_content}} {{comma_separated_data_tags}}: ' \
               f'adds data to arcadia, tags are COMMA SEPERATED tags with NO SPACES\n\n'
