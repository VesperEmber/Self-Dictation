import torch
# from torch import sum, clamp, no_grad, tensor
# import torch.nn.functional as F
from torch.nn import functional as F
from scipy.spatial.distance import cosine


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    # return sum(token_embeddings * input_mask_expanded, 1) / clamp(input_mask_expanded.sum(1), min=1e-9)


def calculate_embeddings(wordlist, tokenizer, model):
    # Tokenize sentences
    encoded_input = tokenizer(wordlist, padding=True, truncation=True, return_tensors='pt')
    # Compute token embeddings
    with torch.no_grad():
    # with no_grad():
        model_output = model(**encoded_input)
    # Perform pooling
    wordlist_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    # Normalize embeddings
    wordlist_embeddings = F.normalize(wordlist_embeddings, p=2, dim=1)
    return wordlist_embeddings


def calculate_similarity_matrix(wordlist1, wordlist2, tokenizer, model):
    """
    计算 wordlist1 中每个词汇与 wordlist2 中每个词汇的 similarity matrix
    similarity_matrix[i][j] 是 wordlist1[i] 与 wordlist2[j] 的 similarity
    :param wordlist1: 听写输入的意思列表
    :param wordlist2: 单词本中记录的原始意思列表
    :param tokenizer: 使用的 tokenizer
    :param model: 使用的 model
    :return: torch.tensor 类型的相似度矩阵张量 similarity_matrix
    similarity_matrix[i][j] 是 wordlist1[i] 与 wordlist2[j] 的 similarity
    """
    wordlist1_embeddings = calculate_embeddings(wordlist1, tokenizer, model)
    wordlist2_embeddings = calculate_embeddings(wordlist2, tokenizer, model)
    similarity_matrix = []
    for i in range(len(wordlist1_embeddings)):
        similarity_wordlist1_i_wordlist2 = [1 - cosine(wordlist1_embeddings[i].numpy(), embedding.numpy()) for embedding
                                            in wordlist2_embeddings]
        similarity_matrix.append(similarity_wordlist1_i_wordlist2)
    return torch.tensor(similarity_matrix)
    # return tensor(similarity_matrix)



def matching(input_meanings, corpus_meanings, input_matched, corpus_matched):
    input_meanings_wrong = [input_meanings[i] for i in range(len(input_matched)) if not input_matched[i]]
    corpus_meanings_missed = [corpus_meanings[i] for i in range(len(corpus_matched)) if not corpus_matched[i]]
    return input_meanings_wrong, corpus_meanings_missed


