class imageData(object):
    def __init__(self, fileID, fuploader, priority, picdata, tag, comment,
                 uploadTime, fileType):
        self.imageID = fileID
        self.imagesUploader = fuploader
        self.imagesPriority = priority
        self.imagesComments = comment
        self.imagesData = picdata
        self.imagesTag = tag
        self.imagesUploadtime = uploadTime
        self.imagesFiletype = fileType

    def set_imageID(self, fileID):
        self.imageID = fileID


    def set_imagesComments(self, comment):
        self.imagesComments = comment
    
    
    def set_imagesData(self, picdata):
        self.imagesData = picdata
    
    
    def set_imagesTag(self, tag):
        self.imagesTag = tag
    
    
    def set_imagesUploader(self, fuploader):
        self.imagesUploader = fuploader
    
    
    def set_imagesPriority(self, priority):
        self.imagesPriority = priority
    
    
    def set_imagesUploadtime(self, uploadTime):
        self.imagesUploadtime = uploadTime
    
    
    def set_imagesFiletype(self, fileType):
        self.imagesFiletype = fileType