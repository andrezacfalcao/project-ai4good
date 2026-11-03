from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

# Exemplo do model card: mesma imagem IAM, disponibilizada localmente.
image = Image.open("a01-122-02-00.jpg").convert("RGB")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-printed")
pixel_values = processor(images=image, return_tensors="pt").pixel_values

generated_ids = model.generate(pixel_values)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(generated_text)
