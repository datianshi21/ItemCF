#!/usr/bin/env python
# coding=utf-8
#########################################################################
# File Name:    item_recommendation.py
# Author:       hongchunxiao
# mail:         hongchunxiao@gmail.com
# Created  Time: 2013/12/28 21:59:08 (Saturday December)
# Modified Time: 2013/12/28 21:59:08 (Saturday December)
#
# Description:
#########################################################################
import sys
import math
from operator import itemgetter

"""
input format:
---user1 item1
---user1 item2
---user2 item1
"""

def do_item_recom(train_file, test_file, k, model_file, result_file_name, N) :
    train = get_data_set(train_file)
    print 'read train data ok!'
    test = get_data_set(test_file) #test set
    print 'read test data ok!'
    sim = item_similarity(train, k)
    print 'train model ok!'
    write_model2file(sim, model_file)
    write_result2file(sim, train, test, N, result_file_name)

    hit, all, prec = precision(sim, train, test, N)
    print 'precision@%d = %d/%d = %f' %(N, hit, all, prec)
    hit, all, rec = recall(sim, train, test, N)
    print 'recall@%d = %d/%d = %f' %(N, hit, all, rec)

#sim： 对每个item，保存和它最相似的k个item的相似度
def recommendation(train, user_id, sim, N) :
    rank = {}
    if user_id not in train :
        return rank
    history = train[user_id]
    total = 0.0
    for item in history : #历史看过的item
        if item in sim :
            for other_item, sim_i_j in sim[item] :
                total += sim_i_j
                if other_item in history :
                    continue
                rank.setdefault(other_item, 0)
                rank[other_item] += sim_i_j
    for recom_item in rank :
        rank[recom_item] /= total #归一化
    
    rank = sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]
    return rank

def write_result2file(sim, train, test, N, result_file_name) :
    result_file = open(result_file_name, 'w')
    total_recom = 0
    total_obj = 0
    for user in train.keys():
        rank = recommendation(train, user, sim, N)
        predict_items_str = ''
        for item, pui in rank :
            predict_items_str = predict_items_str + item + ':' + str(pui) + ','
        obj_items_str = ''
        if user in test :
            for item in test[user] :
                obj_items_str = obj_items_str + item + ','
            total_obj += len(test[user])
        fortmat_str = '%s\t%s\t%s\t\n' %(user, predict_items_str[0:len(predict_items_str)-1], obj_items_str[0:len(obj_items_str)-1])
        result_file.write(fortmat_str)
        total_recom += len(rank)
    print 'total_recom = %d' %(total_recom)
    for user in test.keys() :
        if user not in train:
            obj_items_str = ''
            for item in test[user] :
                obj_items_str = obj_items_str + item + ','
            fortmat_str = '%s\t%s\t%s\t\n' %(user, '', obj_items_str[0:len(obj_items_str)-1])
            total_obj += len(test[user])
            result_file.write(fortmat_str)
    print 'total_obj = %d' %(total_obj)
    result_file.close()

def recall(sim, train, test, N) :
    hit = 0
    all = 0
    for user in test.keys() :
        tu = test[user]
        rank = recommendation(train, user, sim, N)
        for item, pui in rank :
            if item in tu :
                hit += 1
        all += len(tu)
    return hit, all, hit / (all * 1.0)

def precision(sim, train, test, N) :
    hit = 0
    all = 0
    for user in train.keys() :
        rank = recommendation(train, user, sim, N)
        if user in test :
            tu = test[user]
            for item, pui in rank :
                if item in tu :
                    hit += 1
        all += len(rank)
    return hit, all, hit / (all * 1.0)


#对每个item，返回topk个最相似的item
def item_similarity(train, k) :
    item2item_num = {} #item与item在被多少用户共同浏览过
    item_len_dict = {} #item被多少用户浏览过
    for user, items in train.items() :
        for item in items :
            item_len_dict.setdefault(item, 0)
            item_len_dict[item] += 1
            for other_item in items :
                if item == other_item :
                    continue
                item2item_num.setdefault(item, {})
                item2item_num[item].setdefault(other_item, 0)
                item2item_num[item][other_item] += 1
    #calculate similarity
    sim = {}
    for item, related_items in item2item_num.items() :
        for other_item, num_i_j in related_items.items() :
            sim.setdefault(item, {})
            sim[item][other_item] = num_i_j / math.sqrt(item_len_dict[item] * item_len_dict[other_item])
            #print '%s\t%s\t%f' %(item, other_item, sim[item][other_item])
    #取topk，排序
    for item, related_items in sim.items() :
        sim[item] = sorted(related_items.items(), key=itemgetter(1), reverse=True)[0:k]
    return sim

def write_model2file(sim, model_file_name) :
    model_file = open(model_file_name, 'w')
    for item, related_items in sim.items() :
        line = item + '\t'
        for i, value in related_items :
            line = line + i + ':' + str(value) + ','
        line = line[0:len(line)-1]
        model_file.write(line + '\n')
    model_file.close()

def get_data_set(data_file) :
    data = {}
    for line in open(data_file) :
        arr = line.strip().split('\t')
        user = arr[0]
        item = arr[1]
        try:
            int(item)
        except:
            continue
        data.setdefault(user, set())
        data[user].add(item)
    return data

if __name__ == "__main__" :
    if len(sys.argv) < 7 :
        print 'usage: python item_commandation.py train.txt test.txt topk model_file result_file topn'
        sys.exit(-1)
    train_file = sys.argv[1]
    test_file = sys.argv[2]
    topk = int(sys.argv[3])
    model_file = sys.argv[4]
    result_file = sys.argv[5]
    topn = int(sys.argv[6])
    do_item_recom(train_file, test_file, topk, model_file, result_file, topn)

