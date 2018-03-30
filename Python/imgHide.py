#coding=utf-8
import random
import sys
import threading
import cv2
import os
import time
import numpy as np
from PyQt4 import QtGui, QtCore
from Crypto.Util.py3compat import *
from Crypto.Cipher import _AES
from binascii import b2a_hex, a2b_hex
from operator import itemgetter
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_OPENPGP = 7

class ImageHideUi(QtGui.QMainWindow):
    def __init__(self):
        super(ImageHideUi, self).__init__()
        self.initUI()

    def initUI(self):
        self.fileName = ''
        self.__img_thread_status = ''
        self.success = 0  #图像处理进程退出标志
        self.setFixedSize(290,250)
        self.edit = QtGui.QLineEdit(self)      #密钥输入框
        self.edit.move(70, 100)
        self.edit.adjustSize()
        self.edit.setToolTip(u'输入一个1到16位的密钥')
        label_key = QtGui.QLabel(self)
        label_key.setText(u'密钥:')
        label_key.move(40,103)
        label_key.adjustSize()
        self.label_jindu = QtGui.QLabel(self)
        self.label_jindu.setText('0%')
        self.label_jindu.move(235,204)
        self.label_jindu.adjustSize()
        self.pbar = QtGui.QProgressBar(self)     #进度条
        self.pbar.setGeometry(57, 200, 200, 20)
        self.timer = QtCore.QBasicTimer()
        self.step = 0    #进度条进程
        self.connect(self.edit, QtCore.SIGNAL('textChanged(QString)'),self.onChanged) #检测密钥变化
        self.button1 = QtGui.QPushButton(u"载入图像", self)
        self.button1.move(30, 40)
        self.button2 = QtGui.QPushButton(u"载入文件", self)
        self.button2.move(150, 40)
        self.button1.setToolTip(u'载入一张图片')
        self.button2.setToolTip(u'载入一个将要隐写入图片里的文件')
        self.button3 = QtGui.QPushButton(u'提取',self)
        self.button3.setToolTip(u'从载入的图像中提取隐写的内容，图片格式只能为png')
        self.button3.move(30,150)
        self.button4 = QtGui.QPushButton(u'隐写',self)
        self.button4.setToolTip(u'将选择的文件隐写入选择的图像中')
        self.button4.move(150,150)
        button5 = QtGui.QPushButton(u'随机',self)
        button5.resize(40,20)
        button5.setToolTip(u'随机产生一个16位的密钥')
        button5.move(205,100)
        self.connect(button5,QtCore.SIGNAL('clicked()'),self._randomKey)
        self.button1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button4.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.connect(self.button3,QtCore.SIGNAL('clicked()'),self.imgGet)
        self.connect(self.button3,QtCore.SIGNAL('clicked()'),self.doAction)
        self.connect(self.button3,QtCore.SIGNAL('clicked()'),self._showDialog)
        self.connect(self.button4,QtCore.SIGNAL('clicked()'),self.imgHide)
        self.connect(self.button4,QtCore.SIGNAL('clicked()'),self.doAction)
        #self.button2.adjustSize()
        self.connect(self.button1,QtCore.SIGNAL('clicked()'),self.importImg)
        self.connect(self.button2,QtCore.SIGNAL('clicked()'),self.importHideFile)
        self.statusBar().showMessage(u'准备就绪')
        self.setWindowTitle(u'数字图像隐写')
        self.setWindowIcon(QtGui.QIcon('./ico60x60.png'))
        self.center()

    def timerEvent(self, *args, **kwargs):
        if self.send_button.text()==u'提取':
            try:
                if self.imgPath=='':
                    self.statusBar().showMessage(u'请先选择一张图片')
                    return
            except AttributeError:
                self.statusBar().showMessage(u'请先选择一张图片')
                return
            if self.imgType!='png':
                self.statusBar().showMessage(u'只有png格式的图片才能获取隐写信息')
                return
            try:
                if self.key=='':
                    self.statusBar().showMessage(u'没有输入密钥')
                    return
            except AttributeError:
                self.statusBar().showMessage(u'没有输入密钥')
                return
            if len(self.key)>16:
                self.statusBar().showMessage(u'密钥长度超过16位')
                return
        else:
            try:
                if self.imgPath=='':
                    self.statusBar().showMessage(u'请先选择一张图片')
                    return
            except AttributeError:
                self.statusBar().showMessage(u'请先选择一张图片')
                return
            try:
                if self.hidePath=='':
                    self.statusBar().showMessage(u'没有选择需要隐写的文件')
                    return
            except AttributeError:
                self.statusBar().showMessage(u'没有选择需要隐写的文件')
                return
            try:
                if self.key=='':
                    self.statusBar().showMessage(u'没有输入密钥')
                    return
            except AttributeError:
                self.statusBar().showMessage(u'没有输入密钥')
                return
            if len(self.key)>16:
                self.statusBar().showMessage(u'密钥长度超过16位')
                return
        if self.success == 0:
            if self.step<=95:
                self.step+=1
                self.pbar.setValue(self.step)
        else:
            self.pbar.setValue(100)    #self.success为1时图片处理线程已经退出
            self._setButtonEnable()   #设置按钮可用
            #print self.__img_thread_status
            if self.__img_thread_status=='1':   #图像处理无异常
                if self.send_button.text()== u'提取':
                    self.statusBar().showMessage(u'读取隐写信息成功')
                    self.timer.stop()
                else:
                    self.statusBar().showMessage(u'隐写成功，隐写结果为当前目录下的aesresult.png')
                    self.timer.stop()
            else:
                self.statusBar().showMessage(self.__img_thread_status)  #显示错误信息到状态栏
                self.timer.stop()

    def doAction(self):
        self.success = 0
        self.label_jindu.setText('')
        self.pbar.setValue(0)
        self.step = 0
        self.send_button = self.sender()
        if self.send_button.text()==u'提取' and self.fileName!='':
            try:
                if self.imgPath=='':
                    self.statusBar().showMessage(u'请先选择一张图片')
                    return -1
            except AttributeError:
                self.statusBar().showMessage(u'请先选择一张图片')
                return -1
            if self.imgType!='png':
                self.statusBar().showMessage(u'只有png格式的图片才能获取隐写信息')
                return -1
            try:
                if self.key=='':
                    self.statusBar().showMessage(u'没有输入密钥')
                    return -1
            except AttributeError:
                self.statusBar().showMessage(u'没有输入密钥')
                return -1
            if len(self.key)>16:
                self.statusBar().showMessage(u'密钥长度超过16位')
                return -1
            else:
                self.statusBar().showMessage(u'正在提取信息中...')
                self.timer.start(100,self)
        elif self.send_button.text()==u'隐写':
            try:
                if self.imgPath=='':
                    self.statusBar().showMessage(u'请先选择一张图片')
                    return -1
            except AttributeError:
                self.statusBar().showMessage(u'请先选择一张图片')
                return -1
            try:
                if self.hidePath=='':
                    self.statusBar().showMessage(u'没有选择需要隐写的文件')
                    return -1
            except AttributeError:
                self.statusBar().showMessage(u'没有选择需要隐写的文件')
                return -1
            try:
                if self.key=='':
                    self.statusBar().showMessage(u'没有输入密钥')
                    return -1
            except AttributeError:
                self.statusBar().showMessage(u'没有输入密钥')
                return -1
            if len(self.key)>16:
                self.statusBar().showMessage(u'密钥长度超过16位')
                return -1
            else:
                self.statusBar().showMessage(u'正在隐写信息中...')
                self.timer.start(100,self)

    def _setButtonDisable(self):
        self.button3.setEnabled(False)
        self.button4.setEnabled(False)

    def _setButtonEnable(self):
        self.button3.setEnabled(True)
        self.button4.setEnabled(True)

    def _statusGet(self):
        '''You should never access widgets and GUI related things directly
        from a thread other than the main thread'''
        while self.success==0:
            self.statusBar().showMessage(u'正在提取信息中.')
            time.sleep(0.5)
            if self.success==1:
                break
            self.statusBar().showMessage(u'正在提取信息中..')
            time.sleep(0.5)
            if self.success==1:
                break
            self.statusBar().showMessage(u'正在提取信息中...')
            time.sleep(0.5)
            if self.success==1:
                break
        self.statusBar().showMessage(u'读取隐写信息成功')
        self._setButtonEnable()

    def _statusHide(self):
        '''You should never access widgets and GUI related things directly
        from a thread other than the main thread'''
        while self.success==0:
            self.statusBar().showMessage(u'正在隐写信息中.')
            time.sleep(0.5)
            if self.success==1:
                break
            self.statusBar().showMessage(u'正在隐写信息中..')
            time.sleep(0.5)
            if self.success==1:
                break
            self.statusBar().showMessage(u'正在隐写信息中...')
            time.sleep(0.5)
            if self.success==1:
                break
        self.statusBar().showMessage(u'隐写成功，隐写结果为当前目录下的aesresult.png')
        self._setButtonEnable()

    def imgGet(self):
        try:
            if self.imgPath=='':
                self.statusBar().showMessage(u'请先选择一张图片')
                return -1
        except AttributeError:
            self.statusBar().showMessage(u'请先选择一张图片')
            return -1
        if self.imgType!='png':
            self.statusBar().showMessage(u'只有png格式的图片才能获取隐写信息')
            return -1
        try:
            if self.key=='':
                self.statusBar().showMessage(u'没有输入密钥')
                return -1
        except AttributeError:
            self.statusBar().showMessage(u'没有输入密钥')
            return -1
        if len(self.key)>16:
            self.statusBar().showMessage(u'密钥长度超过16位')
            return -1
        else:
            self.success = 0     #necessary
            #thread_get = threading.Thread(target=self._get)
            #thread_statusBar = threading.Thread(target=self._statusGet)
            #self._setButtonDisable()   #按键后设置按钮不可点击状态
            #QtGui.QApplication.processEvents()
            #thread_get.start()
            #thread_statusBar.start()

    def _get(self):
        try:
            self.__img_thread_status = PngImage(self.imgPath).get(self.fileName,self.key)
        except:
            self.__img_thread_status = '-1'
        finally:
            self.success = 1
            self.fileName = ''
        #else:
        #    self.statusBar().showMessage(u'读取隐写信息成功')

    def imgHide(self):
        try:
            if self.imgPath=='':
                self.statusBar().showMessage(u'请先选择一张图片')
                return -1
        except AttributeError:
            self.statusBar().showMessage(u'请先选择一张图片')
            return -1
        try:
            if self.hidePath=='':
                self.statusBar().showMessage(u'没有选择需要隐写的文件')
                return -1
        except AttributeError:
            self.statusBar().showMessage(u'没有选择需要隐写的文件')
            return -1
        try:
            if self.key=='':
                self.statusBar().showMessage(u'没有输入密钥')
                return -1
        except AttributeError:
            self.statusBar().showMessage(u'没有输入密钥')
            return -1
        if len(self.key)>16:
            self.statusBar().showMessage(u'密钥长度超过16位')
            return -1
        else:
            self.success = 0
            thread_hide = threading.Thread(target=self._hide)
            #thread_statusBar = threading.Thread(target=self._statusHide)
            self._setButtonDisable()
            QtGui.QApplication.processEvents()
            thread_hide.start()
            #thread_statusBar.start()

    def _hide(self):
        try:
            self.__img_thread_status = AesPngImage(self.imgPath,self.key).aesHide(self.hidePath,'aesresult.png')
        except:
            self.__img_thread_status = '-2'
        finally:
            self.success = 1
        #else:
        #    self.statusBar().showMessage(u'隐写成功，隐写结果为当前目录下的aesresult.png')

    def onChanged(self, text):
        try:
            self.key = str(text)    #密钥
            self.statusBar().showMessage(u'准备就绪')
        except UnicodeEncodeError:
            self.statusBar().showMessage(u'密钥不能包含中文字符')

    def importImg(self):
        self.statusBar().showMessage('')
        changeFlag = 1
        try:
            temp = self.imgPath
        except AttributeError:
            pass
        self.imgPath = QtGui.QFileDialog.getOpenFileName(self,u'图片选择','.',
                                 'Image File(*.jpg *.png *.gif *.jpeg *.bmp *.tif *.tiff *.jp2)')
        if self.imgPath == '':
            try:
                self.imgPath = temp
                changeFlag = 0
            except:
                pass
        if self.imgPath!='' and changeFlag == 1:
            self.button1.setToolTip(self.imgPath)
            cv2.destroyAllWindows()
            self.imgPath = unicode(self.imgPath).encode('gbk')
            self.imgType = what(self.imgPath)
            cv2img = cv2.imread(self.imgPath)
            self.imgName = self.imgPath.split('/')[-1]
            try:
                length = cv2img.shape[1]
                weight = cv2img.shape[0]
                cv2.namedWindow(self.imgName,0)
            except AttributeError:
                self.statusBar().showMessage(u'这个文件并不是图像文件')
                self.imgPath = ''
                return
            while weight>768 or length>1000:
                weight = weight/2
                length = length/2
            cv2.resizeWindow(self.imgName,length,weight)
            cv2.imshow(self.imgName,cv2img)
            self.button1.setText(self.imgName.decode('gbk'))

    def importHideFile(self):
        changeFlag = 1
        try:
            temp = self.hidePath
        except AttributeError:
            pass
        self.hidePath = QtGui.QFileDialog.getOpenFileName(self,u'隐写文件选择','.')
        if self.hidePath== '':
            try:
                changeFlag = 0
                self.hidePath = temp
            except:
                pass
        if self.hidePath!= '' and changeFlag== 1:
            self.button2.setToolTip(self.hidePath)
            self.hidePath = unicode(self.hidePath).encode('gbk')
            self.hideName = self.hidePath.split('/')[-1]
            self.button2.setText(self.hideName.decode('gbk'))

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            u"确定退出程序吗?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def _randomKey(self):
        chars = '''0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&*@_'''
        key = ''.join(random.sample(chars, 16))
        self.edit.setText(key)

    def _showDialog(self):    #提取隐写信息文件重命名
        try:
            if self.imgPath=='':
                self.statusBar().showMessage(u'请先选择一张图片')
                return -1
        except AttributeError:
            self.statusBar().showMessage(u'请先选择一张图片')
            return -1
        if self.imgType!='png':
            self.statusBar().showMessage(u'只有png格式的图片才能获取隐写信息')
            return -1
        try:
            if self.key=='':
                self.statusBar().showMessage(u'没有输入密钥')
                return -1
        except AttributeError:
            self.statusBar().showMessage(u'没有输入密钥')
            return -1
        if len(self.key)>16:
            self.statusBar().showMessage(u'密钥长度超过16位')
            return -1
        else:
            self.success = 0   #线程退出标志
            text, ok = QtGui.QInputDialog.getText(self, u'文件重命名',u'请输入文件名:')
            if ok:
                self.fileName = unicode(text).encode('gbk')
                thread_get = threading.Thread(target=self._get)
                self._setButtonDisable()   #按键后设置按钮不可点击状态
                QtGui.QApplication.processEvents()
                self.doAction()
                thread_get.start()
            else:
                self._setButtonEnable()
                return

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

