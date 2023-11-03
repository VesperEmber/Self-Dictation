import json
import os
import load_and_delete_words_speech
from datetime import datetime
import re
import sys


def get_project_path():
    # current_script_path = os.path.abspath(__file__)
    # current_script_path = os.path.abspath(sys.executable)
    # project_path = os.path.dirname(current_script_path).replace('\\', '/')
    project_path = os.getcwd()
    return project_path


def get_speech_config_path():
    # current_script_path = os.path.abspath(__file__)
    # current_script_path = os.path.abspath(sys.executable)
    # current_script_directory = os.path.dirname(current_script_path)
    current_script_directory = os.getcwd()
    speech_config_path = current_script_directory + '/speech_config.json'
    speech_config_path = os.path.normpath(speech_config_path).replace('\\', '/')
    return speech_config_path


def get_speech_config_dt():
    with open(get_speech_config_path(), "r", encoding='utf-8') as json_file:
        speech_config_dt = json.load(json_file)
    return speech_config_dt


def new_word(word, meanings, language='english', import_date=str(datetime.now().date()), voice_name=None,
             case_sensitivity=False, tag=None):
    # 保证 tag 一定为 list
    if not tag:
        tag = []
    if isinstance(tag, str):
        tag = [tag]
    if not voice_name:
        voice_name = get_speech_config_dt()["voice_name"][language]
    new_element = {word: {  # 单词如 'commit'
        "language": language,
        "meanings": meanings,  # 意思列表, 如 ['承诺', '犯下', '投入', '交付', '致力于']
        "voice_name": voice_name,
        "import_date": import_date,  # str格式的时间，如 '2023-10-23'
        "last_test_date": None,  # str格式的时间，如 '2023-10-23'
        "test_times": 0,  # 考核次数
        "correct": 0,  # 正确次数
        "wrong": 0,  # 错误次数
        "case_sensitivity": case_sensitivity,  # 大小写敏感性
        "tag": tag  # 词汇标签列表, 如 ['GRE', 'IELTS', 'my_tag']
    }}
    return new_element


def load_words(words, meanings, language='english', import_date=str(datetime.now().date()), voice_name=None,
               case_sensitivity=False, tag=None):
    """
    导入一个单词
    :param word:
    :param language:
    :param voice_name:
    :return:
    """
    if not words:
        print('There are no words that have been asked to load')
        return

    corpus_path = get_project_path() + '/vocabulary/' + language + '/corpus.json'
    with open(corpus_path, "r", encoding='utf-8') as json_file:
        corpus = json.load(json_file)

    revise_num, update_num = 0, 0
    if not isinstance(words, str):  # 多个单词导入
        for i in range(len(words)):
            # 此时 words 和 meanings 都是 list
            new_element = new_word(words[i], meanings[i], language=language, import_date=import_date,
                                   voice_name=voice_name, case_sensitivity=case_sensitivity, tag=tag)
            # revise 提示
            if words[i] in corpus.keys():
                # print(f'"{language}" word "{words[i]}" has been revised')
                print(f'\033[33m"{words[i]}"\033[0m has been revised.')
                revise_num += 1
            # update 提示
            else:
                # print(f'"{language}" word "{words[i]}" has been loaded into "{language}" corpus')
                print(f'\033[33m"{words[i]}"\033[0m has been loaded into main \033[33m"{language}"\033[0m corpus.')
                update_num += 1
            corpus.update(new_element)
        # input('debug1')
        # 这个放在 load_words_from_txt 中写
        # load_and_delete_words_speech.load_words_speech_from_list(words, language=language, voice_name=voice_name)
    else:  # 一个单词导入
        new_element = new_word(words, meanings, language=language, import_date=import_date,
                               voice_name=voice_name, case_sensitivity=case_sensitivity, tag=tag)
        # revise 提示
        if words in corpus.keys():
            print(f'\033[33m"{words}"\033[0m has been revised.')
            revise_num += 1
        # update 提示
        else:
            print(f'\033[33m"{words}"\033[0m has been loaded into main \033[33m"{language}"\033[0m corpus.')
            update_num += 1
        corpus.update(new_element)

        # 这个放在 load_words_from_txt 中写
        # load_and_delete_words_speech.load_word_speech(words, language=language, voice_name=voice_name)

    # 将修改后的数据写回 JSON 文件
    with open(corpus_path, "w", encoding='utf-8') as json_file:
        json.dump(corpus, json_file, indent=4, ensure_ascii=False)
    # print(f'\033[33mImport successfully, {update_num} words imported, {revise_num} words revised.\033[0m')


