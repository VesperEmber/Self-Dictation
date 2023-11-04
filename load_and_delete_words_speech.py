from read_words import get_md5_hash_base62_encoded, get_corpus_path, read
import speech_synthesis
# from tqdm import tqdm
import os
import time


def load_word_speech(word, language='english', voice_name=None):
    # input('debug4')
    corpus_path = get_corpus_path(language=language)
    word_path = corpus_path + '/' + get_md5_hash_base62_encoded(word) + '.wav'
    if not os.path.exists(word_path) or voice_name:
        # input('debug5')
        speech_synthesis.azure_text_to_speech(word, language=language, to_file=True, voice_name=voice_name)
    else:
        print(f'Audio of \033[33m"{word}"\033[0m is \033[33malready existed\033[0m at',
              '\033[33m' + word_path + '\033[0m')


def load_words_speech_from_list(wordlist, language='english', voice_name=None):
    # for word in tqdm(wordlist, desc='Importing words'):
    #     input('debug3')
    #     load_word_speech(word, language=language, voice_name=voice_name)
    # for word in wordlist:
    for i in range(len(wordlist)):
        print(f'\033[31m({i + 1}/{len(wordlist)}): \033[0m', end='')
        load_word_speech(wordlist[i], language=language, voice_name=voice_name)
    time.sleep(1)
    # print('\ndebug')


def delete_speech_by_word(word, language='english'):
    corpus_path = get_corpus_path(language=language)
    word_path = corpus_path + '/' + get_md5_hash_base62_encoded(word) + '.wav'
    try:
        os.remove(word_path)
        print(f'Successfully deleted \033[33m"{word}"\033[0m audio: \033[33m"{word_path}"\033[0m')
    except:
        print(f'\033[33m"{word}"\033[0m has no audio: \033[33m"{word_path}"\033[0m to delete.')


def delete_speeches_by_wordlist(wordlist, language='english'):
    # for word in tqdm(wordlist):
    #     delete_speech_by_word(word, language=language)
    for i in range(len(wordlist)):
        print(f'\033[31m({i + 1}/{len(wordlist)}): \033[0m', end='')
        delete_speech_by_word(wordlist[i], language=language)
    time.sleep(1)


if __name__ == '__main__':
    pass
    # word_list = ['harbinger', 'light', 'lost', 'words']
    # load_words_speech_from_list(word_list, language='english')
    # for word in word_list:
    #     read(word, language='english')
