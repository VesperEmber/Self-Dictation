from speech_synthesis import azure_system_speech

azure_connection = False


# "\033[32m" + 'self-dictation: ' + "\033[0m"

class Help:
    @staticmethod
    def main_help():
        help_text = """
                Convention: 
                  The <> enclosed contents are the parameters that must be occupied.
                  The [] enclosed contents are the optional parameters.

                Usage: <command>
                Commands:
                  help [options]              - Print help document.
                  exit                        - Exit the program.
                  clear                       - Clear the screen.
                  corpus <actions> [args]...  - Implement operations on the corpus.
                  import <dir>                - Import words from the dir into corpus.
                  delete <dir>                - Delete words from corpus based on dir.
                  dictation [args]...         - Implement dictation program.

                Usage: help [options]
                Options:
                  exit       - Print help document about the "exit" instruction in detail.
                  clear      - Print help document about the "clear" instruction in detail.
                  corpus     - Print help document about the "corpus" instruction in detail.
                  import     - Print help document about the "import" instruction in detail.
                  delete     - Print help document about the "delete" instruction in detail.
                  dictation  - Print help document about the "dictation" instruction in detail.
                """
        print(help_text)

    @staticmethod
    def help_corpus():
        help_text = """
                corpus  - Implement operations on the corpus.
                Usage: corpus <action> [options]...

                Actions:
                  divide  - Divide the corpus based on certain criteria.
                    Usage: corpus divide <method> [options]...
                    Methods:
                      num|nums|number  - Divide the corpus into a specified number of parts.
                        Usage: corpus divide num <integer>
                      date  - Divide the corpus based on import dates.
                        Usage: corpus divide date <date1> [date2]
                        Note: If date2 is not provided, it defaults to today's date.
                      tag  - Divide the corpus based on word tags.
                        Usage: corpus divide tag [tags]...

                  display  - Display words and their information from the corpus.
                    Usage: corpus display [<num>] [options]...
                    If provided, `<num>` must be the first argument, specifying the number of words to display.

                    Options:
                      <num>                The number of words to display. Must be the first argument if used.
                      language             Show language information.
                      voice_name           Show voice name information.
                      import_date          Show import date.
                      last_test_date       Show last test date.
                      test_times           Show test times.
                      correct              Show correct answer times.
                      wrong                Show wrong answer times.
                      case_sensitivity     Show case sensitivity setting.
                      tag                  Show tags.
                      weight               Show weight.
                      all_params           Show all available information.
                      tabulate             Display information in a tabular format.

                    Examples:
                      corpus display 15 language weight
                      corpus display tag import_date tabulate


                  sort  - Sort the corpus based on specified criteria.
                    Usage: corpus sort <criteria> [reverse]
                    Criteria:
                      word, import_date, last_test_date, test_times, correct, wrong, case_sensitivity, weight

                  reload  - Reload the main corpus.
                    Usage: corpus reload [language]
                    Note: If a language is specified, the main corpus for that language will be loaded.
                """
        print(help_text)

    @staticmethod
    def help_import():
        help_text = """
                import  - Import words from a .txt file into the corpus.
                  Usage: corpus import <file_path>
                  The <file_path> parameter should be a valid path to a .txt file containing words to be imported.

                  <file_path>
                    The path to the .txt file you wish to import. The file should be formatted in a way that is compatible with the corpus import function.

                  File Format:
                  The .txt file should be formatted as follows:
                  - Parameters section: Define the default settings for the imported words.
                    Example:
                    # parameters
                    language: english
                    voice_name: en-US-JennyNeural
                    import_date: 2023-10-24
                    case_sensitivity: false
                    tag: GRE, CET6, CET4

                  - Wordlist section: List the words and their meanings.
                    Format: word: meaning1, meaning2, ...
                    Example:
                    # wordlist
                    avatar: 化身
                    mist: 雾, 使蒙上雾
                    ...

                  Examples:
                    corpus import C:/Users/YourUsername/Documents/words_to_import.txt
                    corpus delete ./relative/path/to/your/deletion_list.txt

                  Note:
                    Please ensure that the .txt file is formatted correctly and the file path is accurate. 
                    The format requirements of the .txt file should be documented in the user manual or the corpus import function documentation.
                        """
        print(help_text)

    @staticmethod
    def help_delete():
        help_text = """
                delete  - Delete words from the corpus using a list from a .txt file.
                  Usage: corpus delete <file_path>
                  The <file_path> parameter should be a valid path to a .txt file containing words to be deleted.

                  <file_path>
                    The path to the .txt file you wish to use for deleting words from the corpus. 
                    The file should be formatted in a specific way to ensure proper deletion.

                  File Format:
                    The .txt file should be formatted as follows:
                    - Parameters section: Define the language setting for the deletion operation.
                      Example:
                      # parameters
                      language: english

                    - Wordlist section: List the words to be deleted.
                      Format: word1
                              word2
                              ...
                      Example:
                      # wordlist
                      avatar
                      mist
                      denote
                      ...

                  Examples:
                    corpus delete C:/Users/YourUsername/Documents/words_to_delete.txt
                    corpus delete ./relative/path/to/your/deletion_list.txt

                  Note:
                    Please ensure that the .txt file is formatted correctly and the file path is accurate. 
                    The parameters section is optional, and if not provided, the default language setting of the corpus will be used.
"""
        print(help_text)

    @staticmethod
    def help_dictation():
        help_text = """
                dictation  - Conduct a dictation exercise based on words from the corpus.
                  Usage: corpus dictation <scope> [options]...

                  <scope>
                    all        Conduct the dictation using all words from the corpus.
                    <number>   Conduct the dictation using the first <number> words from the corpus.

                  Options:
                    random         Randomly sample words for the dictation (not applicable when 'all' is specified).
                    smart          Smartly sample words for the dictation based on certain criteria (default, not applicable when 'all' is specified).
                    meanings_only  Focus the dictation on meanings only; the spellings will be provided by the program.

                  Description:
                    The 'dictation' command initiates a dictation exercise where words are presented to the user, and the user is required to spell them and/or provide their meanings.

                    Upon starting the dictation, the screen will automatically clear to provide a clean workspace for the exercise.

                    The <scope> argument determines the range of words used for the dictation:
                      - 'all' means that all words in the corpus will be considered.
                      - Providing a <number> means that only the first <number> words in the corpus will be considered.

                    The [options] allow further customization of the dictation exercise:
                      - 'random' will ensure that words are randomly selected from the chosen range. This option is not applicable when 'all' is specified.
                      - 'smart' will use intelligent sampling to choose words, focusing on words that might need more practice. 
                                This is the default behavior if neither 'random' nor 'smart' are specified and is not applicable when 'all' is specified.
                      - 'meanings_only' shifts the focus of the dictation to testing only the meanings of words. 
                                If not specified, both spellings and meanings will be tested.

                  Examples:
                    corpus dictation all
                    corpus dictation 7
                    corpus dictation all meanings_only
                    corpus dictation 10 smart

                  Notes:
                    - The order of the options does not matter.
                    - Ensure that the corpus is loaded and contains words before initiating a dictation exercise.
    """
        print(help_text)

    @staticmethod
    def help_exit():
        help_text = """
                exit  - Exit the program.
                  Usage: exit
"""
        print(help_text)

    @staticmethod
    def help_clear():
        help_text = """
                clear  - Clear the screen.
                  Usage: clear
    """
        print(help_text)


