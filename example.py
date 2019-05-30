# Copyright 2019 Matthew J. Aburn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See <http://www.gnu.org/licenses/>.
"""
Demonstrate python bindings for QCustomPlot.
"""

from __future__ import absolute_import
import sys
import numpy as np
from PySide2 import QtCore, QtGui, QtWidgets
import QCustomPlot


class DemoWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.text = QtWidgets.QLabel('Some text.')
        self.plot = QCustomPlot.QCustomPlot()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.plot, stretch=1)
        self.setLayout(layout)
        self.plot.addGraph()
        x = np.linspace(0.0, 12.0, 1201)
        y = np.exp(-0.8 * x) * np.sin(10 * x)
        self.plot.graph(0).setData(x, y)
        self.plot.xAxis.setRange(0.0, 8.0)
        self.plot.yAxis.setRange(-1.0, 1.0)
        self.plot.setInteraction(QCP.iRangeDrag, True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dw = DemoWindow()
    available = app.desktop().availableGeometry(dw)
    dw.resize(available.width() / 2.0, available.height() / 2.0)
    dw.show()
    res = app.exec_()
    sys.exit(res)
