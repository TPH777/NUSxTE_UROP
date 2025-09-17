import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
from torchvision.datasets import ImageFolder
from torchvision.utils import save_image
from PIL import Image
from pretrain_conditional_encoder import BetaVAE, EncoderWithLatent, denormalize, WeldingDataset
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

def generate_random_from_class(vae, class_label, latent_dim=16, num_samples=3, noise_factor=0.3):
    random_latents = torch.randn(num_samples, latent_dim).to(device)
    label_embedding = vae.get_label_embedding(class_label)
    label_embedding_expanded = label_embedding.repeat(num_samples, 1)
    random_latents = random_latents + noise_factor * random_latents.std(dim=1, keepdim=True) * torch.randn_like(random_latents)
    with torch.no_grad():
        synthetic_images = vae.decoder(random_latents, label_embedding_expanded)

    return synthetic_images

if __name__ == "__main__":
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  latent_dim = 16
  image_size = 224
  channels = 3
  batch_size = 1
  num_synthetic_per_image = 3
  dataset_path = 'train'
  output_path = 'synthetic_conditional'

  transform = transforms.Compose([
      transforms.Resize((image_size, image_size)),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize with ImageNet stats
  ])

  resnet = models.resnet18(pretrained=True)
  encoder = EncoderWithLatent(resnet)
  # Load trained weights
  vae = BetaVAE(encoder,latent_dim=16, beta=1).to(device)
  vae.load_state_dict(torch.load('vae_model.pth'))
  vae.eval()
  k = 1
  noise_factor = 0.3
  
  dataset = datasets.ImageFolder(root=dataset_path, transform=transform)
  dataloader = DataLoader(dataset, batch_size=1, shuffle=True)
  synthetic_images = []
  for i in range(5):
    class_label = torch.LongTensor([i]).to(device)
    generated_images = generate_random_from_class(vae, class_label)
    print(generated_images.shape)
    synthetic_images.append(generated_images)
  for synth_img in synthetic_images:
      for i, img in enumerate(synth_img):
          image_norm = denormalize(img)
          #print(image_norm.shape)
          pixel_values = torch.clamp(image_norm, 0, 1) * 255
          pixel_values = pixel_values.to(torch.uint8)
          to_pil = ToPILImage()
          pil_img = to_pil(pixel_values.cpu())
          if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
          pil_img.save(f"generated_{k+1}.png")
          k += 1
  print(f"Synthetic images generated and saved in '{output_path}'")