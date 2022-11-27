import pytorch_lightning as pl
import torch
import torch.nn as nn

# Parent class, containing required parameters and classes for a LF network
class LFNeuralNetworkProto(pl.LightningModule):
    def __init__(self, input_shape, output_shape, network_settings_dict={}, training_settings_dict={}):
        super().__init__()
        self.input_shape = input_shape
        self.output_shape = output_shape
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
    
    # Required: this is where you create your network, see LFMNet or VCDNet as examples
    def init_network_instance(self):
        raise NotImplementedError
    # Format a LF with size [ax,ay,sx,sy] (a:angular s:spatial)
    # into the shape required by the network
    def prepare_input(self, input):
        raise NotImplementedError
    # If a pretrained network is available load it
    def load_model(self, path):
        pass