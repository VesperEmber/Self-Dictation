from judge_synonym import dictation_examination
from read_words import read
import sounddevice as sd
from scipy.io.wavfile import read as readwav
import os
import time
import re
from datetime import datetime


def count_down():
    time.sleep(0.5)
    print('\033[36m', end='')
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)
    print('\033[0m', end='')
    time.sleep(1)


def correct_sound(word_path='property/correct.wav', wait=True):
    if os.path.exists(word_path):
        rate, data = readwav(word_path)
        sd.play(data, rate)
        if wait:
            sd.wait()


def wrong_sound(word_path='property/wrong.wav', wait=True):
    if os.path.exists(word_path):
        rate, data = readwav(word_path)
        sd.play(data, rate)
        if wait:
            sd.wait()


def get_today():
    return str(datetime.now().date())


def dictation_loop(corpus, nums=0, smart_sample=True, meanings_only=False, MiniLM=None, sbert=None,
                   threshold_MiniLM=0.41, threshold_sbert=0.67):
    """
    听写程序的循环.
    给定单词本 corpus, 听写词数 nums, 是否智能抽词策略 smart_sample, 是否只考察单词意思 meanings_only,
    MiniLM 模型, sbert 模型, 以及两模型的语义相似度判别阈值后, 进入听写循环.
    :param corpus:
    :param nums:
    :param smart_sample:
    :param meanings_only:
    :param MiniLM:
    :param sbert:
    :param threshold_MiniLM:
    :param threshold_sbert:
    :return:
    """
    if corpus.corpus_size <= 0:
        print(f'\033[31mWarning: This "{corpus.language}" corpus is empty.\033[0m')
        return

        # 限制 nums 范围
    if nums <= 0 or nums > corpus.corpus_size:
        nums = corpus.corpus_size

    if MiniLM and sbert:
        sentence_model = 'Using \033[33mMiniLM\033[0m model and \033[33msbert\033[0m model for joint arbitration.'
    elif MiniLM:
        sentence_model = 'Only use \033[33mMiniLM\033[0m model for arbitration.'
    elif sbert:
        sentence_model = 'Only use \033[33msbert\033[0m model for arbitration.'
    else:
        sentence_model = 'None of the models were successfully loaded, the program will arbitrate using the \033[33mnaive string matching method\033[0m.\n' \
                         '\033[31mYour answers must match exactly the answers in the corpus.\033[0m'
    print('\033[33mDictation program start. The information of this dictation is:\033[0m')
    sample_algorithm = 'smart sample' if smart_sample else 'random sample'
    print(
        f'There are \033[33m{nums} words\033[0m in the test, sampled by using \033[33m"{sample_algorithm} algorithm"\033[0m.')
    sentence_test = 'This dictation will ' + (
        '\033[33monly test the meaning of words.\033[0m' if meanings_only else '\033[33mtest both spelling and meaning.\033[0m')
    print(sentence_test)
    print(sentence_model)
    count_down()
    print(f'\033[33mDictation begins!\033[0m')
    time.sleep(1)

    wordlist = corpus.smart_sample(nums) if smart_sample else corpus.random_sample(nums)
    wronglist = []  # 本次听写错误单词列表
    for i in range(nums):
        spell_correct = True
        # 拼写考察
        if not meanings_only:  # 即也考察拼写, 需要读出单词发音
            chances = 2
            word = wordlist[i]
            case_sensitivity = corpus.corpus[wordlist[i]]['case_sensitivity']
            if case_sensitivity:
                print('Note: This word is \033[36mcase sensitive.\033[0m')
            if ' ' in word:
                print('Note: This is a \033[36mphrase.\033[0m')
            while chances > 0:
                if chances == 1:
                    print('\033[33mYou only have one last chance.\033[0m')
                repeat = True
                while True:  # 获取 spell
                    if repeat:  # 默认 repeat 是 True, 即新词一上来会读
                        read(wordlist[i], language=corpus.language)
                    spell = input(f'({i + 1}/{nums}) (spell):').strip()
                    if spell == '':  # 处理单纯按下回车键的情况, 然而此时不应该重读单词
                        repeat = False
                    elif spell.lower() == '$repeat':  # 可以用 $repeat 命令要求重新读
                        repeat = True
                    else:
                        break
                if not case_sensitivity:  # 大小写不敏感
                    spell, word = spell.lower(), word.lower()
                if spell == word:
                    correct_sound(wait=False)
                    spell_correct = True  # 拼写正确
                    break
                else:
                    spell_correct = False
                    wrong_sound(wait=False)
                    chances -= 1  # 少一次机会
                    time.sleep(0.5)  # 睡 0.5 秒, 避免错误提示音后立刻播放单词
            # 已跳出 while 循环, spell_correct 反映是否拼写正确, 若错误, 则应当给出正确拼写以加深印象
            if not spell_correct:
                print("\033[33mI'm sorry to learn that you didn't spell it correctly.\033[0m")
                print(f"The correct spelling is: \033[33m\"{wordlist[i]}\"\033[0m")
        else:  # 只考察含义, 此时需要程序给出这个词
            print("\033[32m" + 'self-dictation:' + "\033[0m", wordlist[i])

        chances = 2
        dictation_correct = True
        # 含义考察
        while chances > 0:
            if chances == 1:
                print('\033[33mYou only have one last chance.\033[0m')
            while True:  # 处理一下单纯按回车键, 输入为空的情况, 这可能是用户误触
                input_meanings = input(f'({i + 1}/{nums}) (meanings):').strip()
                if input_meanings:
                    break
            input_meanings = re.sub(r'[,，;；、]', ' ', input_meanings).split()  # input_meanings 就是输入意思的列表
            corpus_meanings = corpus.corpus[wordlist[i]]['meanings']  # corpus_meanings 就是该词汇在 corpus 中的含义列表
            input_meanings_wrong, corpus_meanings_missed = dictation_examination(input_meanings=input_meanings,
                                                                                 corpus_meanings=corpus_meanings,
                                                                                 MiniLM=MiniLM, sbert=sbert,
                                                                                 threshold_MiniLM=threshold_MiniLM,
                                                                                 threshold_sbert=threshold_sbert)
            if not input_meanings_wrong and not corpus_meanings_missed:  # 两个列表都是空的
                # 这个相当于全对
                dictation_correct = True
            else:  # 否则至少有一个列表有东西, 这种情况下就是含义默写错误了
                dictation_correct = False
                if input_meanings_wrong:  # 输入的意思列表中有错的
                    print(f'\033[31mThose "{", ".join(input_meanings_wrong)}" are incorrect.\033[0m')
                if corpus_meanings_missed:  # 正确意思列表中有未命中的, 即输入列表中有没写到的
                    print(f'\033[31mThere are {len(corpus_meanings_missed)} meanings missing.\033[0m')

            if dictation_correct:  # 听写结果正确
                correct_sound()
                break
            else:
                wrong_sound()
                chances -= 1
                # time.sleep(1)

        # 更新单词本中的词汇被考察相关的信息
        corpus.corpus[wordlist[i]]['last_test_date'] = get_today()
        corpus.corpus[wordlist[i]]['test_times'] += 1

        print(f'\033[36m{wordlist[i]}: {", ".join(corpus.corpus[wordlist[i]]["meanings"])}\033[0m')
        # 如果是 meanings_only=True, 即只考察意思, 不考察拼写, 则也能判断通过. 因为 spell_correct 默认为 True
        if spell_correct and dictation_correct:  # 这个词答对了
            corpus.corpus[wordlist[i]]['correct'] += 1
            # print(f'\033[33m{wordlist[i]}: {", ".join(corpus.corpus[wordlist[i]]["meanings"])}\033[0m')
            if i < nums:  # 接下来还有词
                print('\033[33mGood job! Next word.\033[0m')
        else:  # spell_correct 或 dictation_correct 中任意一个有错, 则这个单词就算错了
            # print(f'\033[36m{wordlist[i]}: {", ".join(corpus.corpus[wordlist[i]]["meanings"])}\033[0m')
            wronglist.append(wordlist[i])
            corpus.corpus[wordlist[i]]['wrong'] += 1

    correct_nums = nums - len(wronglist)
    if nums != 0:
        print(
            f'\033[33mDictation is over, correct rate: {round(correct_nums / nums * 100, 2)}% ({correct_nums}/{nums})\033[0m')
    else:
        print('No words!')

    corpus.refresh()  # 听写完之后先更新一下目前手持的单词本
    # 然后再询问是否要写回主单词本的json文件
    print('\nWould you like to update this dictation into the main corpus?')
    while True:
        update_main_corpus = input('(y/n):').strip().lower()
        if update_main_corpus in ['y', 'n']:
            if update_main_corpus == 'y':
                corpus.save_corpus_changes()
            break


# dictation_examination(input_meanings, corpus_meanings, MiniLM=None, sbert=None,


#                       threshold_MiniLM=0.4, threshold_sbert=0.6):


if __name__ == '__main__':
    # print(get_today())
    while True:
        x = input('input:')
        if x == '1':
            correct_sound()
        else:
            wrong_sound()
