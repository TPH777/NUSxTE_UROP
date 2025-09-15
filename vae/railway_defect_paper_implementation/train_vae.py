import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torchvision.utils import save_image
from tqdm import tqdm

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

image_size = 256        # the pixel size for the input for network
channels = 1            # 1 for greyscale, 3 for rgb
latent_dim = 32         # Latent space dimensionality
batch_size = 16         
learning_rate = 1e-3    
num_epochs = 100       
weight_decay_lambda = 1e-4  # Weight decay coefficient for model regularization (paper adds weight decay to reconstruction loss)

# resizes the TE image (299 x 299) to (256 x 256)
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=channels),
    transforms.Resize((image_size, image_size)),
    transforms.ToTensor(),
])

# Dataset loading assumes folder structure by class as in CPR defect dataset
dataset_path = '~/vae/images'  # Replace with your dataset path
dataset = ImageFolder(root=dataset_path, transform=transform)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# encodes the image to meaning in latent space 
class Encoder(nn.Module):
    def __init__(self, latent_dim):
        super(Encoder, self).__init__()
        self.conv1 = nn.Conv2d(channels, 32, kernel_size=4, stride=2, padding=1)  # 256 -> 128
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1)        # 128 -> 64
        self.conv3 = nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1)       # 64 -> 32
        self.conv4 = nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1)      # 32 -> 16
        self.conv5 = nn.Conv2d(256, 512, kernel_size=4, stride=2, padding=1)      # 16 -> 8
        self.conv6 = nn.Conv2d(512, 1024, kernel_size=4, stride=2, padding=1)      # 8 -> 4
        self.flatten = nn.Flatten()
        self.fc_mu = nn.Linear(1024*4*4, latent_dim)       # used later for the latent means
        self.fc_logvar = nn.Linear(1024*4*4, latent_dim)   # used later for the latent log variances

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))
        x = F.relu(self.conv6(x))
        x = self.flatten(x)
        mu = self.fc_mu(x)         # Latent means for reparameterization
        logvar = self.fc_logvar(x) # Latent log variances
        return mu, logvar

# reconstructing the images 
class Decoder(nn.Module):
    def __init__(self, latent_dim):
        super(Decoder, self).__init__()
        self.fc = nn.Linear(latent_dim, 1024*4*4)  # latent vector back to the features
        self.deconv1 = nn.ConvTranspose2d(1024, 512, 4, 2, 1)  # Upsample 4->8
        self.deconv2 = nn.ConvTranspose2d(512, 256, 4, 2, 1)  # Upsample 8->16
        self.deconv3 = nn.ConvTranspose2d(256, 128, 4, 2, 1)   # Upsample 16->32
        self.deconv4 = nn.ConvTranspose2d(128, 64, 4, 2, 1)   # Upsample 32->64
        self.deconv5 = nn.ConvTranspose2d(64, 32, 4, 2, 1)    # Upsample 64->128
        self.deconv6 = nn.ConvTranspose2d(32, channels, 4, 2, 1)  # Upsample 128->256

    def forward(self, z):
        x = self.fc(z)
        x = x.view(-1, 1024, 4, 4)
        x = F.relu(self.deconv1(x))
        x = F.relu(self.deconv2(x))
        x = F.relu(self.deconv3(x))
        x = F.relu(self.deconv4(x))
        x = F.relu(self.deconv5(x))
        x = torch.sigmoid(self.deconv6(x))  # Sigmoid to constrain output to [0, 1]
        return x

class VAE(nn.Module):
    def __init__(self, latent_dim):
        super(VAE, self).__init__()
        self.encoder = Encoder(latent_dim)
        self.decoder = Decoder(latent_dim)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)      # Standard deviation from log variance
        eps = torch.randn_like(std)        # Random noise for sampling latent vector
        return mu + eps * std              # Reparameterization trick enabling gradient flow

    def forward(self, x):
        mu, logvar = self.encoder(x)      # Encode input image to latent distribution parameters
        z = self.reparameterize(mu, logvar) # Sample latent vector
        x_recon = self.decoder(z)         # Decode to reconstructed image
        return x_recon, mu, logvar

# Loss function implementing paper’s combined loss: reconstruction + KL divergence + weight decay
def loss_function(x_recon, x, mu, logvar, model, weight_decay_lambda):
    recon_loss = F.mse_loss(x_recon, x, reduction='sum')  # Reconstruction loss: MSE between input and output images
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())  # KL divergence: regularizes latent space towards N(0, I)
    l2_reg = torch.tensor(0., requires_grad=True).to(device)
    for param in model.parameters():
        l2_reg = l2_reg + torch.sum(param ** 2)            # Weight decay: penalize large weights for regularization
    total_loss = recon_loss + kl_loss + weight_decay_lambda * l2_reg
    return total_loss, recon_loss, kl_loss


if __name__ == "__main__":
  # Create model instance and optimizer
  vae = VAE(latent_dim).to(device)
  optimizer = torch.optim.Adam(vae.parameters(), lr=learning_rate)
  # Training loop
  vae.train()
  for epoch in range(num_epochs):
      train_loss = 0
      recon_loss_total = 0
      kl_loss_total = 0
      loop = tqdm(dataloader, desc=f"Epoch {epoch + 1}/{num_epochs}", leave=False)
      for inputs, _ in loop:
          inputs = inputs.to(device)         # Move inputs to GPU if available
          optimizer.zero_grad()              # Reset optimizer grads
          outputs, mu, logvar = vae(inputs) # Forward pass through VAE
          loss, recon_loss, kl_loss = loss_function(outputs, inputs, mu, logvar, vae, weight_decay_lambda) # Compute total loss
          loss.backward()                   # Backpropagation
          optimizer.step()                  # Update weights

          train_loss += loss.item()
          recon_loss_total += recon_loss.item()
          kl_loss_total += kl_loss.item()

          loop.set_postfix(
              Loss=train_loss / len(dataset),
              Reconstruction=recon_loss_total / len(dataset),
              KL_Divergence=kl_loss_total / len(dataset)
          )

      print(f'Epoch {epoch+1}/{num_epochs} Loss: {train_loss / len(dataset):.4f}, '
            f'Reconstruction: {recon_loss_total / len(dataset):.4f}, KL Divergence: {kl_loss_total / len(dataset):.4f}')

      # Every 10 epochs, save reconstructions for visualization as per paper’s evaluation approach
      if (epoch + 1) % 5 == 0:
          vae.eval()
          with torch.no_grad():
              sample = inputs[:8]          # Take 8 images from last batch
              recon, _, _ = vae(sample)   # Reconstruct from VAE
              save_image(recon.cpu(), f'recon_epoch_{epoch+1}.png')
          vae.train()

  # Save final model weights (paper mentions saving model for synthetic image generation)
  torch.save(vae.state_dict(), 'vae_model.pth')