def load_words_from_txt(filepath):
    if not os.path.exists(filepath):
        print("\033[31mWarning: " + filepath, 'not exists.\033[0m')
        return
    wordlist, meanings = [], []
    language = 'english'
    import_date = str(datetime.now().date())
    voice_name = None
    case_sensitivity = False
    tag = []
    # 在文档中支持设置的导入参数列表
    params_list = ['language', 'import_date', 'voice_name', 'case_sensitivity', 'tag']
    # True 表示目前扫过每行为待读入的单词, False 表示目前每行为读入设置的相关参数
    read_words_mode = True  # 默认是读入单词模式

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):  # 把//解释为注释
                continue
            # 解析命令
            if line.startswith('#') or line.startswith('$'):  # order line 这是一行命令
                order = line[1:].strip()
                if 'parameter' in order.lower():  # 进入读参数模式
                    read_words_mode = False
                elif 'word' in order.lower():  # 进入读单词模式
                    read_words_mode = True
                else:
                    print(
                        f'\033[31mImport failed, "# {order}" in an invalid order, please check your import file and use "# parameter" or "# wordlist" instead.\033[0m')
                    return
                continue  # 解析完命令后继续读下一行
            # 读单词
            if read_words_mode:
                pt1 = r'[:：]+'
                try:
                    word, meaning = map(lambda x: x.strip(), re.split(pt1, line))
                except Exception as e:
                    print(
                        f'\033[31mImport failed, there must be words and their meanings are not separated by ":", please check your import file.\033[0m')
                    return
                pt2 = r'[,，;； 、。]+'
                meaning = re.split(pt2, meaning)
                wordlist.append(word)
                meanings.append(meaning)

                # 这里改成一词一导, 便于在一个 wordlist 中多次修改不同的参数
                load_words(word, meaning, language=language, import_date=import_date, voice_name=voice_name,
                           case_sensitivity=case_sensitivity, tag=tag)
            # 读参数
            else:  # 读参数
                pt1 = r'[:：=]+'  # 分割 parameter 和其 value
                key, value = map(lambda x: x.strip(), re.split(pt1, line))
                pt2 = r'\s+'  # 给 parameter 替换空格为_
                key_normalized = re.sub(pt2, '_', key).lower()
                if key_normalized not in params_list:  # 保证 key_normalized 是合法的
                    print(f'\033[31mImport failed, "{key}" is an invalid parameter.\033[0m')
                    return

                if key_normalized == 'language':
                    language = value.lower()
                elif key_normalized == 'case_sensitivity':
                    value = [False, True][value.lower() == 'true']
                    case_sensitivity = value
                elif key_normalized == 'tag':
                    pt3 = r'[,，;； 、]+'  # 分割 tag
                    value = re.split(pt3, value)
                    tag = value
                elif key_normalized == 'import_date':
                    import_date = value
                elif key_normalized == 'voice_name':
                    voice_name = value

    # load_words(wordlist, meanings, language=language, import_date=import_date, voice_name=voice_name,
    #            case_sensitivity=case_sensitivity, tag=tag)
    load_and_delete_words_speech.load_words_speech_from_list(wordlist, language=language, voice_name=voice_name)
    # print(f'\033[33mImport successfully, {len(wordlist)} words were successfully imported into main "{language}" corpus.\033[0m')
    print(
        f'However, the corpus you are holding will not be affected, if you want to use the latest corpus, use the command \033[33m"corpus reload {language}".\033[0m')


def load_words_from_corpus(sub_corpus: dict, language='english'):
    """
    将 sub_corpus 中的单词信息更新回全局单词本 corpus
    :param sub_corpus: sub_corpus 是个已改动单词相关信息的子单词本
    :return: 无
    """
    # 获取全局单词本 corpus
    corpus_path = get_project_path() + '/vocabulary/' + language + '/corpus.json'
    with open(corpus_path, "r", encoding='utf-8') as json_file:
        corpus = json.load(json_file)
    # 用 sub_corpus 更新 corpus
    corpus.update(sub_corpus)
    # 将修改后的数据写回 JSON 文件
    with open(corpus_path, "w", encoding='utf-8') as json_file:
        json.dump(corpus, json_file, indent=4, ensure_ascii=False)
    # print(f'\033[33msub-corpus has been updated back to the "{language}" corpus.\033[0m')
    print(f'\033[33mCorpus has been updated back to the main "{language}" corpus.\033[0m')


