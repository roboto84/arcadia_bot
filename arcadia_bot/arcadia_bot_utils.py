import validators


class ArcadiaBotUtils:
    @staticmethod
    def arcadia_bot_help_message() -> str:
        return f'  🤔\n\nDoesn\'t look like you gave me a good command ...\n\n' \
               f'Commands are as follows:\n\n' \
               f'     `/arc tags` : prints out full list of arcadia tags\n' \
               f'     `/arc tags {{tag_search_term}}` : prints tags with search term in it\n' \
               f'     `/arc {{single_word_tag_to_search}}` : returns data associated to the searched tag\n' \
               f'     `/arc {{URL}} {{comma_separated_data_tags}}`: ' \
               f'adds URL to arcadia, URL must be VALID, and tags must be COMMA SEPERATED tags with NO SPACES\n\n'

    @staticmethod
    def validate_url(url: str) -> bool:
        return validators.url(url)

    @staticmethod
    def arcadia_subjects_dictionary_view(subject_dictionary: dict[str:list[str]]) -> str:
        subject_dictionary_str: str = ''
        for key in subject_dictionary:
            if len(subject_dictionary[key]) > 0:
                subject_dictionary_str += f'*{key} |* ' \
                                          f'{"".join(f"{tag}, " for tag in subject_dictionary[key]).rstrip(", ")}\n\n'
        return subject_dictionary_str
