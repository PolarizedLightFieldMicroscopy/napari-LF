import pytorch_lightning as pl
import torch
from torch.utils import data
import torch.nn as nn
import torchvision as tv
from neural_nets.util.LFUtil import *
from neural_nets.util.convNd import convNd
from neural_nets.LFNeuralNetworkProto import LFNeuralNetworkProto
    

# VCDNet definition
class VCDNet(LFNeuralNetworkProto):
    def init_network_instance(self):
        # Required: default network settings
        self.default_net_settings = {'n_Depths'         : 64, 
                                     'LF_in_shape'      : [33,33,39,39], 
                                     'n_interp'         : 4,
                                     'channels_interp'  : 128,
                                     'use_small_unet'   : True}
        
        # Populate members, based on user provided or default settings
        self.n_Depths = self.get_setting('n_Depths')
        self.LF_in_shape = self.get_setting('LF_in_shape')
        self.n_interp = self.get_setting('n_interp')
        channels_interp = self.get_setting('channels_interp')
        
        # Create upsampling step
        self.net_upsample = [nn.Conv2d(self.LF_in_shape[0]*self.LF_in_shape[1], channels_interp, kernel_size=7, padding=3)]
        for i in range(self.n_interp):
            self.net_upsample.append(
                nn.PixelShuffle(2)
            )
            channels_interp = channels_interp // 2
            self.net_upsample.append(
                nn.Conv2d(channels_interp//2, channels_interp, kernel_size=3, padding=1)
            )
        self.net_upsample.append(
            nn.Conv2d(channels_interp, channels_interp, kernel_size=3, padding=1)
        )
        self.net_upsample.append(
            nn.BatchNorm2d(channels_interp)
        )
        self.net_upsample.append(
            nn.ReLU()
        )
        self.net_upsample = nn.Sequential(*self.net_upsample)
        
        # Create Encoder
        pyramid_channels = [128,256,512,512]
        self.encoder_layers = [
            nn.Sequential(nn.Conv2d(channels_interp, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU())
        ]
        previous_nc = self.n_Depths
        for idx, nc in enumerate(pyramid_channels):
            self.encoder_layers.append(nn.Sequential(nn.Conv2d(previous_nc, nc, kernel_size=3, stride=1),
                                                nn.BatchNorm2d(nc),
                                                nn.ReLU(),
                                                nn.MaxPool2d(3, 2))) 
            previous_nc = nc
        self.encoder_layers = nn.Sequential(*self.encoder_layers)
        
        # Create Decoder
        channels_inverted = pyramid_channels[::-1]
        self.decoder_layers = [nn.Sequential(
                nn.Conv2d(channels_inverted[0], channels_inverted[1], kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                nn.BatchNorm2d(channels_inverted[1])
            )]
        for idx in range(1,len(channels_inverted)):
            
            self.decoder_layers.append(nn.Sequential(
                nn.Conv2d(channels_inverted[idx]+channels_inverted[idx-1], channels_inverted[idx], kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                nn.BatchNorm2d(channels_inverted[idx])
            ))
            # print(f'{channels_inverted[idx]+channels_inverted[idx-1]}  {channels_inverted[idx]}')
        self.decoder_layers.append(nn.Sequential(
                nn.Conv2d(channels_inverted[-1]+self.n_Depths, self.n_Depths, kernel_size=3, stride=1, padding=1),
                nn.Tanh()
            ))
        # Create decoder
        self.decoder_layers = nn.Sequential(*self.decoder_layers)
        
        # Init all layers
        def subnet_initialization_small(m):
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.Conv3d) or isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight.data)
                # nn.init.xavier_uniform_(m.weight.data,0.01)
                # if m.bias is not None:
                #     m.bias.data *= 0.01
        
        # self.apply(subnet_initialization_small)
    
    
    def prepare_input(self, input):
        # todo: maybe assert shape
        if torch.is_tensor(input):
            LF_input = input.float()
        else:
            b_torch = torch.from_numpy(input).unsqueeze(0).unsqueeze(0)
            LF_input = LF2Spatial(b_torch, self.LF_in_shape)
        # Pad input with half the LFNet fov, to get an output the same size as the input image
        LF_VCD = LF_input.view(LF_input.shape[0],-1, *LF_input.shape[-2:])
        # Normalize by max: todo: this should be stored in arguments
        if LF_VCD.max() > 1.0:
            LF_VCD /= self.max_LF_train.item()
        LF_VCD[LF_VCD==0] = LF_VCD[LF_VCD!=0.0].min()
        return LF_VCD
    
    def forward(self, input):
        input_ready = self.prepare_input(input).to(self.device)
        # Upsample views
        upsampled_views = self.net_upsample(input_ready)
        
        # Encoder
        outputs = [self.encoder_layers[0](upsampled_views)]
        for layer in self.encoder_layers[1:]:
            outputs.append(layer(outputs[-1]))
        
        # Decoder
        curr_level = self.decoder_layers[0](outputs[-1])
        for ix in range(1,len(outputs)):
            up_sampled = torch.nn.functional.interpolate(curr_level, outputs[-(ix+1)].shape[2:])
            cat_level = torch.cat((up_sampled, outputs[-(ix+1)]), 1)
            curr_level = self.decoder_layers[ix](cat_level)
        
        # Channels to 3D dimension 
        x3D = curr_level.permute((0,2,3,1)).unsqueeze(1)
        return x3D
    
    # Configure dataloader, each architeture may need different shape of input/outputs
    def configure_dataloader(self):
        self.default_training_settings = {'epochs'              : 3, 
                                          'images_ids'          : list(range(10,15)), 
                                          'batch_size'          : 1,
                                          'validation_split'    : 0.1,
                                          'learning_rate'       : 1e-3,
                                          'volume_threshold'    : 0.03,
                                          'dataset_path'        : 'D:\\BrainImagesJosuePage\\Brain_40x_64Depths_362imgs.h5',
                                          'output_dir'          : ''}
        
        # Load data
        all_data = Dataset(self.get_train_setting('dataset_path'), 261290, \
                        fov=0, 
                        neighShape=0, 
                        img_indices=self.get_train_setting('images_ids'), 
                        get_full_imgs=True, center_region=None)
        
        # Resize volumes to correct upsampling size
        all_data.VolFull = F.interpolate(all_data.VolFull.permute(3,2,0,1), 2*[self.LF_in_shape[-2]*2**self.n_interp]).permute(2,3,1,0)
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