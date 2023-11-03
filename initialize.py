import os
import json
from transformers import AutoTokenizer, AutoModel
from Corpus_class import Corpus
# import sys
import time


def initialize(**kwargs):
    """
    初始化, 若无 utterances 文件夹及其子文件或无 vocabulary 文件夹及其子文件, 则创建.
    若无 speech 的配置文件 config.json 则创建.
    尝试从本地目录加载语义相似度模型及分词器 MiniLM, sbert, 它们是两个元组 (tokenizer, model)

    :param kwargs:
    :return:
    """
    print("\033[33m" + 'initializing...')

    if not os.path.exists('vocabulary'):
        os.makedirs('vocabulary')
        print('makedirs: vocabulary')
    if not os.path.exists('utterances'):
        os.makedirs('utterances')
        print('makedirs: utterances')
    for language in ['chinese', 'english', 'japanese', 'german', 'french']:
        if not os.path.exists('vocabulary/' + language):
            os.makedirs('vocabulary/' + language)
            print('makedirs: vocabulary/' + language)
        if not os.path.exists('utterances/' + language):
            os.makedirs('utterances/' + language)
            print('makedirs: utterances/' + language)
        if not os.path.exists('vocabulary/' + language + '/' + 'corpus.json'):
            json_file_name = 'vocabulary/' + language + '/' + 'corpus.json'
            print('makedirs:', json_file_name)
            data = {}
            with open(json_file_name, "w", encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False)

    for key in ['SPEECH_KEY', 'SPEECH_REGION']:
        kwargs[key] = kwargs.get(key, None)

    kwargs['language'] = kwargs.get('language', 'english')
    kwargs['voice_name'] = kwargs.get('voice_name', {
        "english": "en-US-JennyNeural",
        "chinese": "zh-CN-XiaoxiaoNeural",
        "japanese": "ja-JP-NanamiNeural",
        "german": "de-DE-KatjaNeural",
        "french": "fr-FR-DeniseNeural"
    })
    kwargs['save_path'] = kwargs.get('save_path', os.getcwd().replace('\\', '/') + '/utterances')
    # print(kwargs)
    speech_config_path = 'speech_config.json'
    if not os.path.exists(speech_config_path):
        print('makedir:', speech_config_path)
        with open(speech_config_path, "w", encoding='utf-8') as json_file:
            json.dump(kwargs, json_file, indent=4, ensure_ascii=False)
    # 根据 initialize 方法飞给定的 language 载入单词本(若没给 language 则默认是 english)
    with open(f'vocabulary/{kwargs["language"]}/corpus.json', "r", encoding='utf-8') as json_file:
        corpus = json.load(json_file)

    corpus_hold = Corpus(corpus, language=kwargs['language'])
    if corpus_hold.corpus_size == 0:
        print(f'main "{kwargs["language"]}" corpus is empty.')

    # 从本地目录加载模型和分词器
    # current_dir = os.getcwd().replace('\\', '/')
    # print(current_dir)
    # current_script_path = os.path.abspath(sys.executable)
    # current_dir = os.path.dirname(current_script_path)
    current_dir = os.getcwd()

    MiniLM_path = current_dir + '/judge_synonym_model/models--sentence-transformers--all-MiniLM-L6-v2' \
                                '/snapshots/7dbbc90392e2f80f3d3c277d6e90027e55de9125'
    sbert_path = current_dir + '/judge_synonym_model/models--DMetaSoul--sbert-chinese-general-v1-distill' \
                               '/snapshots/7f20ecf1db8f800b6a1592e6e9de8b5b78d598ab'
    MiniLM, sbert = None, None
    time.sleep(0.5)
    try:
        tokenizer_MiniLM = AutoTokenizer.from_pretrained(MiniLM_path)
        model_MiniLM = AutoModel.from_pretrained(MiniLM_path)
        MiniLM = (tokenizer_MiniLM, model_MiniLM)
        print('MiniLM model successfully loaded.')
    except Exception as e:
        print(e)
        print('failed to load the MiniLM model.')

    try:
        tokenizer_sbert = AutoTokenizer.from_pretrained(sbert_path)
        model_sbert = AutoModel.from_pretrained(sbert_path)
        sbert = (tokenizer_sbert, model_sbert)
        print('sbert model successfully loaded.')
    except Exception as e:
        print(e)
        print('failed to load the sbert model.')

    if MiniLM and sbert:
        print('both MiniLM model and sbert model will be used for joint arbitration.')
    elif MiniLM:
        print('only MiniLM model will be used for arbitration.')
    elif sbert:
        print('only sbert model will be used for arbitration.')
    else:
        print(
            'none of the models were successfully loaded, the program will arbitrate using the naive string matching method.')

    print('initialization complete.' + "\033[0m")
    return corpus_hold, MiniLM, sbert


if __name__ == "__main__":
    initialize()
