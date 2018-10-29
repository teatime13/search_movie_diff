#seccon2018 media 改良版
import os
import shutil
import cv2
from PIL import Image
import imagehash
from queue import Queue
def main():
    video_2_frames()
#参考 http://testpy.hatenablog.com/entry/2017/07/13/003000
#video_file:対象のファイル名、image_dir:保存先、search_frame_rate:何フレームごとに計算するかを指定、comp_frame:何フーム前と比較するかの指定,hash_parameter:画像の差の値10以上でだいたい違う画像と見なされる
def video_2_frames(video_file='./target.mp4', image_dir='./image_dir/',search_frame_rate=1,comp_frame=5,hash_parameter=10,image_file='img_%s.png',diff_file='diff_%s.png'):
    # Delete the entire directory tree if it exists.
    if os.path.exists(image_dir):
        shutil.rmtree(image_dir)  
    # Make the directory if it doesn't exist.
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    # Video to frames
    cap = cv2.VideoCapture(video_file)
    q = Queue()
    q_b = Queue()
    first_flag = False
    i = 0

    while(cap.isOpened()):
        flag, frame = cap.read()  # Capture frame-by-frame
        if flag == False:  # Is a frame left?
            break

        if i % search_frame_rate != 0:
            i += 1
            continue

        cv2.imwrite(image_dir+image_file % str(i).zfill(8), frame)
        hash_new = imagehash.average_hash(Image.open(image_dir+image_file % str(i).zfill(8)))

        if first_flag == False:
            first_flag = True
            for x in range(5):
                q.put(hash_new)
        
        if i % 100 == 0:
            print("count: %d" % i)
        
        if i < search_frame_rate*comp_frame:
            q_b.put(1)
            i += 1
            continue
        elif check_hash(q.get(), hash_new, hash_parameter):
            print("diff  :  " + image_dir+image_file % str(i).zfill(8))
            q_b.get()
            q_b.put(1)
        else:
            if(q_b.get() == 0):
                os.remove(image_dir+image_file % str(i - comp_frame*search_frame_rate).zfill(8))
            q_b.put(0)

        q.put(hash_new)

        i += 1
#        if i >= 10000: #テスト用
#            break
    cap.release()  # When everything done, release the capture
#参考 https://github.com/JohannesBuchner/imagehash
def check_hash(hash_old, hash_new, hash_parameter):
    if(hash_new - hash_old > hash_parameter or hash_old - hash_new > hash_parameter):
        return True
    else:
        return False

if __name__ == '__main__':
    main()