def test_azure():
    global azure_connection
    sentence = 'Welcome to use the intelligent self-dictation tool developed by TLHX.'
    print("\033[32m" + 'self-dictation: ' + "\033[0m" + sentence)
    # connection = speech_synthesis.azure_text_to_speech(sentence)
    time.sleep(0.5)
    print("\033[33m" + 'Connecting to Microsoft-Azure-Speech-Synthesis api...' + "\033[0m")
    connection = azure_system_speech(sentence)
    if not connection:
        time.sleep(1)
        # if not connection:
        # speech_synthesis.azure_text_to_speech(sentence)
        sentence = 'Connecting to Microsoft Azure Speech Synthesis api fails. ' \
                   'If you want to enjoy high quality artificial neural network synthesized voice, please check your SPEECH KEY, SPEECH REGION parameters, and network configuration.'
        print("\033[32m" + 'self-dictation: ' + "\033[0m" + "\033[31m" + sentence + "\033[0m")
        azure_system_speech(sentence)
    else:
        azure_connection = True
        sentence = 'Successfully connect to the Microsoft Azure Speech Synthesis api to enjoy high quality artificial neural network synthesized voice.'
        print("\033[32m" + 'self-dictation: ' + "\033[0m" + sentence)
        azure_system_speech(sentence)


