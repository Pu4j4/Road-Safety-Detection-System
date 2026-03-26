import os
import gdown

LANE_MODEL_ID    = '128sv4hQNhqZoqqHbLS60xHpxqQxKqz-s'
POTHOLE_MODEL_ID = '1EjE3HGr9AttSLCXnKnZnR74y35FmGlgg'

def download_models():
    os.makedirs('model', exist_ok=True)

    if not os.path.exists('model/full_CNN_model.h5'):
        print('⬇ Downloading lane model from Google Drive...')
        gdown.download(
            id=LANE_MODEL_ID,
            output='model/full_CNN_model.h5',
            quiet=False
        )
        print('✅ Lane model downloaded.')
    else:
        print('✅ Lane model already exists.')

    if not os.path.exists('model/best.pt'):
        print('⬇ Downloading pothole model from Google Drive...')
        gdown.download(
            id=POTHOLE_MODEL_ID,
            output='model/best.pt',
            quiet=False
        )
        print('✅ Pothole model downloaded.')
    else:
        print('✅ Pothole model already exists.')

if __name__ == '__main__':
    download_models()
