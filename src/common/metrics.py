#!/usr/bin/env python
# encoding: utf-8
'''
*Copyright (c) 2023, Alibaba Group;
*Licensed under the Apache License, Version 2.0 (the "License");
*you may not use this file except in compliance with the License.
*You may obtain a copy of the License at

*   http://www.apache.org/licenses/LICENSE-2.0

*Unless required by applicable law or agreed to in writing, software
*distributed under the License is distributed on an "AS IS" BASIS,
*WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*See the License for the specific language governing permissions and
*limitations under the License.

@author: Hey
@email: sanyuan.**@**.com
@tel: 137****6540
@datetime: 2022/11/26 21:05
@project: DeepProtFunc
@file: metrics
@desc: metrics for binary classification or multi-class classification
'''
import csv, sys
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,  average_precision_score, confusion_matrix
sys.path.append("./")
sys.path.append("../")
sys.path.append("../src")
try:
    from utils import *
except ImportError:
    from src.utils import *


def topk_accuracy_score(targets, probs, k=3):
    '''
    topk accuracy
    :param targets:
    :param probs:
    :param k:
    :return:
    '''
    # obtain top-k label
    max_k_preds = probs.argsort(axis=1)[:, -k:][:, ::-1]
    a_real = np.resize(targets, (targets.shape[0], 1))
    # obtain the match result
    match_array = np.logical_or.reduce(max_k_preds == a_real, axis=1)
    topk_acc_score = match_array.sum() / match_array.shape[0]
    return topk_acc_score


def multi_class_acc(targets, probs, threshold=0.5):
    if targets.ndim == 2:
        targets = np.argmax(targets, axis=1)
    preds = np.argmax(probs, axis=1)
    return accuracy_score(targets, preds)


def multi_class_precision(targets, probs, average='macro'):
    if targets.ndim == 2:
        targets = np.argmax(targets, axis=1)
    preds = np.argmax(probs, axis=1)
    return precision_score(targets, preds, average=average)


def multi_class_recall(targets, probs, average='macro'):
    if targets.ndim == 2:
        targets = np.argmax(targets, axis=1)
    preds = np.argmax(probs, axis=1)
    return recall_score(targets, preds, average=average)


def multi_class_f1(targets, probs, average='macro'):
    if targets.ndim == 2:
        targets = np.argmax(targets, axis=1)
    preds = np.argmax(probs, axis=1)
    return f1_score(targets, preds, average=average)


def multi_class_roc_auc(targets, probs, average='macro'):
    if targets.ndim == 2:
        targets = np.argmax(targets, axis=1)
    return roc_auc_score(targets, probs, average=average, multi_class='ovr')


def multi_class_pr_auc(targets, probs, average='macro'):
    if targets.ndim == 2:
        targets = np.argmax(targets, axis=1)
    z = probs.shape[1]
    new_targets = np.eye(z)[targets]
    pr_auc = average_precision_score(new_targets, probs, average=average)
    return pr_auc


def metrics_multi_class(targets, probs, average="macro"):
    '''
    metrics of multi-class classification
    :param targets: 1d-array class index (n_samples, )
    :param probs:  2d-array probability (n_samples, m_classes)
    :return:
    '''
    if targets.ndim == 2 and targets.shape[1] > 1:
        targets = np.argmax(targets, axis=1)
    elif targets.ndim == 2 and targets.shape[1] == 1:
        targets = np.squeeze(targets, axis=1)

    preds = np.argmax(probs, axis=1)
    acc = accuracy_score(targets, preds)
    prec = precision_score(targets, preds, average=average)
    recall = recall_score(targets, preds, average=average)
    f1 = f1_score(targets, preds, average=average)
    result = {
        "acc": round(acc, 4),
        "prec": round(prec, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }

    try:
        roc_auc = roc_auc_score(targets, probs, average=average, multi_class='ovr')
    except Exception as e:
        roc_auc = 0
        print(e)
    z = probs.shape[1]
    new_targets = np.eye(z)[targets]
    try:
        pr_auc = average_precision_score(new_targets, probs, average=average)
    except Exception as e:
        pr_auc = 0
        print(e)

    result.update({
        "top2_acc": round(topk_accuracy_score(targets, probs, k=2), 4),
        "top3_acc": round(topk_accuracy_score(targets, probs, k=3), 4),
        "top5_acc": round(topk_accuracy_score(targets, probs, k=5), 4),
        "top10_acc": round(topk_accuracy_score(targets, probs, k=10), 4),
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4)
    })

    return result