def get_language():
    global azure_connection
    if azure_connection:
        valid_language = ['english', 'chinese', 'japanese', 'german', 'french']
    else:
        valid_language = ['english', 'chinese']
    flag = False
    while True:
        sentence = 'Please enter the dictation language for corpus'
        print("\033[32m" + 'self-dictation: ' + "\033[0m" + 'Please enter the dictation language for corpus:')
        if not flag:
            azure_system_speech(sentence, wait=False)
            flag = True
        language = input('(language):').strip().lower()
        if not language:
            continue
        if language in valid_language:
            break
        else:
            # sentence = 'We can only support Chinese, English, Japanese, German and French now.'
            sentence = 'We can only support ' + ', '.join(
                [language.capitalize() for language in valid_language]) + ' for ' + (
                           'Azure' if azure_connection else 'no Azure')
            print("\033[32m" + 'self-dictation: ' + "\033[0m" + "\033[31m" + sentence + "\033[0m")
            azure_system_speech(sentence)
    return language


def parse_instruction(corpus, MiniLM, sbert, instruction: str):
    if not instruction:
        return
    valid_instructions_head = ['help', 'corpus', 'import', 'delete', 'dictation', 'exit', 'clear']
    instructions = instruction.split()
    head, params = instructions[0], instructions[1:]
    if head not in valid_instructions_head:
        sentence = 'Instruction illegal. You can type "help" without the quotes to see all the instructions and their usage.'
        print("\033[32m" + 'self-dictation: ' + "\033[0m" + "\033[31m" + sentence + "\033[0m")
        azure_system_speech(sentence, wait=False)
        return

    def parameters_illegal():
        s = 'Parameters illegal.'
        print("\033[32m" + 'self-dictation: ' + "\033[0m" + "\033[31m" + s + "\033[0m")
        azure_system_speech(s, wait=False)

    def parameters_missing():
        s = 'Parameters missing.'
        print("\033[32m" + 'self-dictation: ' + "\033[0m" + "\033[31m" + s + "\033[0m")
        azure_system_speech(s, wait=False)

    if head == 'exit':
        sentence = 'Thanks for using the self-dictation tool, bye.'
        print("\033[32m" + 'self-dictation: ' + "\033[0m" + sentence)
        azure_system_speech(sentence)
        sys.exit()
    elif head == 'corpus':
        valid_params_corpus = ['divide', 'display', 'sort', 'reload']
        if not params:
            parameters_missing()
            return
        if params[0] not in valid_params_corpus:
            parameters_illegal()
            return
        # 从这开始就是给了 params, 并且 params[0] in ['divide', 'display', 'reload']
        if params[0] == 'divide':  # corpus divide... 这个依旧需要后续的 params
            if not params[1:]:
                parameters_missing()
                return
            if params[1] not in ['date', 'tag', 'num', 'nums', 'number']:
                parameters_illegal()
                return
            if params[1] == 'date':  # corpus divide date...
                if not params[2:]:
                    parameters_missing()
                    return
                if len(params[2:]) > 2:  # 依旧需要后续参数指定日期
                    parameters_illegal()
                    return

                def date_test(date):
                    for d in date:
                        try:
                            datetime.strptime(d, "%Y-%m-%d")
                        except ValueError:
                            return False
                    return True

                if date_test(params[2:]):  # 是个正确的 corpus divide date 2023-10-25 (2023-10-26) 格式的指令
                    corpus.divide_corpus_by_date(*params[2:])
                    return
                else:
                    parameters_illegal()
                    return
            elif params[1] in ['num', 'nums', 'number']:  # corpus divide num...
                if not params[2:]:
                    parameters_missing()
                    return
                if len(params[2:]) > 1:
                    parameters_illegal()
                    return
                try:
                    x = int(params[2])
                except Exception as e:
                    parameters_illegal()
                    return
                corpus.divide_corpus_by_nums(x)  # 是个正确的 corpus divide num 10 格式的指令
                return
            else:  # corpus divide tag...
                if not params[2:]:
                    parameters_missing()
                    return
                tag = params[2:]
                corpus.divide_corpus_by_tag(tag)  # 是个正确的 corpus divide tag GRE, CET4, CET6 格式的指令
                return
        elif params[0] == 'display':  # corpus display...
            if not params[1:]:  # corpus display 也算是个正确指令, 即直接展示词表所有单词以及所有参数
                corpus.display_corpus()
                return
            try:
                x = int(params[1])  # 若执行成功, 则说明有要展示的前 nums 个词这个参数
                corpus.display_corpus(x, *params[2:])
            except Exception as e:  # 这个异常, 则说明后面跟的直接就是参数了, 此时默认 nums=0 也就是全部展示
                corpus.display_corpus(0, *params[1:])
        elif params[0] == 'sort':
            if not params[1:]:
                parameters_missing()
                return
            # corpus sort xxx...
            if len(params[1:]) > 2 or (len(params[1:]) == 2 and params[2] != 'reverse'):
                parameters_illegal()
                return
            corpus.sort_corpus_by_instruction(*params[1:])
            return
        else:  # corpus reload...
            if not params[1:]:  # corpus reload 也算是个正确指令, 即直接 reload corpus.language 的主 corpus
                corpus.load_main_corpus(language=corpus.language)
                return
            # corpus reload 后顶多再接一个 language 参数, 多于 1 个参数则报参数非法. 抑或如果 language 不在合法 language 列表内也报参数非法
            if len(params[1:]) > 1 or params[1] not in ['english', 'chinese', 'japanese', 'german', 'french']:
                parameters_illegal()
                return
            corpus.load_main_corpus(language=params[1])
            return

    elif head == 'import':  # 从给定地址参数导入单词
        if not params:
            parameters_missing()
            return
        if len(params) > 1:
            parameters_illegal()
            return
        # import xxx, xxx需要是个地址
        corpus.import_words_from_txt(params[0])
        return

    elif head == 'delete':  # 从给定地址参数删除单词
        if not params:
            parameters_missing()
            return
        if len(params) > 1:
            parameters_illegal()
            return
        # import xxx, xxx需要是个地址
        corpus.delete_words_from_txt(params[0])
        return

    elif head == 'dictation':
        if not params:
            parameters_missing()
            return
        if len(params) == 1:  # dictation xxx, 这个 xxx 要么是个数字用于指定听写数量, 要么是 all 指定全部听写
            if params[0] == 'all':  # dictation all, 全部听写
                dictation_loop(corpus, 0, MiniLM=MiniLM, sbert=sbert)
                return
            else:  # dictation x, 要测试这个 x 是否为数字
                try:
                    x = int(params[0])
                    dictation_loop(corpus, x, MiniLM=MiniLM, sbert=sbert)
                    return
                except Exception as e:
                    # 参数非法
                    parameters_illegal()
                    return
        elif len(params) == 2:  # dictation [nums, all] [smart, meanings_only] 的情况
            if params[1] not in ['smart', 'random', 'meanings_only']:
                parameters_illegal()
                return
            if params[0] == 'all':  # dictation all, 全部听写
                if params[1] in ['smart', 'random']:
                    dictation_loop(corpus, 0, MiniLM=MiniLM, sbert=sbert)
                else:
                    dictation_loop(corpus, 0, MiniLM=MiniLM, sbert=sbert, meanings_only=True)
                return
            else:  # dictation x, 要测试这个 x 是否为数字
                try:
                    x = int(params[0])
                    if params[1] == 'random':
                        dictation_loop(corpus, x, MiniLM=MiniLM, sbert=sbert, smart_sample=False)
                    elif params[1] == 'meanings_only':
                        dictation_loop(corpus, x, MiniLM=MiniLM, sbert=sbert, meanings_only=True)
                    else:
                        dictation_loop(corpus, x, MiniLM=MiniLM, sbert=sbert)
                    return
                except Exception as e:
                    # 参数非法
                    parameters_illegal()
                    return
        elif len(params) == 3:
            if params[1] not in ['smart', 'random', 'meanings_only'] or params[2] not in ['smart', 'random',
                                                                                          'meanings_only']:
                parameters_illegal()
                return
            if params[0] == 'all':
                x = 0
            else:
                try:
                    x = int(params[0])
                except Exception as e:
                    parameters_illegal()
                    return
            meanings_only = True if 'meanings_only' in params[1:] else False
            random_flag = False if 'random' in params[1:] else True
            if 'random' in params[1:] and 'smart' in params[1:]:
                parameters_illegal()
                return
            dictation_loop(corpus, x, MiniLM=MiniLM, sbert=sbert, meanings_only=meanings_only,
                           smart_sample=random_flag)
            return
        else:
            parameters_illegal()
            return

    elif head == 'clear':
        if params:  # clear 是个单独的命令, 它不应当有参数
            parameters_missing()
            return
        os.system('cls' if os.name == 'nt' else 'clear')

    elif head == 'help':
        if len(params) > 1:
            Help.main_help()
        elif len(params) == 1:
            if params[0] == 'corpus':  # ['help', 'corpus', 'import', 'delete', 'dictation', 'exit', 'clear']
                Help.help_corpus()
            elif params[0] == 'import':
                Help.help_import()
            elif params[0] == 'delete':
                Help.help_delete()
            elif params[0] == 'dictation':
                Help.help_dictation()
            elif params[0] == 'exit':
                Help.help_exit()
            elif params[0] == 'clear':
                Help.help_clear()
            else:
                Help.main_help()
        else:
            Help.main_help()


