python3 main.py -g 0 -m BundleGT -d imdb --info="" \
  --batch_size_test=4096 --batch_size_train=4096 --early_stopping 0 \
  --lr=1e-3 --l2_reg=1e-5 --num_ui_layer=4 --gcn_norm=0 --num_trans_layer=3 \
  --num_token=70 --folder="train" --ub_alpha=0.5 --bi_alpha=0.5
