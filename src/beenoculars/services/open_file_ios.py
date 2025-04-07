import logging
from pathlib import Path
from typing import Any

from rubicon.objc import (
    ObjCClass,
    ObjCProtocol,
    objc_block,
    objc_const,
    objc_method,
    py_from_ns,
)
from rubicon.objc.runtime import load_library, objc_id

import beenoculars.core as core
from beenoculars.core import safe_async_call

log = logging.getLogger(__name__)

# Import necessary UIKit classes
UIDocumentPickerViewController = ObjCClass("UIDocumentPickerViewController")
UIApplication = ObjCClass("UIApplication")
NSObject = ObjCClass("NSObject")
UIViewController = ObjCClass("UIViewController")
UIDocumentPickerDelegate = ObjCProtocol("UIDocumentPickerDelegate")
NSURL = ObjCClass("NSURL")
NSNotificationCenter = ObjCClass('NSNotificationCenter')


class DocumentPickerDelegate(NSObject,  # type: ignore
                             protocols=[UIDocumentPickerDelegate]):  # type: ignore

    @objc_method
    def init_(self):
        self = self.init()
        if self is None:
            return None
        self.serviceCallback = None
        return self

    @objc_method
    def set_serviceCallback(self, serviceCallback: objc_block):
        self.serviceCallback = serviceCallback

    @objc_method
    def get_serviceCallback(self):
        return self.serviceCallback

    @objc_method
    def documentPicker_didPickDocumentsAtURLs_(self, picker: objc_id, urls: objc_id) -> None:
        # Handle the selected files
        if self.serviceCallback is not None:
            self.serviceCallback(urls)  # type: ignore
        keyWindow = UIApplication.sharedApplication.keyWindow  # type: ignore
        keyWindow.rootViewController.dismissViewControllerAnimated_completion_(
            True, None)

    @objc_method
    def documentPickerWasCancelled_(self, picker: objc_id) -> None:
        keyWindow = UIApplication.sharedApplication.keyWindow  # type: ignore
        keyWindow.rootViewController.dismissViewControllerAnimated_completion_(
            True, None)


class IOSFileOpen(core.AsyncService):
    def __init__(self,
                 document_types: list[str] = ["UTTypePNG",
                                              "UTTypeJPEG",
                                              "UTTypeWebP",
                                              "UTTypeTIFF",
                                              "UTTypeGIF",
                                              "UTTypeBMP",
                                              "UTTypeRAWImage",
                                              #   "UTTypeImage"
                                              ],
                 allowsMultipleSelection: bool = True) -> None:
        super().__init__()
        # IMPORTANT: the delegate must be create and store here
        # because the delegate is a weak reference
        # and can be deleted without any reference in Python side
        self.delegate = DocumentPickerDelegate.alloc().init_()
        self.document_types = document_types
        self.allowsMultipleSelection = allowsMultipleSelection

    @safe_async_call(log)
    async def handle_event(self,
                           widget: Any,
                           app,
                           service_callback,
                           *args, **kwargs):
        if service_callback is None:
            raise ValueError("service_callback must be provided")
        libcf = load_library("UniformTypeIdentifiers")
        # You can specify other UTIs if needed
        document_types = [objc_const(libcf, item)
                          for item in self.document_types]
        picker = UIDocumentPickerViewController.alloc()  # type: ignore
        picker = picker.initForOpeningContentTypes_(
            document_types)
        picker.allowsMultipleSelection = self.allowsMultipleSelection

        def local_callback(fnames_c: objc_id) -> None:
            # convert the NSArray to a Python list
            fnames_c_list = py_from_ns(fnames_c)
            fnames = []
            for item in fnames_c_list:  # type: ignore
                # Convert NSURL to string
                path_str: str = py_from_ns(item.path)  # type: ignore
                # Convert to Path object
                fnames.append(Path(path_str))
            if self.allowsMultipleSelection:
                service_callback(fnames)
            else:
                if len(fnames) > 0:
                    service_callback(fnames[0])
        # Set the service callback
        self.delegate.set_serviceCallback(local_callback)  # type: ignore
        # Set the delegate
        picker.delegate = self.delegate
        # Present the document picker
        keyWindow = UIApplication.sharedApplication.keyWindow  # type: ignore
        keyWindow.rootViewController.presentViewController_animated_completion_(
            picker, True,  None)
