# Zrodla:
# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPainter.html#rendering-quality
# Stack overflow, GPT

# Import modułów
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QToolBar, QWidget, QColorDialog, QFileDialog
# Narzędzia graficzne PySide6
from PySide6.QtGui import QPainter, QPen, QPainterPath, QPixmap, QRegion
from PySide6.QtCore import Qt, QPoint, QRect
from enum import Enum, auto

class Mode(Enum):
    """Klasa definiująca różne tryby rysowania"""
    FREEFORM = auto()  # Tryb rysowania dowolnego kształtu
    RECTANGLE = auto()  # Tryb rysowania prostokąta
    LINE = auto()  # Tryb rysowania linii
    CIRCLE = auto()  # Tryb rysowania koła/elipsy

class Shape:
    """Klasa reprezentująca ogólny kształt, używana jako podstawowa klasa bazowa dla konkretnych kształtów"""
    def __init__(self, color, pen_size):
        """Inicjalizacja kształtu z podanym kolorem i rozmiarem 'pióra' """
        self.path = QPainterPath()  # Ścieżka przechowująca kształt
        self.color = color  # Kolor kształtu
        self.pen_size = pen_size  # Rozmiar "pióra"

class Rectangle:
    """Klasa reprezentująca prostokąt """
    def __init__(self, color, pen_size, rect):
        """Inicjalizacja prostokąta z podanym kolorem, rozmiarem 'pióra' i prostokątnym obszarem"""
        self.rect = rect  # Obszar prostokąta (QRect)
        self.color = color  # Kolor prostokąta
        self.pen_size = pen_size

class Line:
    """Klasa reprezentująca linię"""
    def __init__(self, color, pen_size, start_point, end_point):
        """Inicjalizacja linii z podanym kolorem, rozmiarem 'pióra' oraz punktami początkowym i końcowym"""
        self.color = color  # Kolor
        self.pen_size = pen_size
        self.start_point = start_point  # Punkt początkowy (QPoint)
        self.end_point = end_point  # Punkt końcowy (QPoint)

class Circle:
    """Klasa reprezentująca koło/elipsę"""
    def __init__(self, color, pen_size, rect):
        """Inicjalizacja koła z podanym kolorem, rozmiarem 'pióra' i obszarem ograniczającym"""
        self.rect = rect  # Obszar ograniczający koło (QRect)
        self.color = color  # Kolor
        self.pen_size = pen_size

