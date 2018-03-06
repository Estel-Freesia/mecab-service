#!/bin/python3
from flask import Flask, jsonify, abort, request
import MeCab

app = Flask(__name__)

messages = ['Success', 'Faild']


@app.route('/mecab/v1/parse-ipadic', methods=['POST'])
def parse():
    if not (request.json and 'sentence' in request.json):
        abort(400)

    sentence = request.json['sentence']
    if ('nbest' in request.json and (isinstance(request.json['nbest'], int) or request.json['nbest'].isdigit())):
        nbest = int(request.json['nbest'])
    else:
        nbest = 1

    results = mecab_parse(sentence, nbest)

    return mecab_response(200, messages[0], nbest, results, 'ipadic')



@app.route('/mecab/v1/parse-neologd', methods=['POST'])
def parse_neologd():
    if not (request.json and 'sentence' in request.json):
        abort(400)

    sentence = request.json['sentence']
    if ('nbest' in request.json and (isinstance(request.json['nbest'], int) or request.json['nbest'].isdigit())):
        nbest = int(request.json['nbest'])
    else:
        nbest = 1

    results = mecab_parse(sentence, nbest, 'neologd')

    return mecab_response(200, messages[0], nbest, results, 'neologd')


@app.errorhandler(400)
def error400(error):
    return mecab_response(400, messages[1], None, None, None)


def mecab_response(status, message, nbest, results, dic):
    return jsonify({'status': status, 'message': message, 'nbest': nbest, 'results': results, 'dict': dic}), status


def mecab_parse(sentence, nbest, dic='ipadic'):
    dic_dir = "/usr/local/lib/mecab/dic/"
    if dic == 'neologd':
        dic_name = 'mecab-ipadic-neologd'
    else:
        dic_name = dic

    m = MeCab.Tagger('-l 1 -d ' + dic_dir + dic_name)

    # 出力フォーマット（デフォルト）
    format = ['表層形', '品詞','品詞細分類1', '品詞細分類2', '品詞細分類3', '活用形', '活用型','原型','読み','発音']

    n = 0
    r = []
    results = []
    for p in m.parseNBest(nbest, sentence).split('\n')[:-1]:
        if p == 'EOS':
            results.append({'id': n, 'items': r})
            r = []
            n += 1
        else:
            r.append(dict(zip(format, (lambda x: [x[0]]+x[1].split(','))(p.split('\t')))))

    return results


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

