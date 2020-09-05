OFFSET = 127462 - ord("A")


def flag_emoji(code):
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)


if __name__ == "__main__":
    available_locales = {
        "en_US": flag_emoji("US") + " English (US)",
        "de_DE": flag_emoji("DE") + " Deutsch (DE)",
        # 'es_ES': flag('ES') + ' Español (ES)',
        # 'id_ID': flag('ID') + ' Bahasa Indonesia',
        # 'it_IT': flag('IT') + ' Italiano',
        # 'pt_BR': flag('BR') + ' Português Brasileiro',
        # 'ru_RU': flag('RU') + ' Русский язык',
        # 'zh_CN': flag('CN') + ' 中文(简体)',
        # 'zh_HK': flag('HK') + ' 廣東話',
        # 'zh_TW': flag('TW') + ' 中文(台灣)'
    }

    print(available_locales)