class Canvas(QWidget):
    """Klasa reprezentująca obszar do rysowania"""
    def __init__(self):
        """Inicjalizacja obszaru do rysowania"""
        super().__init__()
        self.drawing = False  # Flaga określająca, czy obecnie jest rysowany kształt
        self.mode = Mode.FREEFORM  # Aktualny tryb rysowania (domyslnie rysowanie dowolnego kształtu)
        self.color = Qt.black  # Aktualny kolor pióra
        self.pen_size = 2  # Aktualny rozmiar pióra
        self.shapes = []  # Lista przechowująca wszystkie narysowane kształty
        self.start_point = QPoint()  # Punkt początkowy dla rysowanych kształtów
        self.end_point = QPoint()  # Punkt końcowy dla rysowanych kształtów
        self.current_shape = QPainterPath()  # Aktualny kształt w trakcie rysowania

    def paintEvent(self, event):
        """Metoda obsługująca zdarzenie malowania"""
        painter = QPainter(self)  # Utworzenie obiektu QPainter do rysowania
        painter.setRenderHint(QPainter.Antialiasing)  # Ustawienie flagi dla płynniejszego rysowania
        # https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPainter.html#rendering-quality
        
        # Rysowanie wszystkich kształtów
        for shape in self.shapes:
            pen = QPen(shape.color, shape.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)  # Utworzenie pióra
            painter.setPen(pen)  # Ustawienie pióra dla rysowania kształtu
            if isinstance(shape, Shape):
                painter.drawPath(shape.path)  # Rysowanie dowolnego kształtu
            elif isinstance(shape, Rectangle):
                painter.drawRect(shape.rect)  # Rysowanie prostokąta
            elif isinstance(shape, Line):
                painter.drawLine(shape.start_point, shape.end_point)  # Rysowanie linii
            elif isinstance(shape, Circle):
                painter.drawEllipse(shape.rect)  # Rysowanie koła/elipsy

        # Rysowanie aktualnie rysowanego kształtu (podgląd)
        if self.drawing:
            pen = QPen(self.color, self.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)  # Utworzenie pióra
            painter.setPen(pen)  # Ustawienie pióra dla rysowania aktualnego kształtu
            if self.mode == Mode.FREEFORM:
                temp_path = QPainterPath(self.current_shape)
                temp_path.lineTo(self.end_point)
                painter.drawPath(temp_path)  # Rysowanie tymczasowej ścieżki dla trybu rysowania dowlnego kształtu
            elif self.mode == Mode.LINE:
                painter.drawLine(self.start_point, self.end_point)  # Rysowanie linii
            elif self.mode == Mode.CIRCLE:
                painter.drawEllipse(QRect(self.start_point, self.end_point))  # Rysowanie koła
            elif self.mode == Mode.RECTANGLE:
                painter.drawRect(QRect(self.start_point, self.end_point))  # Rysowanie prostokąta

    def set_color(self, color):
        """Metoda ustawiająca aktualny kolor pióra"""
        self.color = color  # Ustawienie koloru pióra na podany kolor
    
    def set_pen_size(self, size):
        """Metoda ustawiająca aktualny rozmiar pióra"""
        self.pen_size = size  # Ustawienie rozmiaru pióra na podany rozmiar
    
    def mousePressEvent(self, event):
        """Metoda obsługująca zdarzenie naciśnięcia przycisku myszy"""
        self.drawing = True  # Ustawienie flagi rysowania na True
        self.start_point = event.pos()  # Ustawienie punktu początkowego na pozycję myszy
        self.end_point = event.pos()  # Ustawienie punktu końcowego na pozycję myszy
        if self.mode == Mode.FREEFORM:
            self.current_shape = QPainterPath()  # Inicjalizacja ścieżki dla trybu rysowania dowlnego kształtu
            self.current_shape.moveTo(event.pos())  # Przejście do pozycji początkowej ścieżki
        self.update()  # Odświeżenie widoku
    
    def mouseMoveEvent(self, event):
        """Metoda obsługująca zdarzenie przesuwania myszy"""
        if self.drawing:  # Sprawdzenie, czy aktualnie trwa rysowanie
            self.end_point = event.pos()  # Ustawienie punktu końcowego na aktualną pozycję myszy
            if self.mode == Mode.FREEFORM:
                self.current_shape.lineTo(event.pos())  # Dodanie linii do ścieżki dla trybu rysowania dowlnego kształtu
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Metoda obsługująca zdarzenie zwolnienia przycisku myszy"""
        self.drawing = False  # Ustawienie flagi rysowania na False
        if self.mode == Mode.FREEFORM:
            new_shape = Shape(self.color, self.pen_size)  # Utworzenie nowego kształtu
            new_shape.path = self.current_shape  # Ustawienie ścieżki kształtu na aktualną ścieżkę
            self.shapes.append(new_shape)  # Dodanie kształtu do listy kształtów
        elif self.mode == Mode.RECTANGLE:
            new_shape = Rectangle(self.color, self.pen_size, QRect(self.start_point, event.pos()))  # Utworzenie nowego prostokąta
            self.shapes.append(new_shape)  # Dodanie prostokąta do listy kształtów
        elif self.mode == Mode.LINE:
            new_shape = Line(self.color, self.pen_size, self.start_point, event.pos())  # Utworzenie nowej linii
            self.shapes.append(new_shape)  # Dodanie do listy kształtów
        elif self.mode == Mode.CIRCLE:
            new_shape = Circle(self.color, self.pen_size, QRect(self.start_point, event.pos()))  # Utworzenie nowego kształtu koła/elipsy
            self.shapes.append(new_shape)  # Dodanie do listy kształtów
        self.current_shape = QPainterPath()  # Zresetowanie aktualnej ścieżki
        self.update()  # Odświeżenie widoku
    
    def clear_canvas(self):
        """Metoda czyszcząca okno rysowania"""
        self.shapes = []  # Wyczyszczenie listy kształtów
        self.current_shape = QPainterPath()  # Zresetowanie aktualnej ścieżki
        self.update()  # Odświeżenie widoku

class MainWindow(QMainWindow):
    """Główne okno aplikacji"""
    def __init__(self):
        """Inicjalizacja głównego okna"""
        super().__init__()  # Wywołanie konstruktora klasy nadrzędnej QMainWindow
        self.canvas = Canvas()  # Utworzenie instancji klasy Canvas do rysowania
        self.initUI()  # Inicjalizacja interfejsu użytkownika (definicja położenia/rozmiarów itd)

    def initUI(self):
        """Inicjalizacja interfejsu użytkownika"""
        self.setCentralWidget(self.canvas)  # Ustawienie obszaru do rysowania
        self.setWindowTitle("My PySide6 Paint")  # Ustawienie tytułu głównego okna
        self.setGeometry(100, 100, 800, 600)  # Ustawienie rozmiaru i położenia głównego okna
        self.backgroundImage = QPixmap() # Inicjalizacja atrybutu backgroundImage jako pustego QPixmap # NEW
        
        loadImageButton = QPushButton("Load image",) # Przycisk do wczytywania obrazów NEW
        loadImageButton.clicked.connect(self.loadImage) # Uruchamia funkcję loadImage NEW
        
        saveImageButton = QPushButton("Save image",) # Przycisk do zapisywania obrazów NEW
        saveImageButton.clicked.connect(self.save_image) # Uruchamia funkcję save_image NEW

        clear_button = QPushButton("Clear")  # Przycisk do czyszczenia obszaru rysowania
        clear_button.clicked.connect(self.clear)  # Połączenie przycisku z metodą czyszczącą

        color_button = QPushButton("Color")  # Przycisk do wyboru koloru
        color_button.clicked.connect(self.choose_color)  # Połączenie przeycisku z metodą

        pen_size_combo = QComboBox()  # ComboBox do wyboru rozmiaru pióra
        pen_size_combo.addItems(["1", "2", "3", "4", "5"])  # Dodanie dostępnych rozmiarów
        pen_size_combo.currentIndexChanged.connect(self.set_pen_size) # Połączenie combo-boxa z metodą

        mode_combo = QComboBox()  # ComboBox do wyboru trybu rysowania
        mode_combo.addItem("Freeform", Mode.FREEFORM)  # Dodanie opcji rysowania dowolnego kształtu
        mode_combo.addItem("Rectangle", Mode.RECTANGLE)  # Prostokąt
        mode_combo.addItem("Line", Mode.LINE)  # Linia
        mode_combo.addItem("Circle", Mode.CIRCLE)  # Koło/elipsa
        mode_combo.currentIndexChanged.connect(self.set_mode)  # Połączenie ComboBoxa z metodą

        toolbar = QToolBar()  # Pasek narzędzi
        toolbar.addWidget(loadImageButton)  # Dodanie przycisków
        toolbar.addWidget(clear_button)  
        toolbar.addWidget(color_button)  
        toolbar.addWidget(pen_size_combo)  # Dodanie ComboBoxów
        toolbar.addWidget(mode_combo) 
        toolbar.addWidget(saveImageButton) 
        self.addToolBar(Qt.BottomToolBarArea, toolbar)  # Dodanie paska narzędzi do głównego okna
        
    def loadImage(self): # NEW
        imagePath, _ = QFileDialog.getOpenFileName(self, "Select image", "", "Image formats available: (*.png *.jpg *.jpeg *.bmp)")  # Wybór i wczytanie obrazka
        if imagePath:
            self.backgroundImage = QPixmap(imagePath)
            self.update()  # Odświeżenie widoku
            
    def save_image(self): # NEW
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath:
            # Tworzenie QPixmap do renderowania
            pixmap = QPixmap(self.size())  # Ustawienie wymiarów QPixmap na wymiary okna
            painter = QPainter(pixmap) # Będziemy dokonywali rysowania na pixmap - całe obrazki i nasze rysunki, które zapiszemy (po zrenderowaniu) do pliku
            self.render(painter, QPoint(), QRegion(self.rect()), QWidget.RenderFlags(QWidget.DrawWindowBackground | QWidget.DrawChildren))  # Renderowanie całego okna (w tym tła i rysunków) na QPainter
            # painter - obiekt docelowy na którym rysujemy
            # QPoint - punkt 0,0 - punkt startowy (lewy górny róg)
            # QRegion(self.rect()) - renderujemy cały obszar kreslenia
            #  QWidget.RenderFlags... - flagi renderowania - pokazują, że mamy uwzględnić tło widgetu, jak i elementy potomne (Children)
            painter.end()
            pixmap.save(filePath)  # Zapis obrazu do wybranego pliku
      
    def paintEvent(self, event): # NEW
        # Rozszerzenie metody paintEvent do rysowania obrazka w tle - później na nim będzie rysowany wybrany kształt / kształty
        painter = QPainter(self)
        if not self.backgroundImage.isNull(): # Rysowanie wczutanego obrazka 
            painter.drawPixmap(self.rect(), self.backgroundImage)
        # A teraz można rysować na nim kształty
        super().paintEvent(event)
        
    def clear(self): # NEW
        # Resetowanie obrazka w tle do pustego QPixmap
        self.backgroundImage = QPixmap() # Czyszczenie obrazka
        self.canvas.clear_canvas() # Czyszczenie canvasa

    def choose_color(self):
        """Metoda obsługująca wybór koloru"""
        color = QColorDialog.getColor()  # Pobranie wybranego koloru
        if color.isValid():  # Sprawdzenie, czy wybrany kolor jest prawidłowy
            self.canvas.set_color(color)  # Ustawienie wybranego koloru dla rysowanego kształu

    def set_pen_size(self, index):
        """Metoda obsługująca ustawienie rozmiaru pióra"""
        size = int(self.sender().currentText())  # Pobranie rozmiaru pióra z ComboBox
        self.canvas.set_pen_size(size)  # Ustawienie rozmiaru pióra

    def set_mode(self, index):
        """Metoda obsługująca ustawienie trybu rysowania"""
        mode = self.sender().itemData(index)  # Pobranie wybranego trybu rysowania z ComboBox
        self.canvas.mode = mode  # Ustawienie wybranego trybu rysowania

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Utworzenie instancji aplikacji
    window = MainWindow()  # Utworzenie instancji głównego okna
    window.show()  # Wyświetlenie głównego okna
    sys.exit(app.exec_())  # Uruchomienie pętli głównej aplikacji
