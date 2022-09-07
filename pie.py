
import sys

from PyQt5.QtChart import QChart, QPieSeries, QChartView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QMainWindow, QApplication


class TestChart(QMainWindow):

    def __init__(self):
        super().__init__()

        self.series = QPieSeries()

        self.series.append('Jane', 6)
        self.series.append('Joe', 6)
        self.series.append('Andy', 2)
        self.series.append('Barbara', 2)
        self.series.append('Axel', 1)

        self.slice = self.series.slices()[1]
        self.slice.setExploded()
        self.slice.setLabelVisible()
        self.slice.setPen(QPen(Qt.darkGreen, 2))
        self.slice.setBrush(Qt.green)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle('Simple piechart example')
        self.chart.legend().show()

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(self._chart_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TestChart()
    window.show()
    window.resize(440, 300)

    sys.exit(app.exec())