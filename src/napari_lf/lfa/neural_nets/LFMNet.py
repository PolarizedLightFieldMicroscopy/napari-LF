import pytorch_lightning as pl
import torch
from torch.utils import data
import torch.nn as nn
import torchvision as tv
from neural_nets.util.LFUtil import *
from neural_nets.util.convNd import convNd
from neural_nets.LFNeuralNetworkProto import LFNeuralNetworkProto

# LFMNet definition
class LFMNet(LFNeuralNetworkProto):
    def init_network_instance(self):
        # Required: default network settings
        self.default_net_settings = {
            'n_Depths' : 64, 
            'LF_in_shape' : [33,33,39,39], 
            'LF_in_fov' : 9, 
            'use_bias' : True, 
            'use_skip_conn' : False, 
            'use_small_unet' : True}
        
        # Populate members, based on user provided or default settings
        self.n_Depths = self.get_setting('n_Depths')
        self.LF_in_shape = self.get_setting('LF_in_shape')
        self.LF_in_fov = self.get_setting('LF_in_fov') 
        use_bias = self.get_setting('use_bias')
        use_skip_conn = self.get_setting('use_skip_conn')
        use_small_unet = self.get_setting('use_small_unet')
        
        # Create networks and layers
        if use_small_unet:
            from neural_nets.util.UnetShallow import UNetLF
        else:
            from neural_nets.util.UnetFull import UNetLF

        self.lensletConvolution = nn.Sequential(
            convNd(1,2, num_dims=4, kernel_size=(3,3, self.LF_in_fov, self.LF_in_fov), stride=1, padding=(1,1,0,0), use_bias=use_bias),
            nn.LeakyReLU())
        
        self.Unet = UNetLF(2, self.n_Depths, use_skip=use_skip_conn)
        
    
    # Configure dataloader
    def configure_dataloader(self):
        self.default_training_settings = {'epochs'              : 3, 
                                          'images_ids'          : list(range(10,15)), 
                                          'batch_size'          : 1,
                                          'validation_split'    : 0.1,
                                          'learning_rate'       : 1e-3,
                                          'LF_ROI_size'         : 3, # Volume behind how many micro-lenses to reconstruct? # 39 means full image
                                          'use_patches'         : False, 
                                          'volume_threshold'    : 0.03,
                                          'dataset_path'        : 'D:\\BrainImagesJosuePage\\Brain_40x_64Depths_362imgs.h5',
                                          'output_dir'       : ''}
        
        # Load data
        all_data = Dataset(self.get_train_setting('dataset_path'), 261290, \
                        fov=self.LF_in_fov, 
                        neighShape=self.get_train_setting('LF_ROI_size'), 
                        img_indices=self.get_train_setting('images_ids'), 
                        get_full_imgs=not self.get_train_setting('use_patches'), center_region=None)
        
        # Create train and test loaders
        train_size = int((1 - self.get_train_setting('validation_split')) * len(all_data))
        test_size = len(all_data) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(all_data, [train_size, test_size])
        # Create data loaders
        self.train_loader = data.DataLoader(train_dataset, batch_size=self.get_train_setting('batch_size'),
                                        shuffle=True, num_workers=0, pin_memory=True)
        self.val_loader = data.DataLoader(val_dataset, batch_size=self.get_train_setting('batch_size'),
                                    shuffle=False, num_workers=0, pin_memory=True)
        
        # Find normalization values
        temp_max_LF_train, temp_max_vol_train = all_data.get_max()
        # store these as nn.Parameter so the network storesthem in a checkpoint
        self.max_LF_train = nn.Parameter(torch.tensor(float(temp_max_LF_train)))
        self.max_vol_train = nn.Parameter(torch.tensor(float(temp_max_vol_train)))
        
        self.save_hyperparameters()
        
    def prepare_input(self, input):
        # todo: maybe assert shape
        if torch.is_tensor(input):
            b_torch = input.float()
        else:
            b_torch = torch.from_numpy(input).unsqueeze(0).unsqueeze(0)
        # check if the input is already in LF 4D format
        if b_torch.ndim == 6:
            LF_input = b_torch
        else:
            print(b_torch.shape)
            LF_input = LF2Spatial(b_torch, self.LF_in_shape)
        # Pad input with half the LFNet fov, to get an output the same size as the input image
        if LF_input.shape[-2] < self.LF_in_shape[-2] and LF_input.shape[-1] < self.LF_in_shape[-1]:
            LF_padded = F.pad(LF_input, 4*[self.LF_in_fov//2])
        else:
            LF_padded = LF_input
        # Normalize by max
        if LF_padded.max() > 1.0:
            LF_padded /= self.max_LF_train.item()
        return LF_padded
    
    def forward(self, input):
        input_ready = self.prepare_input(input).to(self.device)
        # 4D convolution
        inputAfter4DConv = self.lensletConvolution(input_ready)
        # 4D to 2D image
        newLFSize = inputAfter4DConv.shape[2:]
        newLensletImage = LF2Spatial(inputAfter4DConv, newLFSize)
        # U-net prediction
        x = self.Unet(newLensletImage)
        # Channels to 3D dimension 
        x3D = x.permute((0,2,3,1)).unsqueeze(1)
        return x3D