def self_dictation_loop(corpus, models):
    # valid_instructions = ['help', '']
    sentence = 'Program begins! You can type "help" without the quotes to see all the instructions and their usage.'
    # print("\033[32m" + 'self-dictation: ' + "\033[0m" + sentence + '\n(instruction):', end=''
    print("\033[32m" + 'self-dictation: ' + "\033[0m" + sentence)
    azure_system_speech(sentence, wait=False)
    MiniLM, sbert = models
    while True:
        instruction = input('(instruction):').strip().lower()
        instruction = re.sub(r'[,，;；、]', ' ', instruction)
        parse_instruction(corpus, MiniLM, sbert, instruction)
        # print('(instruction):', end='')


def main():
    print('\033[33mstarting...\033[0m')
    time.sleep(0.5)
    test_azure()
    language = get_language()
    from initialize import initialize

    corpus, MiniLM, sbert = initialize(language=language)

    self_dictation_loop(corpus, (MiniLM, sbert))


if __name__ == '__main__':
    try:
        from datetime import datetime
        from dictation import dictation_loop
        import re
        import os
        import time
        import sys

        main()
    except Exception as e:
        print(e)
        print()
        # print('目前工作路径:', os.getcwd())
        sentence = "There are some bugs, the above should be printed bug information,\n" \
                   "please report these information to TLHX, the author of this project."
        print('\033[31m' + sentence + '\033[0m')
        azure_system_speech(sentence)
        input()
