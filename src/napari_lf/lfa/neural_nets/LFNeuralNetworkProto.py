import pytorch_lightning as pl
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision as tv
from neural_nets.util.LFUtil import *

# Parent class, containing required parameters and classes for a LF network
class LFNeuralNetworkProto(pl.LightningModule):
    def __init__(self, input_shape, output_shape, network_settings_dict={}, training_settings_dict={}, name='LFNeuralNetworkProto'):
        super().__init__()
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.name = self.__class__.__name__
        # Specific settings needed for a network instance
        self.network_settings_dict = network_settings_dict
        self.training_settings_dict = training_settings_dict
        self.default_net_settings = None
        self.default_training_settings = None
        # Function to either use the default settings or choose from user provided settings
        self.get_setting = lambda setting_name: self.network_settings_dict[setting_name] if setting_name in self.network_settings_dict.keys() else self.default_net_settings[setting_name] 
        self.get_train_setting = lambda setting_name: self.training_settings_dict[setting_name] if setting_name in self.training_settings_dict.keys() else self.default_training_settings[setting_name] 
        # Initiallize instance
        self.init_network_instance()
        self.save_hyperparameters()
        self.hparams['name'] = self.name
        # Normalization values
        self.max_LF_train = nn.Parameter(torch.tensor(255.0))
        self.max_vol_train = nn.Parameter(torch.tensor(255.0))
    
############## Required: this is where you create your network, see LFMNet or VCDNet as examples
    def init_network_instance(self): # Create network structure (encoders,decoders, etc.)
        raise NotImplementedError
    
    # Format a LF with size [ax,ay,sx,sy] (a:angular s:spatial)
    # into the shape required by the network
    def prepare_input(self, input):
        raise NotImplementedError
    
############## The following functions work for LFMNet and VCDNet, feel free to overload them with your own implementation
    # Evaluate sample
    def evaluate_sample(self, batch, batch_idx, logging_tag='val'):
        # Load image and volume
        LF_in, vol_in = batch
        # Normalize input and output with stored values from training
        LF_in_norm = LF_in / self.max_LF_train.item()
        vol_in_norm = vol_in / self.max_vol_train.item()
        
        # Predict 3D volume from LF image
        vol_pred = self.forward(LF_in_norm)
        # Compute error (Mean square error in this case)
        loss = F.mse_loss(vol_in_norm, vol_pred)
        self.log(f'loss/{logging_tag}', loss.detach())
        
        if logging_tag=='val':
            self.log("hp_metric", loss.detach())

        # Log to tensorboard
        if self.global_step % 100 or batch_idx==0:
            tensorboard = self.logger.experiment
            tensorboard.add_image(f'GT/{logging_tag}', 
                                tv.utils.make_grid(
                                    volume_2_projections(
                                        vol_in_norm, 
                                        depths_in_ch=False)[0,0,...].float().unsqueeze(0).cpu().data.detach(), 
                                    normalize=True, 
                                    scale_each=False), self.global_step)
            tensorboard.add_image(f'pred/{logging_tag}', 
                                tv.utils.make_grid(
                                    volume_2_projections(
                                        vol_pred, 
                                        depths_in_ch=False)[0,0,...].float().unsqueeze(0).cpu().data.detach(), 
                                    normalize=True, 
                                    scale_each=False), self.global_step)
        return loss
    
    # training_step defines the train loop.  
    def training_step(self, batch, batch_idx):
        return self.evaluate_sample(batch, batch_idx, 'train')
    
    def validation_step(self, batch, batch_idx):
        return self.evaluate_sample(batch, batch_idx, 'val')
    
    
    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.get_train_setting('learning_rate'))
        return optimizer