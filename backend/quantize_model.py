from onnxruntime.quantization import quantize_dynamic, QuantType

quantize_dynamic(
    model_input="models/model.onnx",
    model_output="models/model-int8.onnx",
    weight_type=QuantType.QInt8,
)

print("Model quantized successfully!")