def delete_words(words, language='english'):
    if not words:
        print('There are no words that have been asked to delete')
        return
    corpus_path = get_project_path() + '/vocabulary/' + language + '/corpus.json'
    with open(corpus_path, "r", encoding='utf-8') as json_file:
        corpus = json.load(json_file)

    delete_num = 0
    if not isinstance(words, str):  # 多个单词删除, words是个word的list
        for i in range(len(words)):
            # 此时 words 是 list
            del_result = corpus.pop(words[i], None)
            # 成功 delete 提示
            if del_result:
                print(f'\033[33m"{words[i]}" has been deleted from "{language}" corpus.\033[0m')
                delete_num += 1
            # 不存在 words[i] 提示
            else:
                print(f'\033[33mThere is no "{words[i]}" to delete.\033[0m')
        load_and_delete_words_speech.delete_speeches_by_wordlist(words, language=language)
    else:  # 一个单词删除, 此时 words 是个 str
        del_result = corpus.pop(words, None)
        # 成功 delete 提示
        if del_result:
            print(f'\033[33m"{words}" has been deleted from "{language}" corpus.\033[0m')
            delete_num += 1
        # 不存在 words 提示
        else:
            print(f'\033[33mThere is no "{words}" to delete.\033[0m')
        load_and_delete_words_speech.delete_speech_by_word(words, language=language)

    # 将修改后的数据写回 JSON 文件
    with open(corpus_path, "w", encoding='utf-8') as json_file:
        json.dump(corpus, json_file, indent=4, ensure_ascii=False)
    print(f'\033[33m{delete_num} words deleted.\033[0m')


def delete_words_from_txt(filepath):
    if not os.path.exists(filepath):
        print(filepath, 'not exists')
        return
    language = 'english'
    wordlist = []
    # True 表示目前扫过每行为待读入的单词, False 表示目前每行为读入设置的相关参数
    read_words_mode = True  # 默认是读入单词模式
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):  # 把//解释为注释
                continue
            # 解析命令
            if line.startswith('#') or line.startswith('$'):  # order line 这是一行命令
                order = line[1:].strip()
                if 'parameter' in order.lower():  # 进入读参数模式
                    read_words_mode = False
                elif 'word' in order.lower():  # 进入读单词模式
                    read_words_mode = True
                else:
                    # print(f'"# {order}" in an invalid order, please use "# parameter" or "# wordlist" instead')
                    print(
                        f'\033[31mDelete failed, "# {order}" in an invalid order, please check your delete file and use "# parameter" or "# wordlist" instead.\033[0m')
                    return
                continue  # 解析完命令后继续读下一行
            # 读单词
            if read_words_mode:
                word = line
                wordlist.append(word)
            # 读参数
            else:
                pt1 = r'[:：=]+'  # 分割 parameter 和其 value
                key, value = map(lambda x: x.strip(), re.split(pt1, line))
                key_normalized = key.lower()
                if key_normalized != 'language':  # 保证 key_normalized 是合法的
                    # print(f'"{key}" is an invalid parameter')
                    print(f'\033[31mDelete failed, "{key}" is an invalid parameter.\033[0m')
                    return
                else:
                    language = value.lower()

    delete_words(wordlist, language=language)
    print(
        f'\033[33mHowever, the corpus you are holding will not be affected, if you want to use the latest corpus, use the command "corpus reload {language}".\033[0m')


if __name__ == '__main__':
    print(get_speech_config_path())
    print(get_project_path())
    pass
    # load_words_from_txt('wordlist_load_test.txt')
    # delete_words('tape')
    # delete_words_from_txt('wordlist_delete_test.txt')
    # load_words_from_txt('wordlist_delete_test.txt')
    # sub_corpus = {"replenish": {
    #     "language": "english",
    #     "meanings": [
    #         "重新装满"
    #     ],
    #     "voice_name": "en-US-JennyNeural",
    #     "import_date": "2023-10-23",
    #     "last_test_date": None,
    #     "test_times": 0,
    #     "correct": 0,
    #     "wrong": 0,
    #     "case_sensitivity": False,
    #     "tag": [
    #         "GRE",
    #         "CET6",
    #         "CET4"
    #     ]
    # }}
    # print(sub_corpus)
    # load_words_from_corpus(sub_corpus)
