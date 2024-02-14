import math

import torch_geometric.data

import params
import src.mdl.gnn.graph
from src.mdl.team2vec import data_handler

import os
import torch
from torch_geometric.nn import MetaPath2Vec
import numpy as np

class M2V(src.mdl.gnn.graph.Graph):

    # setup the entire model before running
    def __init__(self):
        # it will already inherit all the variables in the super class
        super().__init__()
        self.init_child_variables()

    # this method will already have all the variables contained in the super class
    # so the additional ones will be initialized here
    def init_child_variables(self):
        # the variables only specific to the model will be under the hierarchy of model_params section
        # in the params.py file
        # model_params is a local file for convenient access
        model_params = self.params['model'][self.model_name]['model_params']
        self.shuffle = model_params['shuffle']
        self.metapath = model_params['metapath']
        self.lr = model_params['lr']

    # this will load the desired graph data for running with the model
    def load(self, graph_datapath):
        print(f'graph data to load from : {graph_datapath}')
        self.data = self.dh.load_graph(graph_datapath)

        print(f'loaded graph data : {self.data}')

    # initialize the model
    def init_model(self):
        assert type(self.data) == torch_geometric.data.hetero_data.HeteroData

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = MetaPath2Vec(self.data.edge_index_dict, embedding_dim=self.embedding_dim,
                             metapath=self.metapath, walk_length=self.walk_length, context_size=self.context_size,
                             walks_per_node=self.walks_per_node, num_negative_samples=self.num_negative_samples,
                             sparse=True).to(self.device)

        self.loader = self.model.loader(batch_size = self.batch_size, shuffle = self.loader_shuffle, num_workers = self.num_workers)
        self.optimizer = torch.optim.SparseAdam(list(self.model.parameters()), lr = self.lr)

    # train the model to generate embeddings
    def learn(self, model, optimizer, loader, device, epoch, log_steps = 50, eval_steps = 2000):
        model.train()

        total_loss = 0
        print(f'learn(epoch({epoch})')
        print(f'######################################')
        for i, (pos_rw, neg_rw) in enumerate(loader):
            optimizer.zero_grad()
            loss = model.loss(pos_rw.to(device), neg_rw.to(device))
            loss.backward()
            optimizer.step()

            print(f'\ti : {i}, loss : {loss}')
            total_loss += loss.item()
            # if (i + 1) % log_steps == 0:
            #     print((f'Epoch: {epoch}, Step: {i + 1:05d}/{len(loader)}, '
            #            f'Loss: {total_loss / log_steps:.4f}'))
            #     total_loss = 0
        print(f'######################################')
        return total_loss / len(loader)

    def run(self):
        self.load(self.teams_graph_input_filepath)
        for num_epochs in self.max_epochs:
            self.init_model()

            losses = []
            list_epochs = []
            min_loss = math.inf

            # this file logs every 10 / 20 epochs
            # it is NOT the final pickle file for embeddings
            with open(f'{self.graph_preprocessed_output_filename}.e{num_epochs}.txt', 'w') as outfile:
                line = f'Graph : \n\n' \
                       f'data = {self.data.__dict__}\n' \
                       f'\nNumber of Epochs : {num_epochs}\n' \
                       f'---------------------------------\n'
                for epoch in range(num_epochs):
                    loss = self.learn(self.model, self.optimizer, self.loader, self.device, epoch)
                    if(loss < min_loss):
                        min_loss = loss
                        print('.')
                    if (epoch % 20 == 0):
                        print(f'Epoch = {epoch : 02d}, loss = {loss : .4f}')

                        # the model() gives all the weights and biases of the model currently
                        # the detach() enables this result to require no gradient
                        # and then we convert the tensor to numpy array
                        weights = self.model.embedding.weight.detach().numpy()
                        # weights = self.normalize(weights)
                        # weights = np.around(weights, 2)

                        print(f'\nepoch : {epoch}\n')
                        print(weights)

                        # lines to write to file
                        line += f'Epoch : {epoch}\n'
                        line += f'--------------------------\n'
                        line += f'Node ----- Embedding -----\n\n'
                        for i, weights_per_node in enumerate(weights):
                            print(weights_per_node)
                            line += f'{i:2} : {weights_per_node}\n'
                        line += f'--------------------------\n\n'
                    losses.append(loss)
                    list_epochs.append(epoch)
                # write to file
                outfile.write(line)

            # store the final embeddings to a pickle file
            self.dh.write_graph(weights, f'{self.graph_preprocessed_output_filename}.e{num_epochs}.pkl')

            # draw and save the loss vs epoch plot
            self.plot(list_epochs, losses, f'{self.graph_plot_filename}.e{num_epochs}.png')


def main():
    m2v = M2V()
    m2v.run()

if __name__ == '__main__':
    main()