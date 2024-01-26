from collections import OrderedDict

import torch.nn as nn


# Code adapted from https://github.com/amirhossein-kz/HiFormer

class ConvUpsample(nn.Module):
    def __init__(self, in_chans=384, out_chans=[128], upsample=True):
        super().__init__()
        self.in_chans = in_chans
        self.out_chans = out_chans

        self.conv_tower = nn.ModuleList()
        for i, out_ch in enumerate(self.out_chans):
            if i > 0: self.in_chans = out_ch
            self.conv_tower.append(nn.Conv2d(
                self.in_chans, out_ch,
                kernel_size=3, stride=1,
                padding=1, bias=False
            ))
            self.conv_tower.append(nn.GroupNorm(32, out_ch))
            self.conv_tower.append(nn.ReLU(inplace=False))
            if upsample:
                self.conv_tower.append(nn.Upsample(
                    scale_factor=2, mode='bilinear', align_corners=False))

        self.convs_level = nn.Sequential(*self.conv_tower)

    def forward(self, x):
        return self.convs_level(x)


class HiFormerSegmentationHead(nn.Sequential):
    def __init__(self, out_channels, kernel_size=3, dec_channels=[16]):
        self.modules = OrderedDict()
        for i in range(1, len(dec_channels)):
            is_last_conv = i == len(dec_channels) - 1
            self.modules[f"dec_conv_{i}"] = nn.Conv2d(dec_channels[i - 1], dec_channels[i], kernel_size=kernel_size,
                                                      padding=0, bias=True)
            if not is_last_conv:
                self.modules[f"dec_act_{i}"] = nn.ReLU()
        self.modules["dec_final_conv"] = nn.Conv2d(dec_channels[-1], out_channels, kernel_size=kernel_size,padding=0,
                                                   bias=True)
        super().__init__(self.modules)
