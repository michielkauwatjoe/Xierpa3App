#-*- coding: utf-8 -*-
#
#  main.py
#  Xierpa3App
#
#  Created by Michiel on 27/05/14.
#  Copyright (c) 2014 __MyCompanyName__. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import X3AppDelegate

# pass control to AppKit
AppHelper.runEventLoop()
