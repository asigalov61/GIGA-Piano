# GIGA Piano Original Training Data

***

## [NEW] GIGA-Piano Perceiver Training Data Pack

### 1) Contains ~420k Solo Piano MIDI compositions
### 1) Based on original GIGA-Piano training data
### 2) Uses modified GIGA-Piano encoding
### 3) Works with any type of data sampling and any model sequence length

```
!wget --no-check-certificate -O 'GIGA-Piano-Perceiver-Training-Data.zip' "https://onedrive.live.com/download?cid=8A0D502FC99C608F&resid=8A0D502FC99C608F%2118740&authkey=ANEK-9WanNFyalw"
```

### Encoding info:
### [dTime(0-126), Duration(1-126)+128, MIDI Pitch(1-126)+256, MIDI Velocity(1-126)+384]
### Compositions separator/Intro/Zero sequence: [126, 126+128, 0+256, 0+384]

***

## If you want to reproduce the results presented in this repo, here is the original training data file:

### Please note that this is training data for the original training code and original sequence length (1024)
### If you want to increase the sequence length of the resulting model, you will have to process MIDIs from scratch

```
!wget --no-check-certificate -O 'GIGA-Piano-INTs.zip' "https://onedrive.live.com/download?cid=8A0D502FC99C608F&resid=8A0D502FC99C608F%2118651&authkey=ABGFgaUwv_HgypY"
```

```
https://1drv.ms/u/s!Ao9gnMkvUA2KgZFb_PsSwy4MutfVKg?e=cJdMuc
```

***

## [NEW] 2.7 GB Training Data Pack (if you want to train a more capable model)
### This will work with exsiting training code and 1024 seq_len

```
!wget --no-check-certificate -O 'GIGA-Piano-INTs.zip' "https://onedrive.live.com/download?cid=8A0D502FC99C608F&resid=8A0D502FC99C608F%2118656&authkey=AKeSKT-LYg8QkPs"
```

***

## How to use:

### Use the original training code/colab from the repo
### Load training data like so:
```
train_data1 = TMIDIX.Tegridy_Any_Pickle_File_Reader('./GIGA_Piano_INTs')
```
### Then you can jump straight to TRAIN section of the colab. It should work fine and load the original training data

***

### Project Los Angeles
### Tegridy Code 2022
