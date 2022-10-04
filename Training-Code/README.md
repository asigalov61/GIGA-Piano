# GIGA Piano Training Code

***

[![Open In Colab][colab-badge]][colab-notebook1]

[colab-notebook1]: <https://colab.research.google.com/github/asigalov61/GIGA-Piano/blob/main/Training-Code/GIGA_Piano_Maker.ipynb>
[colab-badge]: <https://colab.research.google.com/assets/colab-badge.svg>

***

## Please also check out SOTA Perceiver-AR Transformer Implementation for GIGA-Piano in the folder above

***

## NOTE ON THE DISPLAYED TRAINING TIME

### If you want the dataloader to display accurate steps-per-epoch/training time do the following:

### Replace this:

```
def __len__(self):
        return self.data.size(0)
```

### To this:

```
def __len__(self):
        return self.data.size(0) // self.seq_len
```

***

## ALTERNATIVE/MORE EFFICIENT/CONSECUTIVE DATALOADER CODE
### It seems that random sampling is redundant and does not do much.
### Also, it seems that training for more than one epoch is redundant as well and does not really improve results.
### So here is the alternative/consecutive sampling dataloader that would allow efficient training in just 1 epoch

```
data_train, data_val = torch.Tensor(train_data1), torch.Tensor(train_data1[:(1024 * 128)+1])

class MusicSamplerDataset(Dataset):
    def __init__(self, data, seq_len):
        super().__init__()
        self.data = data
        self.seq_len = seq_len

    def __getitem__(self, index):

        idx = index * self.seq_len

        x = self.data[idx: idx + self.seq_len].long()
        trg = self.data[(idx+1): (idx+1) + self.seq_len].long()
        
        return x, trg

    def __len__(self):
        return (self.data.size(0) // self.seq_len) - 1

train_dataset = MusicSamplerDataset(data_train, SEQ_LEN)
val_dataset   = MusicSamplerDataset(data_val, SEQ_LEN)
train_loader  = DataLoader(train_dataset, batch_size = BATCH_SIZE)
val_loader    = DataLoader(val_dataset, batch_size = BATCH_SIZE)
```

***

### Project Los Angeles
### Tegridy Code 2022
