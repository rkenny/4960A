#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from torch.utils.data import DataLoader
import setproctitle
import dataset
from model import BGCN, BGCN_Info
from utils import check_overfitting, early_stop, logger
from train import train
from metric import Recall, NDCG, MRR
from config import CONFIG
from test import test
import loss
from itertools import product
import time
from tensorboardX import SummaryWriter


def main():
    #  set env
    setproctitle.setproctitle(f"train{CONFIG['name']}")
    os.environ["CUDA_VISIBLE_DEVICES"] = CONFIG['gpu_id']
    device = torch.device('cuda')

    #  fix seed
    seed = 123
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True

    #  load data
    bundle_train_data, bundle_test_data, item_data, assist_data = \
            dataset.get_dataset(CONFIG['path'], CONFIG['dataset_name'], task=CONFIG['task'])
    # Batch was 2048
    train_loader = DataLoader(bundle_train_data, 8096, True,
                              num_workers=16, pin_memory=True)
    # Batch was 4096
    test_loader = DataLoader(bundle_test_data, 8096, False,
                             num_workers=16, pin_memory=True)

    #  pretrain
    if 'pretrain' in CONFIG:
        pretrain = torch.load(CONFIG['pretrain'], map_location='cpu')
        print('load pretrain')

    #  graph
    ub_graph = bundle_train_data.ground_truth_u_b
    ui_graph = item_data.ground_truth_u_i
    bi_graph = assist_data.ground_truth_b_i

    #  metric
    # metrics = [Recall(1), NDCG(1), Recall(10), NDCG(10), Recall(20), NDCG(20)]
    metrics = [Recall(20)]
    TARGET = 'Recall@20'

    #  loss
    loss_func = loss.BPRLoss('mean')

    #  log
    log = logger.Logger(os.path.join(
        CONFIG['log'], CONFIG['dataset_name'], 
        f"{CONFIG['model']}_{CONFIG['task']}", ''), 'best', checkpoint_target=TARGET)

    theta = 0.6

    time_path = time.strftime("%y%m%d-%H%M%S", time.localtime(time.time()))

    for lr, decay, message_dropout, node_dropout \
            in product(CONFIG['lrs'], CONFIG['decays'], CONFIG['message_dropouts'], CONFIG['node_dropouts']):

        visual_path =  os.path.join(CONFIG['visual'], 
                                    CONFIG['dataset_name'],  
                                    f"{CONFIG['model']}_{CONFIG['task']}", 
                                    f"{time_path}@{CONFIG['note']}", 
                                    f"lr{lr}_decay{decay}_medr{message_dropout}_nodr{node_dropout}")

        # model
        if CONFIG['model'] == 'BGCN':
            graph = [ub_graph, ui_graph, bi_graph]
            info = BGCN_Info(64, decay, message_dropout, node_dropout, 2)
            model = BGCN(info, assist_data, graph, device, pretrain=None).to(device)

        assert model.__class__.__name__ == CONFIG['model']

        # op
        op = optim.Adam(model.parameters(), lr=lr)
        # env
        env = {'lr': lr,
               'op': str(op).split(' ')[0],   # Adam
               'dataset': CONFIG['dataset_name'],
               'model': CONFIG['model'], 
               'sample': CONFIG['sample'],
               }

        #  continue training
        if CONFIG['sample'] == 'hard' and 'conti_train' in CONFIG:
            model.load_state_dict(torch.load(CONFIG['conti_train']))
            print('load model and continue training')

        retry = CONFIG['retry']  # =1
        
        while retry >= 0:
            # log
            log.update_modelinfo(info, env, metrics)
            try:
                # train & test
                early = CONFIG['early']  
                train_writer = SummaryWriter(log_dir=visual_path, comment='train')
                test_writer = SummaryWriter(log_dir=visual_path, comment='test')
                for epoch in range(CONFIG['epochs']):
                    # train
                    trainloss = train(model, epoch+1, train_loader, op, device, CONFIG, loss_func)
                    print("I got past train")
                    train_writer.add_scalars('loss/single', {"loss": trainloss}, epoch)
                    print("i got past train_writer")
                    # test
                    print("Epoch is " + str(epoch))
                    print("Test interval is " + str (CONFIG['test_interval']))
                    print(epoch % CONFIG['test_interval'])
                    if epoch % CONFIG['test_interval'] == 0: 
                        output_metrics = test(model, test_loader, device, CONFIG, metrics)
                        print("argh")
                        for metric in output_metrics:
                            test_writer.add_scalars('metric/all', {metric.get_title(): metric.metric}, epoch)
                            # print(test_writer)
                            if metric==output_metrics[0]:
                                test_writer.add_scalars('metric/single', {metric.get_title(): metric.metric}, epoch)

                        # log
                        log.update_log(metrics, model)

                        # check overfitting
                        if epoch > 10:
                            if check_overfitting(log.metrics_log, TARGET, 1, show=False):
                                print("the model was overfitting")
                                break
                        # early stop
                        early = early_stop(
                            log.metrics_log[TARGET], early, threshold=0)
                        if early <= 0:
                            print("this was an early stop")
                            break
                train_writer.close()
                test_writer.close()

                log.close_log(TARGET)
                retry = -1
            except RuntimeError as e:
                print(e)
                retry -= 1
    log.close()
    
    for (metric, i) in zip(output_metrics, range(0, len(output_metrics))):
      with open('/home/kennyr/projects/def-hfani/kennyr/Outputs/BGCN/'+CONFIG['dataset_name']+metric.get_title()+'.pred.pickle', 'wb') as outputFile:
        pickle.dump(metric.scores, outputFile, protocol=pickle.HIGHEST_PROTOCOL)
      with open('/home/kennyr/projects/def-hfani/kennyr/Outputs/BGCN/'+CONFIG['dataset_name']+metric.get_title()+'.ground_truth.pickle', 'wb') as outputFile:
        pickle.dump(metric.ground_truth, outputFile, protocol=pickle.HIGHEST_PROTOCOL)

    #with open('/mnt/4960/4960_git/Outputs/BGCN/'+CONFIG['dataset_name']+'.pred.pickle', 'wb') as outputFile:
    #  pickle.dump(metric.scores, outputFile, protocol=pickle.HIGHEST_PROTOCOL)
    #with open('/mnt/4960/4960_git/Outputs/BGCN/'+CONFIG['dataset_name']+'.ground_truth.pickle', 'wb') as outputFile:
    #  pickle.dump(metric.ground_truth, outputFile, protocol=pickle.HIGHEST_PROTOCOL)
    # input("press enter to continue")


if __name__ == "__main__":
    main()