class BlockAlgo():
    def __init__(self, factory, key, *args, **kwargs):
        self.mode = self._getParameter('mode', 0, args, kwargs, default=MODE_ECB)
        self.block_size = factory.block_size
        if self.mode != MODE_OPENPGP:
            self._cipher = factory.new(key, *args, **kwargs)
            self.IV = self._cipher.IV
        else:
            self._done_first_block = False
            self._done_last_block = False
            self.IV = self._getParameter('iv', 1, args, kwargs)
            if not self.IV:
                raise ValueError("MODE_OPENPGP requires an IV")
            IV_cipher = factory.new(key, MODE_CFB,
                    b('\x00')*self.block_size,      # IV for CFB
                    segment_size=self.block_size*8)
            if len(self.IV) == self.block_size:
                # ... encryption
                self._encrypted_IV = IV_cipher.encrypt(
                    self.IV + self.IV[-2:] +        # Plaintext
                    b('\x00')*(self.block_size-2)   # Padding
                    )[:self.block_size+2]
            elif len(self.IV) == self.block_size+2:
                # ... decryption
                self._encrypted_IV = self.IV
                self.IV = IV_cipher.decrypt(self.IV +   # Ciphertext
                    b('\x00')*(self.block_size-2)       # Padding
                    )[:self.block_size+2]
                if self.IV[-2:] != self.IV[-4:-2]:
                    raise ValueError("Failed integrity check for OPENPGP IV")
                self.IV = self.IV[:-2]
            else:
                raise ValueError("Length of IV must be %d or %d bytes for MODE_OPENPGP"
                    % (self.block_size, self.block_size+2))
            self._cipher = factory.new(key, MODE_CFB,
                self._encrypted_IV[-self.block_size:],
                segment_size=self.block_size*8)

    def _getParameter(self, name, index, args, kwargs, default=None):
        param = kwargs.get(name)
        if len(args)>index:
            if param:
                raise ValueError("Parameter '%s' is specified twice" % name)
            param = args[index]
        return param or default

    def encrypt(self, plaintext):
        if self.mode == MODE_OPENPGP:
            padding_length = (self.block_size - len(plaintext) % self.block_size) % self.block_size
            if padding_length>0:
                # CFB mode requires ciphertext to have length multiple of block size,
                # but PGP mode allows the last block to be shorter
                if self._done_last_block:
                    raise ValueError("Only the last chunk is allowed to have length not multiple of %d bytes",
                        self.block_size)
                self._done_last_block = True
                padded = plaintext + b('\x00')*padding_length
                res = self._cipher.encrypt(padded)[:len(plaintext)]
            else:
                res = self._cipher.encrypt(plaintext)
            if not self._done_first_block:
                res = self._encrypted_IV + res
                self._done_first_block = True
            return res
        return self._cipher.encrypt(plaintext)

    def decrypt(self, ciphertext):
        if self.mode == MODE_OPENPGP:
            padding_length = (self.block_size - len(ciphertext) % self.block_size) % self.block_size
            if padding_length>0:
                # CFB mode requires ciphertext to have length multiple of block size,
                # but PGP mode allows the last block to be shorter
                if self._done_last_block:
                    raise ValueError("Only the last chunk is allowed to have length not multiple of %d bytes",
                        self.block_size)
                self._done_last_block = True
                padded = ciphertext + b('\x00')*padding_length
                res = self._cipher.decrypt(padded)[:len(ciphertext)]
            else:
                res = self._cipher.decrypt(ciphertext)
            return res
        return self._cipher.decrypt(ciphertext)

