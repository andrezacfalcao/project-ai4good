from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

# exemplo oficial do README de microsoft/trocr-small-printed (imagem a01-122-02-00.jpg do IAM)
image = Image.open("va2/tec/a01-122-02-00.jpg").convert("RGB")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-printed")
pixel_values = processor(images=image, return_tensors="pt").pixel_values

generated_ids = model.generate(pixel_values, max_new_tokens=20)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(generated_text)
