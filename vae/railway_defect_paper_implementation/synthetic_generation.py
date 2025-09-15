import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torchvision.utils import save_image
from PIL import Image
import random
from train_vae import VAE

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Parameters - adjust as needed
latent_dim = 32
image_size = 256
channels = 1
batch_size = 1  # Process one image at a time for reconstruction
num_synthetic_per_image = 3  # Number of synthetic images to generate per original image

dataset_path = 'validation_images'          # Original images root folder, structured by class
output_path = 'synthetic'    # Where to save generated images

# Image preprocessing same as training
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=channels),
    transforms.Resize((image_size, image_size)),
    transforms.ToTensor(),
])

# Define Encoder, Decoder, VAE classes exactly as in training code here or import if modularized

# [Insert your Encoder, Decoder, VAE class definitions here]
# For brevity, omitted here - use the same classes as training script.

# For demonstration, assume `vae` is your model and is defined

# Load trained weights
vae = VAE(latent_dim).to(device)
vae.load_state_dict(torch.load('vae_model.pth'))
vae.eval()

# Helper function: sample multiple latent vectors from encoder output distribution
def sample_latents(mu, logvar, n_samples):
    std = torch.exp(0.5 * logvar)
    samples = []
    for _ in range(n_samples):
        eps = torch.randn_like(std)
        z = mu + eps * std
        samples.append(z)
    return torch.cat(samples, dim=0)

# For each class, generate synthetic images
for cls in os.listdir(dataset_path):
    class_dir = os.path.join(dataset_path, cls)
    if not os.path.isdir(class_dir):
        continue

    output_class_dir = os.path.join(output_path, cls)
    os.makedirs(output_class_dir, exist_ok=True)

    image_files = [f for f in os.listdir(class_dir)
                   if any(f.endswith(ext) for ext in ['png', 'jpg', 'jpeg'])]

    for img_name in image_files:
        img_path = os.path.join(class_dir, img_name)
        image = Image.open(img_path).convert('L')  # Grayscale
        input_tensor = transform(image).unsqueeze(0).to(device)  # Shape: [1,1,H,W]

        # Encode to latent space
        with torch.no_grad():
            mu, logvar = vae.encoder(input_tensor)

        # Sample multiple latent vectors
        latent_vectors = sample_latents(mu, logvar, num_synthetic_per_image)

        with torch.no_grad():
            # Decode each latent vector to generate synthetic images
            synthetic_images = vae.decoder(latent_vectors)

        # Save each synthetic image
        for i, synth_img in enumerate(synthetic_images):
            save_name = f"{os.path.splitext(img_name)[0]}_synth_{i+1}.png"
            save_path = os.path.join(output_class_dir, save_name)
            save_image(synth_img, save_path)

print(f"Synthetic images generated and saved in '{output_path}'")