class AESCipher (BlockAlgo):
    def __init__(self, key, *args, **kwargs):
        BlockAlgo.__init__(self, _AES, key, *args, **kwargs)

class Aes():
    __KEY = 'd6tU$7^Nh$aS4vpZ'
    def __init__(self, key):
        self.key = key + self.__KEY[0:(16-len(key))]
        self.mode = MODE_CBC

    def encrypt(self, text): #加密
        cryptor = self.new(self.key, self.mode, self.key)
        length = 16
        count = len(text)
        if count < length:
            add = (length-count)
            text = text + ('\\' * add)
        elif count > length:
            add = (length-(count % length))
            text = text + ('\\' * add)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)

    def decrypt(self, text): #解密
        cryptor = self.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        #return plain_text
        return plain_text.rstrip('\\')

    def new(self, key, *args, **kwargs):
        return AESCipher(key, *args, **kwargs)

'''根据头部判别图像格式'''
def what(file, h=None):
    f = None
    try:
        if h is None:
            if isinstance(file, basestring):
                f = open(file, 'rb')
                h = f.read(32)
            else:
                location = file.tell()
                h = file.read(32)
                file.seek(location)
        for tf in tests:
            res = tf(h, f)
            if res:
                return res
    finally:
        if f: f.close()
    return None
