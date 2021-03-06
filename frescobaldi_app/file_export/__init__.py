# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
Export to non-lilypond file types.
"""

from __future__ import unicode_literals

import os

from PyQt4.QtCore import Qt, QUrl
from PyQt4.QtGui import QAction, QFileDialog, QKeySequence, QMessageBox

import app
import actioncollection
import actioncollectionmanager
import plugin
import tokeniter
import info


class FileExport(plugin.MainWindowPlugin):
    def __init__(self, mainwindow):
        ac = self.actionCollection = Actions()
        actioncollectionmanager.manager(mainwindow).addActionCollection(ac)
        ac.export_musicxml.triggered.connect(self.exportMusicXML)
        ac.export_audio.triggered.connect(self.exportAudio)

    def exportMusicXML(self):
        """ Convert the current document to MusicXML """
        doc = self.mainwindow().currentDocument()
        orgname = doc.url().toLocalFile()
        filename = os.path.splitext(orgname)[0] + '.xml'
        caption = app.caption(_("dialog title", "Export MusicXML File"))
        filetypes = '{0} (*.xml);;{1} (*)'.format(_("XML Files"), _("All Files"))
        filename = QFileDialog.getSaveFileName(self.mainwindow(), caption, filename, filetypes)
        if not filename:
            return False # cancelled
        import ly.musicxml
        writer = ly.musicxml.writer()
        #writer.parse_tokens(tokeniter.all_tokens(doc))
        writer.parse_tree(doc)
        xml = writer.musicxml()
        # put the Frescobaldi version in the xml file
        software = xml.root.find('.//encoding/software')
        software.text = "{0} {1}".format(info.appname, info.version)
        try:
            xml.write(filename)
        except (IOError, OSError) as err:
            QMessageBox.warning(self.mainwindow(), app.caption(_("Error")),
                _("Can't write to destination:\n\n{url}\n\n{error}").format(
                    url=filename, error=err.strerror))

    def exportAudio(self):
        """ Convert the current document to Audio """
        doc = self.mainwindow().currentDocument()
        orgname = doc.url().toLocalFile()
        filename = os.path.splitext(orgname)[0] + '.wav'
        caption = app.caption(_("dialog title", "Export Audio File"))
        filetypes = '{0} (*.wav);;{1} (*)'.format(_("WAV Files"), _("All Files"))
        filename = QFileDialog.getSaveFileName(self.mainwindow(), caption, filename, filetypes)
        if not filename:
            return False # cancelled
        file = os.path.splitext(orgname)[0]
        if os.path.exists(file + '.midi'):
            os.system('timidity "%s.midi" -Ow -o "%s.wav"' % (file, file))
        else:
            QMessageBox.critical(None, _("Error"),
                    _("The audio file couldn't be created. Please create midi file first"))


class Actions(actioncollection.ActionCollection):
    name = "file_export"
    def createActions(self, parent):
        self.export_musicxml = QAction(parent)
        self.export_audio = QAction(parent)

    def translateUI(self):
        self.export_musicxml.setText(_("Export Music&XML..."))
        self.export_musicxml.setToolTip(_("Export current document as MusicXML."))

        self.export_audio.setText(_("Export Audio..."))
        self.export_audio.setToolTip(_("Export to different audio formats."))

