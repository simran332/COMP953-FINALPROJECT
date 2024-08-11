import requests
import ctypes

def main():
    # Functionality testing code will be added here
    pass

def download_image(image_url):
    print(f'Downloading image from {image_url}...', end='')
    response = requests.get(image_url)

    if response.status_code == requests.codes.ok:
        print('Download successful')
        return response.content
    else:
        print('Download failed')
        print(f'Response code: {response.status_code} ({response.reason})')

def save_image_file(image_data, image_path):
    try:
        print(f'Saving image file as {image_path}...', end='')
        with open(image_path, 'wb') as file:
            file.write(image_data)
        print('Save successful')
        return True
    except Exception as e:
        print('Save failed')
        print(f'Error: {e}')
        return False

def set_desktop_background_image(image_path):
    print(f'Setting desktop background to {image_path}...', end='')
    SPI_SETDESKWALLPAPER = 20
    try:
        if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3):
            print('Success')
            return True
        else:
            print('Failed')
    except Exception as e:
        print('Failed')
        print(f'Error: {e}')
    return False

def scale_image(image_size, max_size=(800, 600)):
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()
