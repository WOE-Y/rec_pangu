# -*- ecoding: utf-8 -*-
# @ModuleName: run_ranking_example
# @Author: wk
# @Email: 306178200@qq.com
# @Time: 2022/6/10 7:40 PM
import sys
sys.path.append('../../')
import torch
from rec_pangu.dataset import get_dataloader
from rec_pangu.models.ranking import WDL, DeepFM, NFM, FiBiNet, AFM, AFN, AOANet, AutoInt, CCPM, LR, FM, xDeepFM, DCN
from rec_pangu.trainer import RankTraniner
import pandas as pd

if __name__=='__main__':
    df = pd.read_csv('sample_data/ranking_sample_data.csv')
    #声明数据schema
    schema={
        "sparse_cols":['user_id','item_id','item_type','dayofweek','is_workday','city','county',
                      'town','village','lbs_city','lbs_district','hardware_platform','hardware_ischarging',
                      'os_type','network_type','position'],
        "dense_cols" : ['item_expo_1d','item_expo_7d','item_expo_14d','item_expo_30d','item_clk_1d',
                       'item_clk_7d','item_clk_14d','item_clk_30d','use_duration'],
        "label_col":'click',
    }
    #准备数据,这里只选择了100条数据,所以没有切分数据集
    train_df = df
    valid_df = df
    test_df = df

    #声明使用的device
    device = torch.device('cpu')
    #获取dataloader
    train_loader, valid_loader, test_loader, enc_dict = get_dataloader(train_df, valid_df, test_df, schema, batch_size=512)
    #声明模型,排序模型目前支持：WDL, DeepFM, NFM, FiBiNet, AFM, AFN, AOANet, AutoInt, CCPM, LR, FM, xDeepFM
    model = xDeepFM(enc_dict=enc_dict)
    #声明Trainer
    trainer = RankTraniner(num_task=1)
    #训练模型
    trainer.fit(model, train_loader, valid_loader, epoch=5, lr=1e-3, device=device)
    #保存模型权重
    trainer.save_model(model, './model_ckpt')
    #保存模型权重和enc_dict
    trainer.save_all(model, enc_dict, './model_ckpt')
    #模型验证
    test_metric = trainer.evaluate_model(model, test_loader, device=device)

    #测试 predict_dataframe
    y_pre_dataftame = trainer.predict_dataframe(model, test_df, enc_dict, schema)
    #测试 predict_dataloader
    y_pre_dataloader = trainer.predict_dataloader(model, test_loader)
    assert y_pre_dataftame == y_pre_dataloader,"预测结果不一致"