tests = []
def test_jpeg(h, f):
    """JPEG data in JFIF format"""
    if h[6:10] == 'JFIF':
        return 'jpeg'

tests.append(test_jpeg)

def test_exif(h, f):
    """JPEG data in Exif format"""
    if h[6:10] == 'Exif':
        return 'jpeg'

tests.append(test_exif)

def test_png(h, f):
    if h[:8] == "\211PNG\r\n\032\n":
        return 'png'

tests.append(test_png)

def test_gif(h, f):
    """GIF ('87 and '89 variants)"""
    if h[:6] in ('GIF87a', 'GIF89a'):
        return 'gif'

tests.append(test_gif)

def test_tiff(h, f):
    """TIFF (can be in Motorola or Intel byte order)"""
    if h[:2] in ('MM', 'II'):
        return 'tiff'

tests.append(test_tiff)

def test_rgb(h, f):
    """SGI image library"""
    if h[:2] == '\001\332':
        return 'rgb'

tests.append(test_rgb)

def test_pbm(h, f):
    """PBM (portable bitmap)"""
    if len(h) >= 3 and \
        h[0] == 'P' and h[1] in '14' and h[2] in ' \t\n\r':
        return 'pbm'

tests.append(test_pbm)

def test_pgm(h, f):
    """PGM (portable graymap)"""
    if len(h) >= 3 and \
        h[0] == 'P' and h[1] in '25' and h[2] in ' \t\n\r':
        return 'pgm'

