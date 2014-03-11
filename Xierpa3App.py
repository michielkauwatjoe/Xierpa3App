# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#     Xierpa 3 Application
#     (c) 2014  buro@petr.com, www.petr.com, www.xierpa.com
#
#     X I E R P A  3
#     No distribution without permission.
#
# -----------------------------------------------------------------------------
#
# sudo python setup.py py2app
#

from AppKit import NSObject, NSColor, NSView, NSFilenamesPboardType, NSDragOperationNone, NSDragOperationCopy
from PyObjCTools import AppHelper
from vanilla import *
import os
import httplib, mimetypes, urllib, binascii
from xierpalib.tools.parsers.json import cjson

class SimpleAppAppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, notification):
        SimpleAppWindow()

class DropNSView(NSView):

    def init(self):
        self = super(DropNSView, self).init()
        # # register for file dropping
        self.registerForDraggedTypes_([NSFilenamesPboardType])
        self._dropCallback = None
        return self

    def setDropCallback_(self, callback):
        self._dropCallback = callback

    def draggingEntered_(self, sender):
        source = sender.draggingSource()
        if source == self:
            return NSDragOperationNone
        return NSDragOperationCopy

    def draggingUpdated_(self, sender):
        source = sender.draggingSource()
        if source == self:
            return NSDragOperationNone
        return NSDragOperationCopy

    def draggingExited_(self, sender):
        return None

    def prepareForDragOperation_(self, sender):
        source = sender.draggingSource()
        if source == self:
            return NSDragOperationNone
        pb = sender.draggingPasteboard()
        files = pb.propertyListForType_(NSFilenamesPboardType)
        return self._proposeDrop(files, testing=True)

    def performDragOperation_(self, sender):
        source = sender.draggingSource()
        if source == self:
            return NSDragOperationNone
        pb = sender.draggingPasteboard()
        files = pb.propertyListForType_(NSFilenamesPboardType)
        return self._proposeDrop(files, testing=False)

    def _proposeDrop(self, files, testing):
        if self._dropCallback is None:
            return False
        return self._dropCallback(files, testing)

class Drop(Group):

    nsViewClass = DropNSView

    def __init__(self, posSize, dropCallback=None):
        super(Drop, self).__init__(posSize)
        self._nsObject.setDropCallback_(dropCallback)


