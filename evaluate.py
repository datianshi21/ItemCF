#!/usr/bin/env python
# coding=utf-8
#########################################################################
# File Name:    evaluate.py
# Author:       hongchunxiao
# mail:         hongchunxiao@gmail.com
# Created  Time: 2013/12/29 12:33:21 (Sunday December)
# Modified Time: 2013/12/29 12:33:21 (Sunday December)
#
# Description:
#########################################################################
import sys
from operator import *

"""
result_file_name input format:
---user1 recom1:s1,recom2:s2,.. click1,click2...
---user2 recom1:s1,recom2:s2,.. click1,click2...

obj_file input format:
---user1 item1
---user1 item2
---user2 item1

candicate_item_file input format:
---item1
---item2
"""

def evaluate(result_file_name, N, probility, obj_file, candicate_item_file) :
    recom_dict, obj_dict = read_result(result_file_name, N, probility)
    if obj_file != '' :
        obj_dict = read_obj(obj_file)

    hit, all, prec = precision(obj_dict, recom_dict)
    print 'precision@%d = %d/%d = %f' %(N, hit, all, prec)
    hit, all, rec = recall(obj_dict, recom_dict)
    print 'recall@%d = %d/%d = %f' %(N, hit, all, rec)
    print 'F = %f' %(2 * prec * rec / (prec + rec))
    map_value = map(result_file_name, obj_dict)
    print 'map(Mean Average Precision) = %f' %(map_value)
    rec_item_num, obj_item_num, coverage_rate = coverage(recom_dict, candicate_item_file)
    print 'coverage = %d/%d = %f' %(rec_item_num, obj_item_num, coverage_rate)

def read_result(result_file_name, N, probility) :
    recom_dict = {}
    obj_dict = {}
    recom_items = ''
    click_items = ''
    for line in open(result_file_name) :
        arr = line.strip().split('\t')
        user = arr[0]
        if len(arr) >= 2 :
            recom_items = arr[1]
        if len(arr) >= 3 :
            click_items = arr[2]
        #初始化
        recom_dict.setdefault(user, set())
        obj_dict.setdefault(user, set())
        
        rec_num = 0
        for recom_score in recom_items.split(',') :
            r_s = recom_score.split(':')
            if len(r_s) != 2:
                continue
            if rec_num >= N or float(r_s[1]) < probility :
                break
            if len(r_s[0].strip()) > 0 :
                recom_dict[user].add(r_s[0])
                rec_num += 1
        for click_item in click_items.split(',') :
            if len(click_item.strip()) > 0 :
                obj_dict[user].add(click_item)
    return recom_dict, obj_dict

def read_obj(obj_file) :
    obj_dict = dict()
    for line in open(obj_file) :
        arr = line.strip().split('\t')
        user = arr[0]
        item = arr[1]
        obj_dict.setdefault(user, set())
        obj_dict[user].add(item)
    #print 'read obj at: ' + obj_file
    return obj_dict

#Mean Average Precision
def map(result_file_name, obj_dict) :
    total_user = 0
    map = 0
    recom_items = ''
    click_items = ''
    for line in open(result_file_name) :
        arr = line.split('\t')
        user = arr[0]
        total_user += 1
        if len(arr) >= 2 :
            recom_items = arr[1]
        if len(arr) >= 3 :
            click_items = arr[2]

        rec_num = 0
        cur_right = 0
        ap = 0
        for recom_score in recom_items.split(',') :
            r_s = recom_score.split(':')
            if len(r_s) != 2:
                continue
            if len(r_s[0].strip()) > 0 :
                item = r_s[0]
                rec_num += 1
                if item in obj_dict[user] :
                    cur_right += 1
                    ap += cur_right / (1.0 * rec_num)
        ap /= len(obj_dict[user]) 
        map += ap
    map /= total_user
    return map 

def coverage(recom_dict, candicate_item_file) :
    obj_item_set = set()
    rec_item_set = set()
    for line in open(candicate_item_file) :
        obj_item_set.add(line.strip())

    for user, items in recom_dict.items() :
        rec_item_set = rec_item_set.union(items)

    coverage_rate = float(len(rec_item_set)) / len(obj_item_set)
    return len(rec_item_set), len(obj_item_set), coverage_rate

def recall(obj_dict, recom_dict) :
    hit = 0
    all = 0
    for user in obj_dict.keys() :
        recom_items = recom_dict[user]
        obj_items = obj_dict[user]
        for item in obj_items :
            if item in recom_items :
                hit += 1
        all += len(obj_items)
    if all > 0 :
        value = hit / (all * 1.0)
    elif hit == all :
        value = 1
    else :
        value = 0
    #return hit, all , hit / (all * 1.0)
    return hit, all , value

def precision(obj_dict, recom_dict) :
    hit = 0
    all = 0
    #for user in obj_dict.keys() :
    for user in recom_dict.keys() :
        recom_items = recom_dict[user]
        obj_items = obj_dict[user]
        for item in obj_items :
            if item in recom_items :
                hit += 1
        all += len(recom_items)

    if all > 0 :
        value = hit / (all * 1.0)
    elif hit == all :
        value = 1
    else :
        value = 0
    return hit, all , value

if __name__ == '__main__' :
    if len(sys.argv) < 4 :
        print 'usage: python evaluate.py result_file.txt topn probility candicate_item_file [obj_file]'
        sys.exit(-1)
    result_file = sys.argv[1]
    topn = int(sys.argv[2]) #recommend only topn item for per-user
    probility = float(sys.argv[3]) #recommend only when the probility is big than it
    candicate_item_file = sys.argv[4] #the candicate item set for recommended
    if len(sys.argv) == 6:
        obj_file = sys.argv[5] #the item that user visits at object date
    else :
        obj_file = ''

    evaluate(result_file, topn, probility, obj_file, candicate_item_file)
