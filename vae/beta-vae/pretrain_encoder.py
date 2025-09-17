import torch
import torchvision.models as models
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision import models
from PIL import Image
import os
import matplotlib.pyplot as plt
import torchvision.utils as vutils
import torch.nn.functional as F
from torchvision.transforms import ToPILImage

class EncoderWithLatent(nn.Module):
    def __init__(self, original_model, latent_dim=16):
        super().__init__()
        self.features = nn.Sequential(*list(original_model.children())[:-2]) #take out the fc layers 
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1)) #pool the dimensions to 1,512,1,1
        self.flatten = nn.Flatten()
        # created intermediate layer to increase the smooth extraction of feature to latent space
        self.fc_mu = nn.Sequential(
            nn.Linear(512, 128),
            nn.ReLU(True),
            nn.Linear(128, latent_dim)
        )
        # created intermediate layer to increase the smooth extraction of feature to latent space
        self.fc_log_var = nn.Sequential(
            nn.Linear(512, 128),
            nn.ReLU(True),
            nn.Linear(128, latent_dim)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)  
        x = self.flatten(x)  
        mu = self.fc_mu(x)  
        log_var = self.fc_log_var(x) 
        return mu, log_var
    
class Decoder(nn.Module):
    def __init__(self, latent_dim=16, output_channels=3):
        super(Decoder, self).__init__()

        # FC layer to expand latent vector into feature map
        self.fc = nn.Sequential(
            nn.Linear(latent_dim, 128 * 7 * 7),
            nn.ReLU(True)
        )

        self.deconv = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, 2, 1),   # 7 → 14
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.ConvTranspose2d(64, 32, 4, 2, 1),   # 14 → 28
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.ConvTranspose2d(32, 16, 4, 2, 1),    # 28 → 56
            nn.BatchNorm2d(16),
            nn.ReLU(True),
            nn.ConvTranspose2d(16, 8, 4, 2, 1),     # 56 → 112
            nn.BatchNorm2d(8),
            nn.ReLU(True),
            nn.ConvTranspose2d(8, output_channels, 4, 2, 1),  # 112 → 224
            #nn.Tanh()  
        )

    def forward(self, z):
        z = self.fc(z)
        z = z.view(-1, 128, 7, 7)
        x = self.deconv(z)
        return x

class BetaVAE(nn.Module):
    def __init__(self, encoder, latent_dim=16, beta=1.0): #beta=1 is the vanilla vae
        super(BetaVAE, self).__init__()
        self.encoder = encoder
        self.decoder = Decoder(latent_dim)
        self.latent_dim = latent_dim
        self.beta = beta

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        mu, log_var = self.encoder(x)
        z = self.reparameterize(mu, log_var)
        print(z.shape)
        reconstructed_x = self.decoder(z)
        return reconstructed_x, mu, log_var

    def loss_function(self, recon_x, x, mu, log_var):
        #BCE = nn.functional.binary_cross_entropy_with_logits(recon_x, x, reduction='sum')
        reconstruction_loss = F.mse_loss(recon_x, x, reduction='sum')

        # KL Divergence loss
        # D_KL = -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
        # where sigma is exp(0.5 * log_var)
        # KL loss encourages the latent space to approximate a normal distribution
        KL_div = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())

        # Final loss with the β hyperparameter controlling the trade-off
        return reconstruction_loss + self.beta * KL_div
    
class WeldingDataset(Dataset):
    def __init__(self, image_folder, transform=None):
        self.image_folder = image_folder
        self.transform = transform
        self.image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = os.path.join(self.image_folder, self.image_files[idx])
        image = Image.open(img_name).convert('RGB')  # Assuming RGB images

        if self.transform:
            image = self.transform(image)

        return image

def denormalize(tensor):
    """
    tensor: shape [C, H, W] or [B, C, H, W], normalized with given mean/std
    returns denormalized tensor with pixel values roughly in [0,1]
    """
    mean = torch.tensor([0.485, 0.456, 0.406], device=tensor.device).view(-1,1,1)
    std = torch.tensor([0.229, 0.224, 0.225], device=tensor.device).view(-1,1,1)

    if tensor.dim() == 4:  # batch of images
        mean = mean.unsqueeze(0)  # shape [1, C, 1, 1]
        std = std.unsqueeze(0)

    return tensor * std + mean

def show_tensor(tensor, title=""):
    img = tensor.permute(1,2,0).cpu().detach().numpy()
    plt.imshow(img)
    plt.title(title)
    plt.axis('off')
    plt.show()

def train():
  resnet = models.resnet18(pretrained=True)

  image_folder = '../images/unwelded'

  transform = transforms.Compose([
      transforms.Resize((224, 224)),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
  ])

  welding_dataset = WeldingDataset(image_folder=image_folder, transform=transform)
  welding_dataloader = DataLoader(welding_dataset, batch_size=5, shuffle=True)
  encoder = EncoderWithLatent(resnet)
  vae = BetaVAE(encoder, latent_dim=16, beta=1)
  optimizer = torch.optim.Adam(vae.parameters(), lr=1e-3)

  num_epochs = 200
  best_epoch = 1000000
  for epoch in range(num_epochs):
      vae.train()
      epoch_loss = 0

      for i, x in enumerate(welding_dataloader):
          optimizer.zero_grad()  # Zero the gradients
          reconstructed_x, mu, log_var = vae(x)
          loss = vae.loss_function(reconstructed_x, x, mu, log_var)
          loss.backward()
          optimizer.step()
          epoch_loss += loss.item()
      if epoch_loss / len(welding_dataloader) < best_epoch:
          torch.save(vae.state_dict(), 'vae_model.pth')
          best_epoch = epoch_loss / len(welding_dataloader)
      print(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss / len(welding_dataloader)}")
      if (epoch + 1) % 10 == 0:
        image_norm = denormalize(reconstructed_x)
        pixel_values = torch.clamp(image_norm, 0, 1) * 255
        pixel_values = pixel_values.to(torch.uint8)
        to_pil = ToPILImage()
        pil_img = to_pil(pixel_values[0].cpu())
        pil_img.save(f"reconstructed_epoch_{epoch+1}.png")
        #show_tensor(x[0], "Input (normalized)")
        #show_tensor(image_norm[0], "Reconstruction (normalized)")

if __name__ == "__main__":
  train() 