tests.append(test_pgm)

def test_ppm(h, f):
    """PPM (portable pixmap)"""
    if len(h) >= 3 and \
        h[0] == 'P' and h[1] in '36' and h[2] in ' \t\n\r':
        return 'ppm'

tests.append(test_ppm)

def test_rast(h, f):
    """Sun raster file"""
    if h[:4] == '\x59\xA6\x6A\x95':
        return 'rast'

tests.append(test_rast)

def test_xbm(h, f):
    """X bitmap (X10 or X11)"""
    s = '#define '
    if h[:len(s)] == s:
        return 'xbm'

tests.append(test_xbm)

def test_bmp(h, f):
    if h[:2] == 'BM':
        return 'bmp'

tests.append(test_bmp)

def test():
    import sys
    recursive = 0
    if sys.argv[1:] and sys.argv[1] == '-r':
        del sys.argv[1:2]
        recursive = 1
    try:
        if sys.argv[1:]:
            testall(sys.argv[1:], recursive, 1)
        else:
            testall(['.'], recursive, 1)
    except KeyboardInterrupt:
        sys.stderr.write('\n[Interrupted]\n')
        sys.exit(1)

def testall(list, recursive, toplevel):
    import sys
    import os
    for filename in list:
        if os.path.isdir(filename):
            print filename + '/:',
            if recursive or toplevel:
                print 'recursing down:'
                import glob
                names = glob.glob(os.path.join(filename, '*'))
                testall(names, recursive, 0)
            else:
                print '*** directory (use -r) ***'
        else:
            print filename + ':',
            sys.stdout.flush()
            try:
                print what(filename)
            except IOError:
                print '*** not found ***'

class NormalImage():
    __COMPERSSION_RATIO = 3
    def __init__(self,imgPath):
        self.img = cv2.imread(imgPath)
        try:
            self.imgType = what(imgPath)
            self.length = self.img.shape[1]
            self.height = self.img.shape[0]
        except:
            return 'Img Read Error'

    def __del__(self):
        del self.img

    def saveAsPng(self,tempPngName='temp.png'):
        try:
            cv2.imwrite(tempPngName,self.img,[int(cv2.IMWRITE_PNG_COMPRESSION),
                                      self.__COMPERSSION_RATIO])
        except:
            print 'Save Png Error'
            return -1
        return 0

    def printLh(self):
        print 'Image length is %s,height is %s.' % (str(self.length),str(self.height))

    def changeRatio(self,newRatio):
        self.__COMPERSSION_RATIO = newRatio
        self.saveAsPng()

    @classmethod
    def getRatio(cls):
        return cls.__COMPERSSION_RATIO

