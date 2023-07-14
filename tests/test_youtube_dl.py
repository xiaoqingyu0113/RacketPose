from pytube import YouTube


def progress_function(self, chunk, bytes_remaining):
    size = self.filesize
    p = 1.0 - float(bytes_remaining)/float(size)
    print(f'{p*100.0:.1f}%')



yt_url = 'https://www.youtube.com/watch?v=q7y4av-Dr4I'
yt = YouTube(yt_url,on_progress_callback=progress_function)
yt.streams\
    .filter(progressive=True, file_extension='mp4')\
    .order_by('resolution')\
    .desc()\
    .first()\
    .download(output_path='original_videos',filename='mkd.mp4')