class SimpleAppWindow(object):
    u"""
    <doc>
    Implementation of a vanilla-based upload GUI for the Xierpa environment.
    TODO: enable password, encryption via SSH keys.
    </doc>
    """

    # DOMAIN                             = '127.0.0.1'
    DOMAIN = 'red.petr.net'
    PORT = 8001
    HOST = '%s:%s' % (DOMAIN, PORT)
    LOGIN = 'Amex'
    PASSWORD = 'amex'
    PUBLICKEY = ''

    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 600
    WINDOW_MESSAGEHEIGHT = 100

    PARAM_EVENT = 'event'
    PARAM_UPLOAD_CONTENT = 'upload.content'
    PARAM_UPLOAD_FILENAME = 'upload.filename'
    PARAM_UPLOAD_HOST = 'upload.host'
    PARAM_UPLOAD_LOGIN = 'upload.login'
    PARAM_UPLOAD_PUBLICKEY = 'upload.publickey'
    EVENT_XIERPAUPLOAD = 'xierpaupload'
    PATH_INDEXAJAX = '/index/ajax'
    TARGETID_UPLOADRESULT = 'targetid_uploadresult'

    VALID_EXTENSIONS = ['png', 'jpg', 'jpeg', 'tiff', 'tif']

    def __init__(self):
        self.paths = []
        self.w = Window((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), "UploadClient", closable=False)

        self.w.t1 = TextEditor((10, 10, -10, 16), text=self.DOMAIN, callback=self.domainCallback)
        self.w.t2 = TextEditor((10, 30, -10, 16), text=str(self.PORT), callback=self.portCallback)
        self.w.t3 = TextEditor((10, 50, -10, 16), text=self.LOGIN, callback=self.loginCallback)

        self.w.drop = Drop((10, 70, -10, 100), dropCallback=self.dropCallback)
        self.w.drop.text = TextBox((0, 0, -0, 100), 'Drop images or image folders here')
        self.w.uploadbutton = Button((5, 170, 80, 18), 'Upload', callback=self.uploadCallback)
        self.w.testbutton = Button((90, 170, 80, 18), 'Test', callback=self.testCallback)
        self.w.list = List((0, 195, -0, -self.WINDOW_MESSAGEHEIGHT), self.getAsUIList(),
            columnDescriptions=self.getListDescriptor(),
            drawHorizontalLines=True,
            selectionCallback=self.editCallback)
        self.w.message = TextBox((0, -self.WINDOW_MESSAGEHEIGHT, -0, -0), '')
        self.w.open()
        self.w.uploadbutton.enable(False)
        self.w.testbutton.enable(False)

    def message(self, s):
        u"""
        <doc>
        Write message to bottom of GUI.
        </doc>
        """
        self.w.message.set(u'%s' % s)

    def listmessage(self, index, s):
        self.w.list[index]['Result'] = s

    def domainCallback(self, sender):
        u"""
        <doc>
        Callback function for domain field.
        </doc>
        """
        self.DOMAIN = sender.get()

    def portCallback(self, sender):
        u"""
        <doc>
        Callback function for port field.
        </doc>
        """
        self.PORT = sender.get()

    def loginCallback(self, sender):
        u"""
        <doc>
        Callback function for login field.
        </doc>
        """
        self.LOGIN = sender.get()

    def testCallback(self, sender):
        u"""
        <doc>
        Test if server answers.
        </doc>
        """
        self.message('Testing...')
        # One file at the time.
        for index, path in enumerate(self.paths):
            filename = urllib.quote_plus(path)
            # Get the image
            f = open(path, 'rb')
            data = f.read()
            f.close()
            # Make the header
            params = {self.PARAM_EVENT:self.EVENT_XIERPAUPLOAD, 'test':filename}
            result = self.postMultipart(self.HOST, self.PATH_INDEXAJAX, params, [])
            resultdict = cjson.encode(result)
            self.listmessage(index, resultdict.get(self.TARGETID_UPLOADRESULT))
        self.message('Testing DONE')

    def uploadCallback(self, sender):
        u"""
        <doc>
        Main callback to upload the file to a server.
        </doc>
        """
        self.message('Uploading...')
        # One file at the time.
        for index, path in enumerate(self.paths):
            filename = urllib.quote_plus(path)
            # Get the image
            f = open(path, 'rb')
            data = f.read()
            f.close()
            # Make the header
            params = {}
            params[self.PARAM_EVENT] = self.EVENT_XIERPAUPLOAD
            params[self.PARAM_UPLOAD_CONTENT] = binascii.b2a_base64(data)
            params['upload.filename'] = filename
            params[self.PARAM_UPLOAD_HOST] = self.HOST
            params[self.PARAM_UPLOAD_LOGIN] = self.LOGIN
            params[self.PARAM_UPLOAD_PUBLICKEY] = self.PUBLICKEY
            result = self.postMultipart(self.HOST, self.PATH_INDEXAJAX, params, [])
            resultdict = cjson.encode(result)
            self.listmessage(index, resultdict.get(self.TARGETID_UPLOADRESULT))
        self.message('Uploading DONE')

    def dropCallback(self, paths, testing):
        if not testing:
            # # test if the files are correct "only .png, .ttf"
            self.paths = []
            self.result = []
            for path in paths:
                if self.hasCorrectExtension(path):
                    self.setFile4Upload(path)
                else:
                    msg = 'This type of file is not accepted. Valid extensions are '
                    msg += ', '.join(self.VALID_EXTENSIONS)
                    msg += '.'
                    self.message(msg)
            self.w.list.set(self.getAsUIList())
            # Test to set the button state
            self.w.uploadbutton.enable(bool(self.getAsUIList()))
            self.w.testbutton.enable(bool(self.getAsUIList()))
        return True

    def hasCorrectExtension(self, path):
       ext = path.split('.')[-1]
       self.message(ext)
       if ext.lower() in self.VALID_EXTENSIONS:
           return True
       else:
           return False

    def setFile4Upload(self, path):
        if path.startswith('.'):
            pass
        elif os.path.isdir(path):
            for file in os.listdir(path):
                if file.startswith('.'):
                    continue
                self.setFile4Upload(path + '/' + file)
        else:
            self.paths.append(path)
            self.result.append('Not uploaded')

    def editCallback(self, sender):
        u"""
        Get the whole list of the files.
        """
        pass

    def getAsUIList(self):
        list = []
        if self.paths:
            for index, path in enumerate(self.paths):
                list.append(dict(X=True, Name=path.split('/')[-1], Result=self.result[index]))
        return list

    def getFilePaths(self, paths):
        filepaths = []
        for path in paths:
            filepaths.append(path.split('/')[-1])
        return filepaths

    def getListDescriptor(self):
         return [
            dict(title="X", width=48, key='X', cell=CheckBoxListCell()),
            dict(title="Name", key='Name', width=150, editable=False),
            dict(title="Result", key='Result', width=150 - 48),
        ]

    def postMultipart(self, host, selector, fields, files):
        """
        Post fields and files to an HTTP host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return the server's response page.
        """
        content_type, body = self.encodeMultipartFormdata(fields, files)
        h = httplib.HTTP(host)
        h.putrequest('POST', selector)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(body)))
        h.endheaders()
        h.send(body)
        errcode, errmsg, headers = h.getreply()
        return h.file.read()

    def encodeMultipartFormdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for key, value in fields.items():
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self.getContentType(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def getContentType(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

if __name__ == "__main__":
    AppHelper.runEventLoop()