# GIGA Piano Training Code

***

[![Open In Colab][colab-badge]][colab-notebook1]

[colab-notebook1]: <https://colab.research.google.com/github/asigalov61/GIGA-Piano/blob/main/Training-Code/GIGA_Piano_Maker.ipynb>
[colab-badge]: <https://colab.research.google.com/assets/colab-badge.svg>

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
        return self.data.size(0) // self.seq_len // BATCH_SIZE
```

***

### Project Los Angeles
### Tegridy Code 2022
