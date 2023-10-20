# THOSE ARE ACTUALLY USED IN THE EXPERIMENT

HOSTING_URL = 'https://greenlab-15fd0cfe63bd.herokuapp.com'
FILE_PATH = '/static'

text_content = [
    "Lorem ipsum dolor si",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris semper neque tortor, et pretium odio convallis at. Fusce ut posuere ante, vel dapibus nunc. Sed sagittis blandit tortor luctus suscipit.",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris semper neque tortor, et pretium odio convallis at. Fusce ut posuere ante, vel dapibus nunc. Sed sagittis blandit tortor luctus suscipit. Fusce blandit porttitor cursus. Suspendisse potenti. Duis malesuada fringilla felis a rhoncus. Integer cursus velit eu tempus cursus. Nulla commodo pulvinar dolor, at blandit elit rutrum id. Mauris feugiat nisl a massa pulvinar volutpat. Aenean ac consequat tortor. Phasellus mattis ante non semper pellentesque. Nulla aliquam imperdiet gravida. Nam dictum arcu eget ex molestie varius. Nam iaculis lorem vitae turpis venenatis, et tempus libero lobortis. Suspendisse risus sapien, tincidunt id massa quis, vulputate ultrices magna. Quisque lobortis mattis nunc eget sagittis. Maecenas varius ex at "
]

# files samples from gitHub

image_urls = [
    'https://github.com/macko99/file_examples/raw/main/image/JPG_100kB.jpg',
    'https://github.com/macko99/file_examples/raw/main/image/JPG_500kB.jpg',
    'https://github.com/macko99/file_examples/raw/main/image/JPG_1MB.jpg'
]

video_urls = [
    '{}/MP4_1MB.mp4'.format(HOSTING_URL + FILE_PATH),
    '{}/MP4_3MB.mp4'.format(HOSTING_URL + FILE_PATH),
    '{}/MP4_5MB.mp4'.format(HOSTING_URL + FILE_PATH)
]

audio_urls = [
    'https://github.com/macko99/file_examples/raw/main/audio/MP3_50kB.mp3',
    'https://github.com/macko99/file_examples/raw/main/audio/MP3_150kB.mp3',
    'https://github.com/macko99/file_examples/raw/main/audio/MP3_1MB.mp3'
]

file_urls = [
    '{}/PDF_150kB.pdf'.format(HOSTING_URL + FILE_PATH),
    '{}/PDF_1MB.pdf'.format(HOSTING_URL + FILE_PATH),
    '{}/PDF_5MB.pdf'.format(HOSTING_URL + FILE_PATH)
]

# ________NOT USED________ #

attachments_urls = [
    ('image', 'https://github.com/macko99/file_examples/raw/main/JPG_500kB.jpg'),
    ('file', 'https://github.com/macko99/file_examples/raw/main/PDF_1MB.pdf'),
    ('audio', 'https://github.com/macko99/file_examples/raw/main/MP3_1MB.mp3'),
    ('video', 'https://github.com/macko99/file_examples/raw/main/MP4_640_3MB.mp4')]

# facebook

attachments_ids_fb = [('image', '326292163188516'),
                      ('file', '260135086919130'),
                      ('audio', '1039643760813408'),
                      ('video', '975807530537961')]

# viber

attachments_urls_viber = [
    ('picture', 'https://github.com/macko99/file_examples/raw/main/JPG_500kB.jpg', None, None),
    ('file', 'https://github.com/macko99/file_examples/raw/main/PDF_1MB.pdf', 1000000, 'file.pdf'),
    ('file', 'https://github.com/macko99/file_examples/raw/main/MP3_1MB.mp3', 1000000, 'audio.mp3'),
    ('video', 'https://github.com/macko99/file_examples/raw/main/MP4_640_3MB.mp4', 3000000, None)]

# line

attachments_urls_line = [
    ('image', 'https://github.com/macko99/file_examples/raw/main/JPG_500kB.jpg',
     'https://github.com/macko99/file_examples/raw/main/JPG_500kB.jpg', None),
    ('audio', 'https://github.com/macko99/file_examples/raw/main/M4A_1MB.m4a', None, 58000),
    ('video', 'https://github.com/macko99/file_examples/raw/main/MP4_640_3MB.mp4',
     'https://github.com/macko99/file_examples/raw/main/JPG_500kB.jpg', None)]
