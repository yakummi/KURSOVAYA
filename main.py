import requests
import json
from tqdm import tqdm

with open('mytokens.txt') as file:
    access_token = file.readline().strip()
    ya_token = file.readline().strip()
    user_id = file.readline().strip()

class VKPhoto:
    def __init__(self, token: str, user_id: str):
        self.token = token
        self.user_id = user_id
        self.params = {'v': '5.131', 'access_token': self.token}

    def get_info(self) -> dict:
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.user_id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1}
        response = requests.get(url, params={**params, **self.params})
        return response.json()

    def get_photo(self, quantity=5) -> dict:
        photos_info = {}
        values = {'s': 1, 'm': 2, 'x': 3, 'o': 4, 'p': 5, 'q': 6, 'r': 7, 'y': 8, 'z': 9, 'w': 10}
        for params in self.get_info()['response']['items']:
            if params['likes']['count'] not in photos_info:
                name = str(params['likes']['count']) + '.jpg'
                photos_info.setdefault(name, [])
            else:
                name = str(params['date']) + '.jpg'
                photos_info.setdefault(params['date'], [])
            for j in sorted(params['sizes'], key=lambda item: item['type']):
                if j['type'] == 'w':
                    photos_info[name] = [j['url'], 'w', values['w']]
                    break
                else:
                    photos_info[name] = [sorted(params['sizes'], key=lambda item: item['type'])[-1]['url'],
                                         sorted(params['sizes'], key=lambda item: item['type'])[-1]['type'],
                                         values[sorted(params['sizes'], key=lambda item: item['type'])[-1]['type']]]
        if quantity > len(photos_info):
            print(f'{quantity} is too much, maximum of photos quantity is {len(photos_info)}')
            exit()
        final_photos = sorted(photos_info.items(), key=lambda para: para[-1][-1])
        final_photos = dict(final_photos[-quantity:])

        return final_photos


class YaDisc:

    def __init__(self, token: str):
        self.token = token
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        self.headers = {
            'Authorization': f'OAuth {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def create_folder(self, folder_name: str) -> None:
        """Method create folder into your Yandex Disc with name wich user input, name input is mandatory"""
        params = {
            'path': f'/{folder_name}/'
        }
        requests.put(self.url, headers=self.headers, params=params)

    def upload_file(self, loading_files: dict, loading_folder: str) -> None:

        user_url = self.url + 'upload'
        headers = self.headers
        photos_list = []
        for key, value in tqdm(loading_files.items(), ascii=True, desc='Uploading photos: '):

            params = {
                'url': value[0],
                'path': f'{loading_folder}/{key}',
                'disable_redirects': 'true'
            }
            response = requests.post(user_url, params=params, headers=headers)
            photos_list.append({'file_name': key,
                                'size': value[1]})
            status = response.status_code
            if status < 400:
                tqdm.write(f'\nPhoto {key} was loaded with status {status}')
            else:
                tqdm.write(f'\nLoading failed with status code {status}')
        with open('data.json', 'a') as file:
            json.dump(photos_list, file, indent=0)

        tqdm.write('File loading complete')


if __name__ == '__main__':
    photos_quantity = int(input('Пожалуйста, введите количество фотографий: '))
    f_name = 'project'
    my_profile = VKPhoto(access_token, user_id)
    my_profile.get_info()
    my_profile.get_photo(photos_quantity)
    my_disc = YaDisc(ya_token)
    my_disc.create_folder(f_name)
    my_disc.upload_file(my_profile.get_photo(photos_quantity), f_name)