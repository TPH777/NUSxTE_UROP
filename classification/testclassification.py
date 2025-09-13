import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
from transformers import ViTForImageClassification

data_dir = "classification_images"

test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

test_dataset = datasets.ImageFolder(os.path.join(data_dir, "test"), transform=test_transform)
test_loader = DataLoader(test_dataset, batch_size=1)

model_name = "google/vit-base-patch16-224-in21k"
model = ViTForImageClassification.from_pretrained(model_name, num_labels=len(test_dataset.classes))

model.load_state_dict(torch.load("best_model.pth"))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

model.eval()

class_correct = [0] * len(test_dataset.classes)
class_total = [0] * len(test_dataset.classes)

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        outputs = model(inputs)
        _, predicted = torch.max(outputs.logits, 1)
        
        for i in range(len(labels)):
            label = labels[i].item()
            class_total[label] += 1
            class_correct[label] += (predicted[i] == labels[i]).item()

for i in range(len(test_dataset.classes)):
    accuracy = 100 * class_correct[i] / class_total[i] if class_total[i] > 0 else 0
    print(f"Accuracy for class {test_dataset.classes[i]}: {accuracy:.2f}%")