def dictation_examination(input_meanings, corpus_meanings, MiniLM=None, sbert=None,
                          threshold_MiniLM=0.4, threshold_sbert=0.6):
    """
    当成功加载两个近义词检测模型时，将使用两模型联合仲裁听写检查，即只有两模型都认为写对了，才算对。
    当仅加载其中任何一个近义词检测模型时，使用该模型仲裁。
    当未加载任何一个语言模型时，采用朴素的字符串匹配方式做听写检查。
    :param input_meanings: 听写输入的意思列表
    :param corpus_meanings: 单词本中记录的原始意思列表
    :param MiniLM: MiniLM[0] 为其 tokenizer, MiniLM[1] 为其 model
    :param sbert: sbert[0] 为其 tokenizer, sbert[1] 为其 model
    :param threshold_MiniLM: 使用 MiniLM 模型计算语义相似度, 判断为同义词的阈值
    :param threshold_sbert: 使用 sbert 模型计算语义相似度, 判断为同义词的阈值
    :return: (input_meanings_wrong, corpus_meanings_missed): tuple
             input_meanings_wrong(输入的意思中未匹配上正确意思的, 也就是画蛇添足写多了的意思的列表),
             corpus_meanings_missed(词库中正确的意思中未被匹配的, 也就是没写出来的意思的列表),
    """
    # 限制仲裁阈值的合理范围：仲裁阈值应当小于等于 1
    threshold_MiniLM, threshold_sbert = min(threshold_MiniLM, 1), min(threshold_sbert, 1)
    # 没有成功载入任何一个模型
    if not MiniLM and not sbert:
        # 使用朴素的字符串匹配做听写检查
        input_matched, corpus_matched = [False] * len(input_meanings), [False] * len(corpus_meanings)
        # print('没有成功载入任何一个模型, 使用朴素的字符串匹配做听写检查')
        for i in range(len(input_meanings)):
            for j in range(len(corpus_meanings)):
                if input_meanings[i] == corpus_meanings[j]:
                    input_matched[i], corpus_matched[j] = True, True
    elif MiniLM and sbert:  # 两个模型均已成功载入
        # print('两个模型均已成功载入, 使用两模型联合仲裁听写检查')
        tokenizer_MiniLM, model_MiniLM = MiniLM
        tokenizer_sbert, model_sbert = sbert
        similarity_matrix_MiniLM = calculate_similarity_matrix(input_meanings, corpus_meanings, tokenizer_MiniLM,
                                                               model_MiniLM)
        similarity_matrix_sbert = calculate_similarity_matrix(input_meanings, corpus_meanings, tokenizer_sbert,
                                                              model_sbert)
        # vote_matrix 是两模型共同投票仲裁得出的结果
        # print(f'threshold_MiniLM = {threshold_MiniLM}, threshold_sbert = {threshold_sbert}')
        vote_matrix = (similarity_matrix_MiniLM > threshold_MiniLM) * (similarity_matrix_sbert > threshold_sbert)
        input_matched = vote_matrix.sum(dim=1).bool()
        corpus_matched = vote_matrix.sum(dim=0).bool()
    else:  # 仅成功载入了其中一个模型，即另一个模型是None，故可以用(MiniLM or sbert)取得该模型
        # print('仅加载一个近义词检测模型，使用该模型仲裁')
        tokenizer, model = (MiniLM or sbert)
        similarity_matrix = calculate_similarity_matrix(input_meanings, corpus_meanings, tokenizer, model)
        # threshold 取二者最大值的几何平均值, 可以保证其比二者最大的都要更大一些，且小于 1
        # 这样考虑是因为只有一个模型仲裁，需要更严格一些以逼近两模型仲裁的效果
        threshold = max(threshold_MiniLM, threshold_sbert) ** 0.5
        # print(f'threshold = {threshold}')
        vote_matrix = similarity_matrix > threshold
        input_matched = vote_matrix.sum(dim=1).bool()
        corpus_matched = vote_matrix.sum(dim=0).bool()

    return matching(input_meanings, corpus_meanings, input_matched, corpus_matched)


if __name__ == '__main__':
    import random

    input_meanings = ['修剪']
    corpus_meanings = ['裁剪']
    random.shuffle(input_meanings)
    print(input_meanings)

    # matching(input_meanings, corpus_meanings, input_matched, corpus_matched)

    input_meanings_wrong, corpus_meanings_missed = dictation_examination(input_meanings, corpus_meanings)
    print('input_meanings_wrong:', input_meanings_wrong)
    print('corpus_meanings_missed:', corpus_meanings_missed)

    from transformers import AutoTokenizer, AutoModel
    import os

    current_dir = os.getcwd().replace('\\', '/')
    MiniLM_path = current_dir + '/judge_synonym_model/models--sentence-transformers--all-MiniLM-L6-v2' \
                                '/snapshots/7dbbc90392e2f80f3d3c277d6e90027e55de9125'
    sbert_path = current_dir + '/judge_synonym_model/models--DMetaSoul--sbert-chinese-general-v1-distill' \
                               '/snapshots/7f20ecf1db8f800b6a1592e6e9de8b5b78d598ab'

    # 从本地目录加载模型和分词器
    tokenizer_MiniLM = AutoTokenizer.from_pretrained(MiniLM_path)
    model_MiniLM = AutoModel.from_pretrained(MiniLM_path)
    MiniLM = (tokenizer_MiniLM, model_MiniLM)

    tokenizer_sbert = AutoTokenizer.from_pretrained(sbert_path)
    model_sbert = AutoModel.from_pretrained(sbert_path)
    sbert = (tokenizer_sbert, model_sbert)

    input_meanings_wrong, corpus_meanings_missed = dictation_examination(input_meanings, corpus_meanings, MiniLM=MiniLM,
                                                                         sbert=sbert)
    print('input_meanings_wrong:', input_meanings_wrong)
    print('corpus_meanings_missed:', corpus_meanings_missed)

    input_meanings_wrong, corpus_meanings_missed = dictation_examination(input_meanings, corpus_meanings, MiniLM=MiniLM)
    print('input_meanings_wrong:', input_meanings_wrong)
    print('corpus_meanings_missed:', corpus_meanings_missed)

    input_meanings_wrong, corpus_meanings_missed = dictation_examination(input_meanings, corpus_meanings, sbert=sbert)
    print('input_meanings_wrong:', input_meanings_wrong)
    print('corpus_meanings_missed:', corpus_meanings_missed)