class PngImage(NormalImage):
    pngName = 'temp.png'
    aesFlag = '0'       #加密标志位
    infoLenFlag = '0'      #信息长度标志位
    def __init__(self,imgPath):
        '''打开任意一张图片，自动保存为名为pngName的png图片'''
        NormalImage.__init__(self,imgPath)
        NormalImage(imgPath).saveAsPng(self.pngName)
        self.img = cv2.imread(self.pngName)
        #os.remove(self.pngName)
        self.priorityDict = GrayImage(self.pngName).getPriority()
        self.__head = self.__getHead()
        os.remove(self.pngName)

    def __del__(self):
        del self.img
        del self.priorityDict

    def __encode(self,content):
        tempName = 'temp.dat'
        #File(content).file2Binary('yyyyyyyy.dat')
        File(content).file2Binary(tempName)
        infoFile = open(tempName,'r')
        info = infoFile.read()
        infoFile.close()
        include_head_file = open(tempName,'w')
        need_point_num = len(info)/4
        head = '0000'
        length = 20
        if need_point_num>(10**6):
            head = '0100'
            length = 28
        need_point_num_bin = BinDec.dec2Bin(dec=need_point_num,length=length)
        include_head_file.write(head+need_point_num_bin+info) #头+所需像素点数+信息
        del info
        include_head_file.close()
        list = BinaryFile(tempName).file2List()
        os.remove(tempName)
        return list

    def hideInImage(self,list,resultImg):
        imgDst = self.img.copy()
        pointNum = int(len(list)/2)
        #print pointNum
        if pointNum > self.height*self.length:
            return u'这张图像的像素数量不足以隐写这个文件'
        for i in range(0,pointNum):
            q,p = self.priorityDict[i][0].split()
            blue = BinDec.binStr2Dec(str(list[2*i]))
            #green = BinDec.binStr2Dec(str(list[3*i+1]))
            red = BinDec.binStr2Dec(str(list[2*i+1]))
            imgDst[q,p,0] -= (BinDec.binStr2Dec(BinDec.dec2BinLastTwo(imgDst[q,p,0]))-blue)
            #imgDst[q,p,1] -= (BinDec.binStr2Dec(BinDec.dec2BinLastTwo(imgDst[q,p,1]))-green)
            imgDst[q,p,2] -= (BinDec.binStr2Dec(BinDec.dec2BinLastTwo(imgDst[q,p,2]))-red)

        cv2.imwrite(resultImg,imgDst,[int(cv2.IMWRITE_PNG_COMPRESSION),
                                      NormalImage.getRatio()])
        #del imgDst
        return '1'

    def get(self,result='dst',*key):
        if self.imgType!='png':  #只有png格式的图像才能获取隐写内容
            print "this img type is "+self.imgType+",can't get inform"
            return -1
        if self.__head[2:]!='00':   #头部保留位暂时为00
            return u'这张图像没有隐写任何信息'
            #return -1
        pointNum = 0
        start = 6   #从第七个像素点开始才是信息
        if self.__head[0]=='1':
            self.aesFlag = '1'
            if len(key)==0:
                return u'需要一个密钥'
                #return '-1'
            elif len(key)>1:
                return u'提供了多余的参数'
                #return '-1'
        if self.__head[1]=='0':
            '''使用5个像素20bits来存储隐写像素的数量'''
            pointNum_bin = self.__get_start_stop_point(1,5)
            pointNum = BinDec.binStr2Dec(pointNum_bin)
        elif self.__head[1]=='1':
            '''使用7个像素28bits来存储隐写像素的数量'''
            pointNum_bin = self.__get_start_stop_point(1,7)
            pointNum = BinDec.binStr2Dec(pointNum_bin)
            start = 8
        #print pointNum
        if pointNum > (self.height*self.length):
            return u'这张图像没有隐写任何信息'
            #return '-1'
        #print self.__head
        tempName = 'temp.dat'
        binaryFile = open(tempName,'w')
        binaryStr = ''
        for i in range(start,pointNum+start):
            p,q = self.priorityDict[i][0].split()
            binaryStr += (BinDec.dec2BinLastTwo(self.img[p,q,0])+
                          BinDec.dec2BinLastTwo(self.img[p,q,2]))
        binaryFile.write(binaryStr)
        binaryFile.close()
        del binaryStr
        if self.aesFlag=='0':
            BinaryFile(tempName).cvt2File(result)
        elif self.aesFlag=='1':
            KEY = key[0]
            AesHexTemp = 'AesHex.dat'
            BinaryFile(tempName).bin2Hex(hexFilePath=AesHexTemp)
            File(AesHexTemp).decodeFile(key=KEY,dPath=result)
            os.remove(AesHexTemp)
        os.remove(tempName)
        return '1'

    def hide(self,content='content.txt',resultImg='result.png'):
        return self.hideInImage(self.__encode(content),resultImg)

    def __getHead(self):
        p,q = self.priorityDict[0][0].split()
        head = BinDec.dec2BinLastTwo(self.img[p,q,0]) + BinDec.dec2BinLastTwo(self.img[p,q,2])
        return head

    def __get_start_stop_point(self,start,stop):
        str = ''
        for i in range(start,stop+1):
            p,q = self.priorityDict[i][0].split()
            str += (BinDec.dec2BinLastTwo(self.img[p,q,0])+
                          BinDec.dec2BinLastTwo(self.img[p,q,2]))
        return str

