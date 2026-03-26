import os
import gdown

LANE_MODEL_ID    = '1nsoLxwYR0kr41SfO-xcjKLaIJsJ6R2x1'  # lane_model.onnx
POTHOLE_MODEL_ID = '17BtCQOlgec16jVqsD5lTfCCtvan9idiE'  # best.onnx

def download_models():
    os.makedirs('model', exist_ok=True)

    if not os.path.exists('model/lane_model.onnx'):
        print('⬇ Downloading lane model...')
        gdown.download(id=LANE_MODEL_ID, output='model/lane_model.onnx', quiet=False)
        print('✅ Lane model downloaded.')
    else:
        print('✅ Lane model already exists.')

    if not os.path.exists('model/best.onnx'):
        print('⬇ Downloading pothole model...')
        gdown.download(id=POTHOLE_MODEL_ID, output='model/best.onnx', quiet=False)
        print('✅ Pothole model downloaded.')
    else:
        print('✅ Pothole model already exists.')

if __name__ == '__main__':
    download_models()
