import os
import torch
import argparse
from datetime import datetime
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
from transformers import ViTForImageClassification
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

def main():
    # Argument parser for test_dir
    parser = argparse.ArgumentParser(description="Evaluate a ViT model on a test dataset")
    parser.add_argument("--test_dir", type=str, required=True, help="Path to test dataset directory")
    args = parser.parse_args()

    test_dir = args.test_dir

    # Transforms
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Dataset and DataLoader
    test_dataset = datasets.ImageFolder(test_dir, transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=1)

    # Load pre-trained model and weights
    model_name = "google/vit-base-patch16-224-in21k"
    model = ViTForImageClassification.from_pretrained(model_name, num_labels=len(test_dataset.classes))
    model.load_state_dict(torch.load("best_model.pth"))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    # Evaluation metrics
    class_correct = [0] * len(test_dataset.classes)
    class_total = [0] * len(test_dataset.classes)
    misclassified_images = []

    all_true_labels = []
    all_predicted_labels = []

    with torch.no_grad():
        for batch_idx, (inputs, labels) in enumerate(test_loader):
            inputs, labels = inputs.to(device), labels.to(device)
            
            outputs = model(inputs)
            _, predicted = torch.max(outputs.logits, 1)

            all_true_labels.extend(labels.cpu().numpy())
            all_predicted_labels.extend(predicted.cpu().numpy())
            
            for i in range(len(labels)):
                label = labels[i].item()
                class_total[label] += 1
                
                if predicted[i] == labels[i]:
                    class_correct[label] += 1
                else:
                    img_path = test_dataset.imgs[batch_idx][0]
                    true_class = test_dataset.classes[label]
                    predicted_class = test_dataset.classes[predicted[i].item()]
                    
                    misclassified_images.append({
                        'true_class': true_class,
                        'predicted_class': predicted_class,
                        'full_path': img_path
                    })

    print(f"Current datetime: {datetime.now()}")
    for i in range(len(test_dataset.classes)):
        accuracy = 100 * class_correct[i] / class_total[i] if class_total[i] > 0 else 0
        print(f"Accuracy for class {test_dataset.classes[i]}: {accuracy:.2f}%")

    print(f"\nMisclassified images ({len(misclassified_images)} total):")
    for item in misclassified_images:
        print(f"File: {item['full_path']} | True (folder): {item['true_class']} | Predicted: {item['predicted_class']}")

    cm = confusion_matrix(all_true_labels, all_predicted_labels)
    cm_df = pd.DataFrame(cm, index=test_dataset.classes, columns=test_dataset.classes)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print("Confusion Matrix with Class Labels:")
        print(cm_df)

if __name__ == "__main__":
    main()