class AesPngImage(PngImage):
    def __init__(self,imgPath,key):
        PngImage.__init__(self,imgPath)
        self.aesFlag = '1'
        self.key = key

    def __del__(self):
        del self.img
        del self.priorityDict

    def __aesEncode(self,content='content.txt'):
        aesCodePath = 'encode.dat'  #加密后的十六进制字符串文件
        infoHexPath = 'all.dat'   #包含头信息的十六进制字符串文件
        infoHexFile = open(infoHexPath,'w')
        File(content).encodeFile(key=self.key,ePath=aesCodePath)
        aesFile = open(aesCodePath,'r')
        str = aesFile.read()
        need_point = len(str)  #加密内容所需像素点数
        length = 20
        if need_point>(10**6):    #00保留位
            self.head = self.aesFlag+'1'+'00'
            length = 28
        else:
            self.head = self.aesFlag+'0'+'00'
        #print self.head
        need_point_bin = BinDec.dec2Bin(dec=need_point,length=length)
        need_point_hex = ''
        for i in range(0,len(need_point_bin),4):
            need_point_hex += BinaryFile.getHex(need_point_bin[i:i+4])
        str = BinaryFile.getHex(self.head) + need_point_hex + str  #头1位16进制+所需像素点数+信息
        #print BinaryFile.getHex(self.head) + need_point_hex
        infoHexFile.write(str)
        infoHexFile.close()
        del str
        aesFile.close()
        infoBinPath = 'allbin.dat'
        HexFile(infoHexPath).hex2Bin(binPath=infoBinPath)
        list = BinaryFile(infoBinPath).file2List()
        os.remove(infoBinPath)
        os.remove(aesCodePath)
        os.remove(infoHexPath)
        return list

    def aesHide(self,content='content.txt',resultImg='aesresult.png'):
        return self.hideInImage(self.__aesEncode(content),resultImg)

class GrayImage(NormalImage):
    __priorityDict = {}
    def __init__(self,imgPath):
        NormalImage.__init__(self,imgPath)
        self.__grayImg = np.zeros((self.height,self.length),np.uint8)
        self.cvt2GrayByGreen()

    def __del__(self):
        del self.img
        del self.__priorityDict
        del self.__grayImg

    def cvt2GrayByGreen(self):
        '''取RGB图像中的G值作为灰度值'''
        for i in range(0,self.img.shape[0]):
            for m in range(0,self.img.shape[1]):
                self.__grayImg[i,m]=self.img[i,m,1]

    def cvt2GrayByCv2(self):
        '''由opencv2自带的函数进行灰度图转换'''
        self.__grayImg = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)

    def showGrayImage(self):
        cv2.imshow('img',self.__grayImg)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def getPriority(self):
        dict = {}
        x = cv2.Sobel(self.__grayImg,-1,1,0,ksize=1)
        y = cv2.Sobel(self.__grayImg,-1,0,1,ksize=1)
        absX = cv2.convertScaleAbs(x)
        absY = cv2.convertScaleAbs(y)
        sobelResult = cv2.addWeighted(absX,0.5,absY,0.5,0)
        #cv2.imshow('sobel',sobelResult)
        #cv2.waitKey()
        del x,y,absX,absY
        for m in range(0,self.height):
            for n in range(0,self.length):
                dict[str(m)+' '+str(n)] = sobelResult[m,n]
        self.__priorityDict = sorted(dict.iteritems(),key=itemgetter(1),reverse=True)
        return self.__priorityDict

    def __cmp__(self, other):
        try:
            if self.__grayImg.shape[0]!=other.__grayImg.shape[0] or \
                            self.__grayImg.shape[1]!=other.__grayImg.shape[1]:
                print "Two picture size aren't equal"
                return -1
        except AttributeError:
            print 'AttributeError'
            return -1
        differenceDict = {}
        for m in range(0,self.__grayImg.shape[0]):
            for n in range(0,self.__grayImg.shape[1]):
                difference = int(self.__grayImg[m,n])-int(self.__grayImg[m,n])
                if difference==0:
                    continue
                else:
                    differenceDict[str(m)+' '+str(n)] = difference
        return differenceDict

class File():
    def __init__(self,filePath):
        self.path = filePath

    def file2Hex(self,HexDstPath='hex.dat'):
        '''将一个文件转换成十六进制字符串'''
        srcFile = open(self.path,'rb')
        dstFile = open(HexDstPath,'w')
        src = srcFile.read()
        for i in src:
            temp = hex(ord(i))[2:]
            temp = '0' * (2-len(temp)) + temp
            dstFile.write(temp)
        del src
        dstFile.close()
        srcFile.close()

    def file2Binary(self,binaryDstPath='binary.dat'):
        '''将一个文件转换成二进制字符串'''
        srcFile = open(self.path,'rb')
        dstFile = open(binaryDstPath,'w')
        src = srcFile.read()
        for i in src:
            temp = bin(ord(i))[2:]
            temp = '0' * (8-len(temp)) + temp
            dstFile.write(temp)
        del src
        dstFile.close()
        srcFile.close()

    def encodeFile(self,key,ePath='encode.dat'):
        '''加密文件'''
        _aes = Aes(key)
        oldFile = open(self.path,'rb')
        newFile = open(ePath,'w')
        src = oldFile.read()
        newFile.write(_aes.encrypt(src))
        del src
        oldFile.close()
        newFile.close()

    def decodeFile(self,key,dPath='decode.dat'):
        '''解密文件'''
        _aes = Aes(key)
        oldFile = open(self.path,'r')
        newFile = open(dPath,'wb')
        src = oldFile.read()
        newFile.write(_aes.decrypt(src))
        del src
        oldFile.close()
        newFile.close()

