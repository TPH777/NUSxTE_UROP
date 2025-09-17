import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torchvision.utils import save_image
from PIL import Image
from pretrain_encoder import BetaVAE, EncoderWithLatent, denormalize, WeldingDataset
import torchvision.models as models
from torchvision.transforms import ToPILImage

def sample_latents(mu, logvar, n_samples):
    std = torch.exp(0.5 * logvar)
    samples = []
    for _ in range(n_samples):
        eps = torch.randn_like(std)
        z = mu + eps * std
        samples.append(z)
    return torch.cat(samples, dim=0)

if __name__ == "__main__":
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

  latent_dim = 16
  image_size = 224
  channels = 3
  batch_size = 1
  num_synthetic_per_image = 3

  dataset_path = 'test/unwelded'
  output_path = 'synthetic'

  transform = transforms.Compose([
      transforms.Resize((image_size, image_size)),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize with ImageNet stats
  ])
  resnet = models.resnet18(pretrained=True)
  encoder = EncoderWithLatent(resnet)
  vae = BetaVAE(encoder,latent_dim=16, beta=1).to(device)
  vae.load_state_dict(torch.load('vae_model_current.pth'))
  vae.eval()
  k = 1
  noise_factor = 0.5
  
  welding_dataset = WeldingDataset(image_folder=dataset_path, transform=transform)
  welding_dataloader = DataLoader(welding_dataset, batch_size=1)
  for x in welding_dataloader:
    with torch.no_grad():
        mu, logvar = vae.encoder(x)

    latent_vectors = sample_latents(mu, logvar, num_synthetic_per_image)
    latent_vectors = latent_vectors + noise_factor * latent_vectors.std(dim=1, keepdim=True) * torch.randn_like(latent_vectors)

    with torch.no_grad():
        synthetic_images = vae.decoder(latent_vectors)
    for synth_img in synthetic_images:
        image_norm = denormalize(synth_img)
        pixel_values = torch.clamp(image_norm, 0, 1) * 255
        pixel_values = pixel_values.to(torch.uint8)
        to_pil = ToPILImage()
        pil_img = to_pil(pixel_values.cpu())
        if pil_img.mode != 'RGB':
          pil_img = pil_img.convert('RGB')
        pil_img.save(f"generated_{k+1}.png")
        k += 1

  print(f"Synthetic images generated and saved in '{output_path}'")