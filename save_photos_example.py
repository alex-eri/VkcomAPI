# -*- coding:utf-8 -*-
import urllib,os

__author__ = 'eri'

home = os.path.expanduser("~")

if __name__ == '__main__':

    import vkcom
    a=vkcom.API(2256550,4)
    a.Auth.webkitgtk()

    info = a('users.get',uids=a.user_id)

    user_name = '%(first_name)s %(last_name)s' % info[0]

    albums=a('photos.getAlbums')
    albums.extend([
        {'aid':'profile', 'title': 'Фотографии из профиля'},
        {'aid':'wall', 'title': 'Фотографии с моей страницы' },
        {'aid':'saved', 'title': 'Сохраненные фотографии'}])
    for album in albums:
        for pic in a('photos.get',uid=a.user_id,aid=album['aid'],photo_sizes=1):
            src  = filter(lambda x: x['type'] == 'x' , pic['sizes'])[0]
            path = '/Изображения/Из Вконтакте %s/%s/' % (user_name, album['title'])
            if not os.path.exists(home+path):
                os.makedirs(home+path)
            filename = '%s.%s' %( pic['pid'], src['src'].split('.')[-1])
            if not os.path.exists(home+path+filename):
                urllib.urlretrieve(src['src'],home+path+filename)