class BinaryFile(File):
    __binHexDict = {'0000':'0','0001':'1','0010':'2','0011':'3','0100':'4','0101':'5',
                      '0110':'6','0111':'7','1000':'8','1001':'9','1010':'a','1011':'b',
                      '1100':'c','1101':'d','1110':'e','1111':'f'}
    def cvt2File(self,fileDstPath='result.dat'):
        '''将二进制字符串转换为文件'''
        srcFile = open(self.path,'r')
        dstFile = open(fileDstPath,'wb')
        str = srcFile.read()
        for i in range(0,len(str),8):
            dstFile.write(chr(int(str[i:i+8],2)))
        del str
        srcFile.close()
        dstFile.close()

    def file2List(self):
        '''二进制字符串文件每两位保存成列表'''
        file = open(self.path,'r')
        str = file.read()
        list = []
        for i in range(0,len(str),2):
            list.append(str[i:i+2])
        del str
        return list

    def bin2Hex(self,hexFilePath='AesHex.dat'):
        '''二进制字符串转为十六进制字符串'''
        binFile = open(self.path,'r')
        hexFile = open(hexFilePath,'w')
        str = binFile.read()
        for i in range(0,len(str),4):
            hexFile.write(self.__binHexDict[str[i:i+4]])
        del str
        binFile.close()
        hexFile.close()

    @classmethod
    def getHex(cls,binary):
        return cls.__binHexDict[binary]

class HexFile(File):
    __hexBinDict = {'0':'0000','1':'0001','2':'0010','3':'0011','4':'0100','5':'0101','6':'0110',
                  '7':'0111','8':'1000','9':'1001','a':'1010','b':'1011','c':'1100',
                  'd':'1101','e':'1110','f':'1111'}
    def hex2Bin(self,binPath='bin.dat'):
        '''十六进制字符串文本转换成二进制字符串文本'''
        hexFile = open(self.path,'r')
        binFile = open(binPath,'w')
        str = hexFile.read()
        for i in str:
            binFile.write(self.__hexBinDict[i])
        del str
        binFile.close()
        hexFile.close()

class BinDec():
    @staticmethod
    def dec2Bin(dec,length):
        '''十进制转换为二进制字符串'''
        binary = bin(dec)[2:]
        result = str(0)*(length-len(binary)) + str(binary)
        return result

    @staticmethod
    def dec2BinLastTwo(dec):
        '''十进制转为二进制取低两位(像素最大值255)'''
        binary = bin(dec)[2:]    #0b开头
        result = str(0)*(8-len(binary)) + str(binary)
        return result[6:]

    @staticmethod
    def binStr2Dec(str):
        '''二进制字符串转为十进制'''
        dec = 0
        for i in range(0,len(str)):
            dec = dec + 2**(len(str)-i-1)*int(str[i])
        return dec

def uiMain():
    app = QtGui.QApplication(sys.argv)
    ex = ImageHideUi()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    #print printable
    uiMain()
    #aes = Aes('fdjrw')
    #File('2.ico').file2Hex('2.ico.hex')
    #file1 = open('2.ico.hex','r')
    #src = file1.read()
    #file2 = open('2.ico.hex.jm','r')
    ##file3.write(aes.decrypt(file2.read()))
    #file3.close()
    #file2.close()
    #File('allzero').encodeFile('qwer')
    #File('encode.dat').decodeFile('qwer','allzerohuifu')
    #File('3.ico').file2Hex('3.ico.hex')
    #AesPngImage('1.png','fdjrw').aesHide('test.py'.decode('utf-8').encode('gbk'))
    #print '测试.jpg'.decode('utf-8').encode('gbk')
    #imgt = cv2.imread('测试.jpg'.decode('utf-8').encode('gbk'))
    #cv2.imshow('123',imgt)
    #cv2.waitKey()
    #File('allzero').encodeFile('fdjrw')
    #File('encode.dat').decodeFile('fdjrw','allhuifu')
    #BinaryFile('binzero.dat').cvt2File('allzero')
    #File('13.doc').file2Hex('13hex.dat')
    #AesPngImage('1.jpg','daslfjew').aesHide('12.doc')
    #PngImage('aesresult.png').get('15.doc','daslfjew')
    #print BinaryFile.getHex('1001')
    #print BinDec.dec2Bin(300,16)
    #PngImage('aesresult.png').get('dst','fdjrw')
    #PngImage('aesresult.png').get('123.py'.decode('utf-8').encode('gbk'),'fdjrw')
    #PngImage('2.png').get('dsajlekwql.gif')
    #PngImage('1.png').get(192)