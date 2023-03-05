# -*- ecoding: utf-8 -*-
# @ModuleName: comirec
# @Author: wk
# @Email: 306178200@qq.com
# @Time: 2023/3/5 15:08
import torch
from torch import nn
from ..layers import MultiInterest_SA,CapsuleNetwork
from ..base_model import SequenceBaseModel

class ComirecSA(SequenceBaseModel):

    def __init__(self, enc_dict,config):
        super(ComirecSA, self).__init__(enc_dict, config)

        self.multi_interest_sa = MultiInterest_SA(embedding_dim=self.embedding_dim, K=self.config['K'])
        self.apply(self._init_weights)

    def forward(self, data, is_training=True):

        item_seq = data['hist_item_list']
        mask = data['hist_mask_list']
        item = data['target_item']
        if is_training:
            item = data['target_item'].squeeze()
            seq_emb = self.item_emb(item_seq)  # Batch,Seq,Emb
            item_e = self.item_emb(item).squeeze(1)

            mask = mask.unsqueeze(-1).float()
            multi_interest_emb = self.multi_interest_sa(seq_emb, mask)  # Batch,K,Emb

            cos_res = torch.bmm(multi_interest_emb, item_e.squeeze(1).unsqueeze(-1))
            k_index = torch.argmax(cos_res, dim=1)

            best_interest_emb = torch.rand(multi_interest_emb.shape[0], multi_interest_emb.shape[2]).to(self.device)
            for k in range(multi_interest_emb.shape[0]):
                best_interest_emb[k, :] = multi_interest_emb[k, k_index[k], :]

            loss = self.calculate_loss(best_interest_emb,item)
            output_dict = {
                'user_emb':multi_interest_emb,
                'loss':loss,
            }
        else:
            seq_emb = self.item_emb(item_seq)  # Batch,Seq,Emb
            mask = mask.unsqueeze(-1).float()
            multi_interest_emb = self.multi_interest_sa(seq_emb, mask)  # Batch,K,Emb
            output_dict = {
                'user_emb': multi_interest_emb,
            }
        return output_dict

class ComirecDR(SequenceBaseModel):

    def __init__(self, enc_dict,config):
        super(ComirecDR, self).__init__(enc_dict, config)

        self.capsule = CapsuleNetwork(self.embedding_dim,self.max_length,bilinear_type=2,interest_num=self.config['K'])
        self.apply(self._init_weights)

    def forward(self, data, is_training=True):
        item_seq = data['hist_item_list']
        mask = data['hist_mask_list']

        if is_training:
            item = data['target_item'].squeeze()
            seq_emb = self.item_emb(item_seq)  # Batch,Seq,Emb
            item_e = self.item_emb(item).squeeze(1)

            multi_interest_emb = self.capsule(seq_emb, mask,self.device)  # Batch,K,Emb

            cos_res = torch.bmm(multi_interest_emb, item_e.squeeze(1).unsqueeze(-1))
            k_index = torch.argmax(cos_res, dim=1)

            best_interest_emb = torch.rand(multi_interest_emb.shape[0], multi_interest_emb.shape[2]).to(self.device)
            for k in range(multi_interest_emb.shape[0]):
                best_interest_emb[k, :] = multi_interest_emb[k, k_index[k], :]

            loss = self.calculate_loss(best_interest_emb,item)
            output_dict = {
                'user_emb':multi_interest_emb,
                'loss':loss,
            }
        else:
            seq_emb = self.item_emb(item_seq)  # Batch,Seq,Emb
            multi_interest_emb = self.capsule(seq_emb, mask,self.device)  # Batch,K,Emb
            output_dict = {
                'user_emb': multi_interest_emb,
            }
        return output_dict