def metrics_multi_class_for_pred(targets, preds, savepath=None):
    '''
    metrcis for multi-class classification
    :param targets: 1d-array class index (n_samples, )
    :param prebs:  1d-array class index (n_samples, )
    :return:
    '''
    if targets.ndim == 2 and targets.shape[1] > 1:
        targets = np.argmax(targets, axis=1)
    elif targets.ndim == 2 and targets.shape[1] == 1:
        targets = np.squeeze(targets, axis=1)

    acc = accuracy_score(targets, preds)
    prec = precision_score(targets, preds, average='macro')
    recall = recall_score(targets, preds, average='macro')
    f1 = f1_score(y_true=targets, y_pred=preds, average='macro')
    result = {
        "acc": round(acc, 4),
        "prec": round(prec, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }
    return result


def transform(targets, probs, threshold):
    '''
    metrics of binary classification
    :param targets: 1d-array class index (n_samples, )
    :param probs: 1d-array larger class probability (n_samples, )
    :param threshold: 0-1 prob threshokd
    :return:
    '''
    if targets.ndim == 2:
        if targets.shape[1] == 2: # [[0, 1], [1, 0]]
            targets = np.argmax(targets, axis=1)
        else: # [[1], [0]]
            targets = targets.flatten()
    if probs.ndim == 2:
        if probs.shape[1] == 2: # [[0.1, 0.9], [0.9, 0.1]]
            preds = np.argmax(probs, axis=1)
            probs = probs[:, 1].flatten()
        else: # [[0.9], [0.1]]
            preds = (probs >= threshold).astype(int).flatten()
            probs = probs.flatten()
    else:
        preds = (probs >= threshold).astype(int)
    return targets, probs, preds


def binary_acc(targets, probs, threshold=0.5):
    targets, probs, preds = transform(targets, probs, threshold)
    return accuracy_score(targets, preds)


def binary_precision(targets, probs, threshold=0.5, average='macro'):
    targets, probs, preds = transform(targets, probs, threshold)
    return precision_score(targets, preds, average=average)


def binary_recall(targets, probs, threshold=0.5, average='macro'):
    targets, probs, preds = transform(targets, probs, threshold)
    return recall_score(targets, preds, average=average)


def binary_f1(targets, probs, threshold=0.5, average='macro'):
    targets, probs, preds = transform(targets, probs, threshold)
    return f1_score(targets, preds, average=average)


def binary_roc_auc(targets, probs, threshold=0.5, average='macro'):
    targets, probs, preds = transform(targets, probs, threshold)
    return roc_auc_score(targets, probs, average=average)


def binary_pr_auc(targets, probs, threshold=0.5, average='macro'):
    targets, probs, preds = transform(targets, probs, threshold)
    return average_precision_score(targets, probs, average=average)


def binary_confusion_matrix(targets, probs, threshold=0.5, savepath=None):
    targets, probs, preds = transform(targets, probs, threshold)
    cm_obj = confusion_matrix(targets, preds, labels=[0, 1])
    plot_confusion_matrix_for_binary_class(targets, preds, cm=cm_obj, savepath=savepath)
    tn, fp, fn, tp = cm_obj.ravel()
    cm = {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
    return cm


def metrics_binary(targets, probs, threshold=0.5, average="macro", savepath=None):
    '''
    metrics for binary classification
    :param targets: 1d-array class index (n_samples, )
    :param probs: 1d-array larger class probability (n_samples, )
    :param threshold: 0-1 prob threshold
    :return:
    '''
    if targets.ndim == 2:
        if targets.shape[1] == 2: # [[0, 1], [1, 0]]
            targets = np.argmax(targets, axis=1)
        else: # [[1], [0]]
            targets = targets.flatten()
    if probs.ndim == 2:
        if probs.shape[1] == 2: # [[0.1, 0.9], [0.9, 0.1]]
            preds = np.argmax(probs, axis=1)
            probs = probs[:, 1].flatten()
        else: # [[0.9], [0.1]]
            preds = (probs >= threshold).astype(int).flatten()
            probs = probs.flatten()
    else:
        preds = (probs >= threshold).astype(int)
    acc = accuracy_score(targets, preds)
    prec = precision_score(targets, preds, average=average)
    recall = recall_score(targets, preds, average=average)
    f1 = f1_score(targets, preds, average=average)
    result = {
        "acc": round(acc, 4),
        "prec": round(prec, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }
    roc_auc = roc_auc_score(targets, probs, average=average)
    pr_auc = average_precision_score(targets, probs, average=average)
    result.update({
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4)
    })
    cm_obj = confusion_matrix(targets, preds, labels=[0, 1])
    plot_confusion_matrix_for_binary_class(targets, preds, cm=cm_obj, savepath=savepath)
    tn, fp, fn, tp = cm_obj.ravel()
    cm = {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
    result.update({
        "confusion_matrix": cm
    })
    return result


def metrics_binary_for_pred(targets, preds, savepath=None):
    '''
    metrics for binary classification
    :param targets: 1d-array class index (n_samples, )
    :param preds: 1d-array larger class index (n_samples, )
    :return:
    '''
    if targets.ndim == 2:
        if targets.shape[1] == 2: # [[1, 0], [0, 1]
            targets = np.argmax(targets, axis=1)
        else: # [[1], [0]]
            targets = targets.flatten()
    if preds.ndim == 2:
        if preds.shape[1] == 2: # [[0.9, 0.1], [0.1, 0.9]]
            preds = np.argmax(preds, axis=1)
        else: # [[0], [1]]
            preds = preds.flatten()
    cm_obj = confusion_matrix(targets, preds, labels=[0, 1])
    plot_confusion_matrix_for_binary_class(targets, preds, cm=cm_obj, savepath=savepath)
    tn, fp, fn, tp = cm_obj.ravel()
    cm = {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
    if len(np.unique(targets)) > 1:
        acc = accuracy_score(targets, preds)
        prec = precision_score(targets, preds, average='macro')
        recall = recall_score(targets, preds, average='macro')
        f1 = f1_score(y_true=targets, y_pred=preds, average='macro')
        result = {
            "acc": round(acc, 4),
            "prec": round(prec, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4)
        }
    else:

        result = {
            "acc": round((cm["tp"] + cm["tn"]) / (cm["tp"] + cm["tn"] + cm["fp"] + cm["fn"]), 4),
            "prec": round(cm["tp"]/(cm["tp"] + cm["fp"]) if cm["tp"] + cm["fp"] > 0 else 1.0, 4),
            "recall": round(cm["tp"]/(cm["tp"] + cm["fn"]) if cm["tp"] + cm["fn"] > 0 else 1.0, 4),
        }
        result["f1"] = 2 * result["prec"] * result["recall"] / (result["prec"] + result["recall"])

    result.update({
        "confusion_matrix": cm
    })
    return result


def write_error_samples_multi_class(filepath, samples, input_indexs, input_id_2_names, output_id_2_name, targets, probs,
                                    use_other_diags=False, use_other_operas=False, use_checkin_department=False):
    '''
    write the bad cases of multi-class classification
    :param filepath:
    :param samples:
    :param input_indexs:
    :param input_id_2_names:
    :param output_id_2_name:
    :param targets:
    :param probs:
    :param use_other_diags:
    :param use_other_operas:
    :param use_checkin_department:
    :return:
    '''
    targets = np.argmax(targets, axis=1)
    preds = np.argmax(probs, axis=1)
    with open(filepath, "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(["score", "y_true", "y_pred", "inputs"])
        for i in range(len(targets)):
            target = targets[i]
            pred = preds[i]
            score = 1
            if target != pred:
                score = 0
            if output_id_2_name:
                target_label = output_id_2_name[target]
                pred_label = output_id_2_name[pred]
            else:
                target_label = target
                pred_label = pred
            sample = samples[i]
            if input_id_2_names:
                new_sample = []
                for idx, input_index in enumerate(input_indexs):
                    if input_index == 3 and not use_checkin_department:
                        input_index = 12
                    new_sample.append([input_id_2_names[idx][v] for v in sample[input_index]])
                    if (input_index == 6 and use_other_diags) or (input_index == 8 and use_other_operas) or (input_index == 10 and use_other_diags):
                        new_sample.append([input_id_2_names[idx][v] for v in sample[input_index + 1]])
            else:
                new_sample = sample
            row = [score, target_label, pred_label, new_sample]
            writer.writerow(row)


def write_error_samples_binary(filepath, samples, input_indexs, input_id_2_names, targets, probs, threshold=0.5,
                               use_other_diags=False, use_other_operas=False, use_checkin_department=False):
    '''
    write bad cases of binary classification
    :param filepath:
    :param samples:
    :param input_indexs:
    :param input_id_2_names:
    :param targets:
    :param probs:
    :param threshold:
    :param use_other_diags:
    :param use_other_operas:
    :param use_checkin_department:
    :return:
    '''
    with open(filepath, "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(["score", "y_true", "y_pred", "inputs"])
        for i in range(len(targets)):
            target = targets[i][0]
            if target != 1:
                target = 1
            prob = probs[i][0]
            if prob >= threshold:
                pred = 1
            else:
                pred = 0
            score = 1
            if target != pred:
                score = 0
            target_label = "True" if target == 1 else "False"
            pred_label = "True" if target == 1 else "False"
            sample = samples[i]
            if input_id_2_names:
                new_sample = []
                for idx, input_index in enumerate(input_indexs):
                    if input_index == 3 and not use_checkin_department:
                        input_index = 12
                    new_sample.append([input_id_2_names[idx][v] for v in sample[input_index]])
                    if (input_index == 6 and use_other_diags) or (input_index == 8 and use_other_operas) or (input_index == 10 and use_other_diags):
                        new_sample.append([input_id_2_names[idx][v] for v in sample[input_index + 1]])
            else:
                new_sample = sample
            row = [score, target_label, pred_label, new_sample]
            writer.writerow(row)


if __name__ == "__main__":
    '''multi_class'''
    targets = np.array([0, 1, 2, 1, 3])
    probs = np.array([[0.9, 0.05, 0.05, 0], [0.5, 0.45, 0.05, 0], [0.4, 0.05, 0.55, 0], [0.1, 0.55, 0.25, 0.1], [0.4, 0.25, 0.35, 0]])
    print(metrics_multi_class(targets, probs))

    targets = np.array([0, 1, 2, 3, 3])
    probs = np.array([[0.9, 0.05, 0.05, 0], [0.5, 0.45, 0.05, 0], [0.4, 0.05, 0.55, 0], [0.1, 0.25, 0.25, 0.4], [0.1, 0.25, 0.25, 0.4]])
    print(metrics_multi_class(targets, probs))
    targets = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 1]])
    probs = np.array([[0.9, 0.05, 0.05, 0], [0.5, 0.45, 0.05, 0], [0.4, 0.05, 0.55, 0], [0.1, 0.25, 0.25, 0.4], [0.1, 0.25, 0.25, 0.4]])
    print(metrics_multi_class(targets, probs))

    '''binary'''
    targets = np.array([0, 0, 1, 1])
    probs = np.array([[0.1], [0.1], [0.1], [0.9]])
    print(metrics_binary(targets, probs))

    targets = np.array([[0], [0], [1], [1]])
    probs = np.array([[0.1], [0.1], [0.1], [0.9]])
    print(metrics_binary(targets, probs))

    targets = np.array([0, 0, 1, 1])
    probs = np.array([[0.1, 0.1, 0.1, 0.9]])
    print(metrics_binary(targets, probs))

    targets = np.array([0, 0, 1, 1])
    probs = np.array([0.1, 0.1, 0.1, 0.9])
    print(metrics_binary(targets, probs))

    targets = np.array([0, 1, 2, 1, 3])
    probs = np.array([[0.9, 0.05, 0.05, 0], [0.5, 0.45, 0.05, 0], [0.4, 0.05, 0.55, 0], [0.1, 0.55, 0.25, 0.1], [0.4, 0.25, 0.25, 0.1]])
    z = probs.shape[1]
    # print(z)
    print(np.eye(z))
    new_targets = np.eye(z)[targets]
    print(new_targets)

