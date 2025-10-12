import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
from transformers import ViTImageProcessor, ViTForImageClassification
import argparse

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def train_model(train_dir, valid_dir, num_epochs=20, batch_size=1, lr=0.0001):
    # Set seed for reproducibility
    set_seed(42)

    # Data Augmentation and Normalization
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Load Datasets
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    valid_dataset = datasets.ImageFolder(valid_dir, transform=val_test_transform)

    # DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    valid_loader = DataLoader(valid_dataset, batch_size=batch_size)

    # Load Model
    model_name = "google/vit-base-patch16-224-in21k"
    feature_extractor = ViTImageProcessor.from_pretrained(model_name)
    model = ViTForImageClassification.from_pretrained(model_name, num_labels=len(train_dataset.classes))

    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    
    # Learning Rate Scheduler
    scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=0.001, total_steps=len(train_loader) * num_epochs)

    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    best_validation_accuracy = 0.0

    # Training Loop
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs.logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # Validation Loop
        model.eval()
        with torch.no_grad():
            correct = 0
            total = 0
            for inputs, labels in valid_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.logits, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            validation_accuracy = 100 * correct / total

            if validation_accuracy > best_validation_accuracy:
                best_validation_accuracy = validation_accuracy
                torch.save(model.state_dict(), "best_model.pth")

        print(f"Epoch [{epoch + 1}/{num_epochs}] "
              f"Loss: {running_loss / len(train_loader):.4f} "
              f"Validation Accuracy: {validation_accuracy:.2f}%")

        scheduler.step()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a Vision Transformer for Image Classification")
    parser.add_argument("--train_dir", type=str, help="Path to the training dataset")
    parser.add_argument("--valid_dir", type=str, help="Path to the validation dataset")

    args = parser.parse_args()

    train_model(args.train_dir, args.valid_dir)
