# Large GIGA Piano Pre-Trained Model

***

## Here is a large GIGA-Piano pretrained model (24 layers) trained on the large training data pack (2.6GB)
## All other specs are the same (1024 all around with 16 heads)

***

## Some Model Stats:

### Trained upon partial provided 2.6GB training data pack for 1 epochs (60k steps/~30 hours) @ 16 batches on dual A6000 GPUs
### FLoss 0.9514 CE
### VFloss 0.9514 CE
### Acc 0.80 CE (5% improvement!!!)

***

## Model Sequence Info:

### [SOS/EOS(127), dTime(0-126), Duration(1-126), MIDI Pitch(1-126)]

***

## IMPORTANT NOTE ON LOADING
### To load the model with the original provided code/coalb, do not forget to change the number of layers from 16 to 24
### That is all that is needed to use the model! :)

```
config = GPTConfig(128, 
                   1024,
                   dim_feedforward=1024,
                   n_layer=24, # <--- CHANGE THIS FROM 16 TO 24 !!!
                   n_head=16, 
                   n_embd=1024,
                   enable_rpr=True,
                   er_len=1024)
```

***

### Project Los Angeles
### Tegridy Code 2022
