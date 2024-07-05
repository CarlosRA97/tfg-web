from torch import nn
import segmentation_models_pytorch as smp
from segmentation_models_pytorch.losses import DiceLoss

class SegmentationModel(nn.Module):
    def __init__(self, net = "Linknet", encoder = "resnet50", weights="imagenet"):
        super(SegmentationModel,self).__init__()

        if net == "Unet":
          self.arc=smp.Unet(
              encoder_name=encoder,
              encoder_weights=weights,
              in_channels=3,
              classes=1,
              activation=None
          )

        if net == "DeepLab":
          self.arc=smp.DeepLabV3(
              encoder_name=encoder,
              encoder_weights=weights,
              in_channels=3,
              classes=1,
              activation=None
          )

        if net == "FPN":
          self.arc=smp.FPN(
              encoder_name=encoder,
              encoder_weights=weights,
              in_channels=3,
              classes=1,
              activation=None
          )

        if net == "Linknet":
          self.arc=smp.Linknet(
              encoder_name=encoder,
              encoder_weights=weights,
              in_channels=3,
              classes=1,
              activation=None
          )


    def forward(self,images,masks=None):
        logits=self.arc(images)

        if masks!=None:
            loss1=DiceLoss(mode='binary')(logits,masks)
            loss2=nn.BCEWithLogitsLoss()(logits,masks)
            return logits,loss1,loss2
        return logits