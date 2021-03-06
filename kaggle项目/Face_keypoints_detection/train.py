import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
from FaceCNN import FaceCNN
from FaceDataset import FaceDataset

def val(model, dataset, batch_size):
    dataload = data.DataLoader(dataset, batch_size)
    result, num = 0, 0
    for imgs, labels in dataload:
        imgs = imgs.cuda()
        preds = model.forward(imgs)
        preds = preds.cpu()
        mse = np.sum((preds.data.numpy()-labels.data.numpy())**2, axis=1)
        result += np.sum(mse, axis=0)
        num += len(labels)
    return result / num


def train(train_dataset, val_dataset, epoches, batch_size, learning_rate, wt_decay):
    gpus = [0]
    train_dataload = data.DataLoader(train_dataset, batch_size)
    net = FaceCNN()
    net = torch.nn.DataParallel(net, device_ids=gpus).cuda()
    optimize = optim.Adam(net.parameters(), lr=learning_rate, weight_decay=wt_decay)
    loss_fuc = nn.MSELoss()
    for epoch in range(epoches):
        net.train()
        loss = 0
        for imgs, labels in train_dataload:
            imgs = imgs.cuda()
            labels = labels.cuda()
            preds = net.forward(imgs)
            labels = labels.type('torch.FloatTensor').cuda()
            loss = loss_fuc(preds, labels)
            optimize.zero_grad()
            loss.backward()
            optimize.step()
        if epoch % 10 == 0:
            net.eval()
            #train_acc = val(net, train_dataset, batch_size)
            #val_acc = val(net, val_dataset, batch_size)
            print ("train loss is: {}".format(loss))
            #print ("train acc. is: {}".format(train_acc))
            #print ("val acc. is: {}".format(val_acc))
    return net

def main():
    train_path = r"data"
    #val_path = r"/media/root/515e7d3a-49ac-40be-ba58-fef9702d123c/work_record/digit_recognizer/digit-recognizer/digit-recognizer/1216/digit/val"
    train_dataset = FaceDataset(train_path, 'train')
    val_dataset = FaceDataset(train_path, 'val')
    model = train(train_dataset, val_dataset, 100, 256, 0.001, 0.0001)
    torch.save(model, 'face_final_400.pkl')

if __name__ == "__main__":
    main()
