import asyncio
import socket
import sys
import threading
import cv2, cv2_enumerate_cameras as cv2_ec
import numpy as np
import pyautogui
import websockets
import pygetwindow as gw
import mss
import configparser, os
from functools import partial
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QLineEdit,
    QSlider,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ----------------------------------------------------
# Loading / Creating config
# ----------------------------------------------------
config_folder_path = os.path.expandvars("%APPDATA%/ArthyDev/Screenshare")
config_folder_path = os.path.normpath(config_folder_path)


# Generate config folder
if not os.path.isdir(config_folder_path):
  os.makedirs(config_folder_path, exist_ok=True)

# Generate config file
config_file_path = os.path.join(config_folder_path, "config.cfg")
do_config_exists = os.path.isfile(config_file_path)
if not do_config_exists:

  config_file = configparser.ConfigParser()
  config_file["Software"] = {
    "VERSION": "1.0",
    "LANGUAGE": "ENG",
    "SAVED_IPS": "[]"
  }
  # [{"name":"", "ip":""}], ENG / BR
  config_file["Host_Settings"] = {
    "DEFAULT_PORT": "8765",
    "IDX_FPS_TARGET": "2",
    "STREAM_RES": "(1280, 720)",
    "SHOW_CURSOR": "True",
    "SELECTED_MONITOR": "0"
  }

  config_file["Webcam_Settings"] = {
    "SELECTED_WEBCAM": "None",
    "WEBCAM_ON_STREAM": "False",
    "WEBCAM_ON_STREAM_SIZE": "0.25",
    "WEBCAM_DEFAULT_POS_ENABLED": "True",
    "WEBCAM_DEFAULT_POS": "0",
    "WEBCAM_X": "0",
    "WEBCAM_Y": "0",
    "WEBCAM_CROP_ENABLED": "False",
    "W_CROP_TOP": "0",
    "W_CROP_RIGHT": "0",
    "W_CROP_BOTTOM": "0",
    "W_CROP_LEFT": "0"
  }

  with open(config_file_path, "w") as configfile:
    config_file.write(configfile)

config = configparser.ConfigParser()
config.read(config_file_path, encoding="utf-8")
config_software = config["Software"]
config_host = config["Host_Settings"]
config_webcam = config["Webcam_Settings"]

# ----------------------------------------------------
# Languages
# ----------------------------------------------------
langs = {
  "ENG": {
    "MAIN_SCREEN":{
      "MAIN_TITLE":"Scalie",
      "STOP_HOSTING":"Stop",
      "STREAM_TYPE": {
        "0":"Choose Type",
        "1":"Entire Screen",
        "2":"Specific Window",
        "3":"Webcam Only"
        },
      "STREAM_IP_PLACEHOLDER": "Type Stream IP",
    },
    "HOST_SETTINGS":{
      "HOST_SETTINGS_TITLE": "Host Settings",
      "SERVER_PORT":"Port Number",
      "STREAM_FPS":"Stream FPS",
      "FPS_OPTIONS": {
        "0":"Hopeless (5)",
        "1":"Last Measure (10)",
        "2":"Tripping Over (15)",
        "3":"Stop Motion (20)",
        "4":"Cinematic (25)",
        "5":"Normal (30)",
        "6":"High (60)",
        "7":"GLaDOS (144)",
      },
      "RESOLUTION":"Resolution",
      "RESOLUTION_WIDTH_PLACEHOLDER":"Width",
      "RESOLUTION_HEIGHT_PLACEHOLDER":"Height",
      "SHOW_CURSOR":"Show Cursor",
      "WINDOWS_TO_STREAM":"Windows to Stream",
      "WINDOWS_TO_STREAM_DEFAULT":"None",
      "MONITOR":"Monitor",
      "LANGUAGES":"Languages",
      "SAVE_SETTINGS_BUTTON":"Save",
    },
    "WEBCAM_SETTINGS":{
      "WEBCAM_SETTINGS_TITLE": "Webcam Settings",
      "WEBCAMS":"Webcams",
      "WEBCAM_ON_STREAM_AND_SIZE":"On Stream | Size",
      "SNAP_TO_CORNER":"Snap to Corner",
      "UPPER_LEFT":"Upper Left",
      "UPPER_RIGHT":"Upper Right",
      "LOWER_LEFT":"Lower Left",
      "LOWER_RIGHT":"Lower Right",
      "POSITION_X":"Position X",
      "POSITION_Y":"Position Y",
      "ENABLE_CROPPING":"Enable Cropping",
      "CROP_TOP":"Crop Top",
      "CROP_BOTTOM":"Crop Bottom",
      "CROP_LEFT":"Crop Left",
      "CROP_RIGHT":"Crop Right",
    },
    "SAVED_CONTACTS":{
      "SAVED_CONNECTIONS_TITLE":"Saved Contacts",
      "CONTACT_NAME":"Contact Name",
      "CONTACT_IP":"IP Address"
    }
  },
  "BR": {
    "MAIN_SCREEN":{
      "MAIN_TITLE": "Scalie",
      "STOP_HOSTING":"Parar",
      "STREAM_TYPE": {
        "0":"Escolha...",
        "1":"Tela Inteira",
        "2":"Janela Específica",
        "3":"Somente Webcam"
        },
      "STREAM_IP_PLACEHOLDER": "Digite o IP",
    },
    "HOST_SETTINGS":{
      "HOST_SETTINGS_TITLE": "Configurações do Host",
      "SERVER_PORT":"Port Number",
      "STREAM_FPS":"FPS da Stream",
      "FPS_OPTIONS": {
        "0":"Fim da linha (5)",
        "1":"Última tentativa (10)",
        "2":"Tropeçandinho (15)",
        "3":"Stop Motion (20)",
        "4":"Cinemático (25)",
        "5":"Normal (30)",
        "6":"Alto (60)",
        "7":"GLaDOS (144)",
      },
      "RESOLUTION":"Resolução",
      "RESOLUTION_WIDTH_PLACEHOLDER":"Largura",
      "RESOLUTION_HEIGHT_PLACEHOLDER":"Altura",
      "SHOW_CURSOR":"Mostrar Cursor",
      "WINDOWS_TO_STREAM":"Janela Específica",
      "WINDOWS_TO_STREAM_DEFAULT":"Nenhuma",
      "MONITOR":"Monitor",
      "LANGUAGES":"Linguagens",
      "SAVE_SETTINGS_BUTTON":"Salvar",
    },
    "WEBCAM_SETTINGS":{
      "WEBCAM_SETTINGS_TITLE": "Configurações da Webcam",
      "WEBCAMS":"Webcams",
      "WEBCAM_ON_STREAM_AND_SIZE":"Sobre Stream | Tamanho",
      "SNAP_TO_CORNER":"Fixar nos Cantos",
      "UPPER_LEFT":"Upper Left",
      "UPPER_RIGHT":"Upper Right",
      "LOWER_LEFT":"Lower Left",
      "LOWER_RIGHT":"Lower Right",
      "POSITION_X":"Posição X",
      "POSITION_Y":"Posição Y",
      "ENABLE_CROPPING":"Habilitar Cropping",
      "CROP_TOP":"Croppar Topo",
      "CROP_BOTTOM":"Croppar Baixo",
      "CROP_LEFT":"Croppar Esquerda",
      "CROP_RIGHT":"Croppar Direita",
    },
    "SAVED_CONTACTS":{
      "SAVED_CONNECTIONS_TITLE": "Contatos Salvos",
      "CONTACT_NAME":"Nome do Contato",
      "CONTACT_IP":"Endereço IP"
    }
  }
}

# ----------------------------------------------------
# Setting up vars
# ----------------------------------------------------
lang = langs[config_software["LANGUAGE"]]
screen_width, screen_height = pyautogui.size()

# Global vars
FPS_OPTIONS = [5, 10, 15, 20, 25, 30, 60, 144]

# Host vars
HOST_SETTINGS_ACTIVE = False
DEFAULT_PORT = config_host["DEFAULT_PORT"]
IDX_FPS_TARGET = int(config_host["IDX_FPS_TARGET"]) # (15) Int
FPS_TARGET_INT = FPS_OPTIONS[IDX_FPS_TARGET]
STREAM_RES = eval(config_host["STREAM_RES"]) # (1280, 720) Set
SHOW_CURSOR = eval(config_host["SHOW_CURSOR"]) # Boolean
SELECTED_MONITOR = int(config_host["SELECTED_MONITOR"])
SAVED_IPS = eval(config_software["SAVED_IPS"])

# Webcam vars
WEBCAM_SETTINGS_ACTIVE = False
WEBCAM_WIDTH = 0
WEBCAM_HEIGHT = 0

SELECTED_WEBCAM = None
WEBCAM_ON_STREAM = eval(config_webcam["WEBCAM_ON_STREAM"]) # False
WEBCAM_ON_STREAM_SIZE = float(config_webcam["WEBCAM_ON_STREAM_SIZE"]) # 0.25
WEBCAM_DEFAULT_POS_ENABLED = eval(config_webcam["WEBCAM_DEFAULT_POS_ENABLED"]) # Boolean
WEBCAM_DEFAULT_POS = int(config_webcam["WEBCAM_DEFAULT_POS"]) # 0 SE, 1 SD, 2 IE, 3 ID
WEBCAM_X = int(config_webcam["WEBCAM_X"])
WEBCAM_Y = int(config_webcam["WEBCAM_Y"])
WEBCAM_CROP_ENABLED = eval(config_webcam["WEBCAM_CROP_ENABLED"]) # False
W_CROP_TOP = float(config_webcam["W_CROP_TOP"])
W_CROP_RIGHT = float(config_webcam["W_CROP_RIGHT"])
W_CROP_BOTTOM = float(config_webcam["W_CROP_BOTTOM"])
W_CROP_LEFT = float(config_webcam["W_CROP_LEFT"])

STREAM_TYPE = 0
SELECTED_WINDOW_TITLE = ""

IS_HOSTING = False
CONNECTED_CLIENTS = set()
test_var = "Hello World!"

# #d9534f RED
# #00cc00 GREEN
# #d95 Yellow / Orange

# ----------------------------------------------------
# Main App
# ----------------------------------------------------
class ScreenshareApp(QMainWindow):
  update_image_signal = pyqtSignal(str, QImage)
  remove_stream_signal = pyqtSignal(str)

  def __init__(self):
    super().__init__()

    self.active_streams = {}
    self.focused_ip = None
    self.grid_cols = 2

    self.update_image_signal.connect(self.dispatch_frame)
    self.remove_stream_signal.connect(self.close_stream)

    # ----------------------------------------------------
    # Setup
    # ----------------------------------------------------

    self.screen_width, self.screen_height = pyautogui.size()
    self.app_width, self.app_height = (round(self.screen_width*0.65), round(self.screen_height*0.65))

    self.setWindowTitle("Screensharing")
    self.setGeometry(self.screen_width//2-self.app_width//2, self.screen_height//2-self.app_height//2, self.app_width, self.app_height)

    # Global styles
    self.setStyleSheet("""
        QMainWindow { background-color: #1e1e1e; }
        #CentralWidget { border: none; }
        #HostButton { background-color: #666; color: white; font-weight: bold; } #HostButton:hover { background-color: #888 }
        #SettingsButton { font-family: "Segoe UI Symbol", "Arial Unicode MS", "sans-serif"; font-size: 12px; }
        QPushButton { background-color: #444; color: white; border: None; padding: 6px 12px; border-radius: 4px; } QPushButton:hover { background-color: #777; }
        QComboBox { background-color: #444; color: white; border: None; padding: 6px 8px; border-radius: 4px; }
        QLineEdit { background-color: #444; color: white; border: None; padding: 6px 8px; border-radius: 4px; }
    """)

    # ----------------------------------------------------
    # Main Box
    # ----------------------------------------------------
    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    central_widget.setObjectName("CentralWidget")

    main_layout = QVBoxLayout()
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    # ----------------------------------------------------
    # Top Bar
    # ----------------------------------------------------
    top_bar = QHBoxLayout()

    # Host button
    global IS_HOSTING
    self.host_button = QPushButton("Host")
    self.host_button.setObjectName("HostButton")
    self.host_button.setCursor(Qt.CursorShape.PointingHandCursor)
    self.host_button.clicked.connect(self.host)
    self.host_button.setFixedWidth(75)

    # Dropdown stream type
    stream_combobox = QComboBox()
    stream_combobox.addItems([lang["MAIN_SCREEN"]["STREAM_TYPE"]["0"], lang["MAIN_SCREEN"]["STREAM_TYPE"]["1"], lang["MAIN_SCREEN"]["STREAM_TYPE"]["2"], lang["MAIN_SCREEN"]["STREAM_TYPE"]["3"]])
    stream_combobox.currentIndexChanged.connect(self.stream_type)

    # Settings button
    settings_button = QPushButton("🔨")
    settings_button.setObjectName("SettingsButton")
    settings_button.clicked.connect(self.show_hosting_settings)
    settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
    settings_button.setFixedWidth(35)

    # Settings button
    webcam_settings_button = QPushButton("📷")
    webcam_settings_button.clicked.connect(self.show_webcam_settings)
    webcam_settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
    webcam_settings_button.setFixedWidth(35)

    # Debug button
    """
    testButton = QPushButton("Test")
    testButton.clicked.connect(self.on_test_button_click)
    testButton.setObjectName("TestButton")
    testButton.setFixedWidth(100)
    """

    # Adding widgets to top bar left side
    top_bar.addWidget(self.host_button)
    top_bar.addWidget(stream_combobox)
    top_bar.addWidget(settings_button)
    top_bar.addWidget(webcam_settings_button)
    #top_bar.addWidget(testButton)

    # Right side
    top_bar.addStretch()

    # Saved IP's
    saved_ips = QPushButton("📋")
    saved_ips.setStyleSheet("font-size: 12px;")
    saved_ips.setFixedWidth(35)
    saved_ips.setCursor(Qt.CursorShape.PointingHandCursor)
    saved_ips.clicked.connect(self.show_saved_ips)

    # IP Input
    self.ip = ""
    self.ip_input = QLineEdit()
    self.ip_input.setPlaceholderText(lang["MAIN_SCREEN"]["STREAM_IP_PLACEHOLDER"])
    self.ip_input.setMaximumWidth(110)
    self.ip_input.textChanged.connect(lambda text: setattr(self, 'ip', text))

    # Connect Button
    add_connection_button = QPushButton("+")
    add_connection_button.setStyleSheet("font-size: 12px;")
    add_connection_button.setCursor(Qt.CursorShape.PointingHandCursor)
    add_connection_button.clicked.connect(self.start_watching)

    # Adding widgets to top bar right side
    top_bar.addWidget(self.ip_input)
    top_bar.addWidget(add_connection_button)
    top_bar.addWidget(saved_ips)

    # ----------------------------------------------------
    # Streams Main Container
    # ----------------------------------------------------

    #TODO: Change layout based on settings

    # Container horizontal principal que vai segurar os blocos
    streams_container = QHBoxLayout()
    streams_container.setSpacing(10)
    streams_container.setContentsMargins(5, 5, 5, 5) 

    # Inicialização limpa das colunas esquerda e direita
    self.main_stream_container = QVBoxLayout()
    self.mini_streams_container = QVBoxLayout()

    # Zera espaçamentos internos para evitar que os vídeos fiquem esmagados ao meio
    self.main_stream_container.setSpacing(0)
    self.main_stream_container.setContentsMargins(0, 0, 0, 0)
    self.mini_streams_container.setSpacing(10)
    self.mini_streams_container.setContentsMargins(0, 0, 0, 0)

    # Distribui as proporções horizontais (4 partes para a esquerda, 1 parte para a direita)
    streams_container.addLayout(self.main_stream_container, 4)
    streams_container.addLayout(self.mini_streams_container, 1)

    main_layout.addLayout(top_bar)
    main_layout.addLayout(streams_container, 1) 
    
    central_widget.setLayout(main_layout)

  # ----------------------------------------------------
  # Hosting Functions
  # ----------------------------------------------------
  def host(self):
    global IS_HOSTING
    IS_HOSTING = not IS_HOSTING

    if IS_HOSTING:
      threading.Thread(target=self.run_server_thread, daemon=True).start()
      self.host_button.setText(lang["MAIN_SCREEN"]["STOP_HOSTING"])
      self.host_button.setStyleSheet("#HostButton { background-color: #d9534f; color: white; font-weight: bold; } #HostButton:hover { background-color: #d22f2d }")
    else:
      self.host_button.setText("Host")
      self.host_button.setStyleSheet("#HostButton { background-color: #666; color: white; font-weight: bold; } #HostButton:hover { background-color: #888 }")

  def run_server_thread(self):
    asyncio.run(self.server_main())

  async def broadcast_screen(self):
    from pynput.mouse import Controller as MouseController
    import mss  
    global IS_HOSTING, CONNECTED_CLIENTS, FPS_TARGET_INT, STREAM_TYPE, SELECTED_WEBCAM
    
    mouse = MouseController()

    # Inicializa variáveis da webcam
    webcam_cap = None
    last_webcam_idx = None

    def process_frame(raw_frame, m_x, m_y, monitor_info, is_webcam=False, offset_x=0, offset_y=0, raw_webcam=None):
      global SHOW_CURSOR, WEBCAM_WIDTH, WEBCAM_HEIGHT, WEBCAM_DEFAULT_POS, WEBCAM_DEFAULT_POS_ENABLED, WEBCAM_X, WEBCAM_Y
      if raw_frame is None:
        return None
          
      frame = np.array(raw_frame, dtype=np.uint8)
      
      # MSS captura em BGRA, Webcam captura em BGR
      if not is_webcam:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

      # Desenha o cursor apenas se estiver transmitindo a tela inteira
      if SHOW_CURSOR and not is_webcam:
        m_x_rel = m_x - monitor_info["left"] - offset_x
        m_y_rel = m_y - monitor_info["top"] - offset_y

        # Garante que o desenho aconteça apenas se o mouse estiver dentro da janela transmitida
        if 0 <= m_x_rel < frame.shape[1] and 0 <= m_y_rel < frame.shape[0]:
          cursor_pts = np.array([
            [m_x_rel, m_y_rel],
            [m_x_rel + 15, m_y_rel + 15],
            [m_x_rel + 5, m_y_rel + 17]
          ], np.int32)
          
          cv2.fillPoly(frame, [cursor_pts], (255, 255, 255))
          cv2.polylines(frame, [cursor_pts], True, (0, 0, 0), 1)

      if raw_webcam is not None:
        global WEBCAM_ON_STREAM_SIZE

        # Webcam size
        screen_h, screen_w, _ = frame.shape

        # Webcam_w = WEBCAM OVERLAY SIZE
        webcam_w = int((screen_w * WEBCAM_ON_STREAM_SIZE))
        webcam_h = int(raw_webcam.shape[0] * (webcam_w / raw_webcam.shape[1]))

        WEBCAM_WIDTH, WEBCAM_HEIGHT = webcam_w, webcam_h
        
        try:
          # Webcam positioning and resizing
          webcam_resized = cv2.resize(raw_webcam, (webcam_w, webcam_h))
        except cv2.error:
          pass

        # Webcam BORDER SPACING
        margin = 10

        #TODO inverse webcam option
        x_offset, y_offset = margin, margin

        if WEBCAM_DEFAULT_POS_ENABLED:
          match WEBCAM_DEFAULT_POS:
            case 0:
              # Superior Esquerda
              x_offset = margin
              y_offset = margin
            case 1:
              # Superior Direita
              x_offset = screen_w - webcam_w - margin
              y_offset = margin
            case 2:
              # Inferior Esquerda
              x_offset = margin
              y_offset = screen_h - webcam_h - margin
            case 3:
              # Inferior Direita
              x_offset = screen_w - webcam_w - margin
              y_offset = screen_h - webcam_h - margin
        else:
          # Caso posicionamento Custom esteja ativo
          x_offset = WEBCAM_X
          y_offset = WEBCAM_Y
        
        try:
          frame[y_offset:y_offset+webcam_h, x_offset:x_offset+webcam_w] = webcam_resized
        except (ValueError, cv2.error):
          pass

      global STREAM_RES
      frame = cv2.resize(frame, (int(STREAM_RES[0]), int(STREAM_RES[1])))
      _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
      return buffer.tobytes()

    loop = asyncio.get_running_loop()

    with mss.mss() as sct:
      global SELECTED_MONITOR, WEBCAM_ON_STREAM

      while IS_HOSTING:
        monitor = sct.monitors[1:][SELECTED_MONITOR]
        start_time = loop.time()

        if CONNECTED_CLIENTS:
          data = None
          
          # Retornar dados da Webcam caso overlay esteja ativo.
          def webcam_to_pass():
            global SELECTED_WEBCAM, WEBCAM_CROP_ENABLED, W_CROP_TOP, W_CROP_BOTTOM, W_CROP_RIGHT, W_CROP_LEFT
            nonlocal webcam_cap, last_webcam_idx
            try:
              current_idx = int(SELECTED_WEBCAM.split(" ")[1]) if (SELECTED_WEBCAM and "Camera" in SELECTED_WEBCAM) else 0
            except Exception:
              current_idx = 0

            if webcam_cap is None or last_webcam_idx != current_idx:
              if webcam_cap is not None:
                webcam_cap.release()

              webcam_cap = cv2.VideoCapture(current_idx)
              last_webcam_idx = current_idx

            ret, webcam_frame = webcam_cap.read()
            if WEBCAM_CROP_ENABLED and ret and webcam_frame is not None:
              h, w, _ = webcam_frame.shape
  
              start_y = int(h * W_CROP_TOP)
              end_y = int(h * (1.0 - W_CROP_BOTTOM))
              start_x = int(w * W_CROP_LEFT)
              end_x = int(w * (1.0 - W_CROP_RIGHT))
              
              # Aplica o fatiamento de matriz (Garante formato válido contra cortes excessivos)
              if end_y > start_y and end_x > start_x:
                webcam_frame = webcam_frame[start_y:end_y, start_x:end_x]
                  
              return webcam_frame

            webcam_to_pass = webcam_frame if ret else None
            return webcam_to_pass

          # MODO 0: Escolha o tipo (Não transmite nada)
          if STREAM_TYPE == 0:
            if webcam_cap is not None:
              webcam_cap.release()
              webcam_cap = None
              last_webcam_idx = None
            await asyncio.sleep(0.1)
            continue

          # MODO 1: Captura de Tela Inteira (MSS)
          elif STREAM_TYPE == 1:
            if webcam_cap is not None:
              webcam_cap.release()
              webcam_cap = None
              last_webcam_idx = None
                
            sct_img = sct.grab(monitor)
            m_x, m_y = mouse.position

            data = await loop.run_in_executor(
              None, process_frame, sct_img, m_x, m_y, monitor, False, 0, 0, None if not WEBCAM_ON_STREAM else webcam_to_pass()
            )

          # MODO 2: Captura de Janela Fixa Específica (ATUALIZADO!)
          elif STREAM_TYPE == 2:
            if webcam_cap is not None:
              webcam_cap.release()
              webcam_cap = None
              last_webcam_idx = None

            try:
              global SELECTED_WINDOW_TITLE
              win = None
              
              # Se o usuário escolheu uma janela nas configurações, busca ela pelo título exato
              if SELECTED_WINDOW_TITLE and SELECTED_WINDOW_TITLE != "None" or SELECTED_WINDOW_TITLE and SELECTED_WINDOW_TITLE != "Nenhuma":
                windows = gw.getWindowsWithTitle(SELECTED_WINDOW_TITLE)
                if windows and len(windows) > 0:
                  win = windows[0]  # Pega a primeira janela correspondente encontrada
              
              # Se não houver janela salva ou ela foi fechada, recorre à janela ativa como backup
              if win is None:
                win = gw.getActiveWindow()

              if win and win.width > 10 and win.height > 10:
                # Se a janela estiver minimizada, avisa no console ou pula o frame
                if win.isMinimized:
                  await asyncio.sleep(0.05)
                  continue

                region = {
                  "top": win.top,
                  "left": win.left,
                  "width": win.width,
                  "height": win.height
                }
                sct_img = sct.grab(region)
                m_x, m_y = mouse.position
                
                offset_x = win.left - monitor["left"]
                offset_y = win.top - monitor["top"]

                data = await loop.run_in_executor(
                  None, process_frame, sct_img, m_x, m_y, monitor, False, offset_x, offset_y, None if not WEBCAM_ON_STREAM else webcam_to_pass()
                )
              else:
                await asyncio.sleep(0.05)
                continue
            except Exception:
              await asyncio.sleep(0.05)
              continue

          # MODO 3: Webcam Apenas
          elif STREAM_TYPE == 3:
            # Determina qual câmera abrir baseado no painel de configurações
            try:
              current_idx = int(SELECTED_WEBCAM.split(" ")[1]) if (SELECTED_WEBCAM and "Camera" in SELECTED_WEBCAM) else 0
            except Exception:
              current_idx = 0

            # Se trocou de câmera ou ela não foi aberta ainda
            if webcam_cap is None or last_webcam_idx != current_idx:
              if webcam_cap is not None:
                webcam_cap.release()

              webcam_cap = cv2.VideoCapture(current_idx)
              last_webcam_idx = current_idx

            ret, webcam_frame = webcam_cap.read()
            if ret:
              data = await loop.run_in_executor(
                None, process_frame, webcam_frame, 0, 0, None, True
              )

          # Envia o buffer correspondente gerado pelo modo ativo
          if data:
            tasks = [asyncio.create_task(client.send(data)) for client in CONNECTED_CLIENTS]
            if tasks:
              await asyncio.wait(tasks)

        # Controle rígido de FPS
        elapsed_time = loop.time() - start_time
        TARGET_FPS = FPS_TARGET_INT
        FRAME_DURATION = 1.0 / TARGET_FPS 
        sleep_time = max(0, FRAME_DURATION - elapsed_time)
        await asyncio.sleep(sleep_time)

      # Limpeza ao fechar o Host
      if webcam_cap is not None:
        webcam_cap.release()

  async def server_main(self):
    async with websockets.serve(self.server_register, "0.0.0.0", DEFAULT_PORT, ping_interval=None):
      await self.broadcast_screen()

  async def server_register(self, websocket):
    global CONNECTED_CLIENTS
    CONNECTED_CLIENTS.add(websocket)
    try:
      await websocket.wait_closed()
    finally:
      CONNECTED_CLIENTS.remove(websocket)

  # ----------------------------------------------------
  # Watch Functions
  # ----------------------------------------------------
  def start_watching(self):
    if not self.ip:
      return
    ip = self.ip.strip()
    if ip in self.active_streams:
      return

    # Cria e posiciona o painel de vídeo
    new_screen = VideoStream(ip, self.handle_close_request, self.toggle_focus_stream)
    self.active_streams[ip] = new_screen
    self.update_layout_view()
    
    # Dispara a thread de rede em segundo plano
    threading.Thread(target=self.run_watch_thread, args=(ip,), daemon=True).start()
    
    self.ip_input.clear()
    self.ip = ""

  def handle_close_request(self, ip):
    self.remove_stream_signal.emit(ip)
  
  @pyqtSlot(str)
  def close_stream(self, ip):
    if ip in self.active_streams:
      if self.focused_ip == ip:
        self.focused_ip = None

      widget = self.active_streams[ip]
      self.main_stream_container.removeWidget(widget)
      widget.setParent(None)
      widget.deleteLater()
      del self.active_streams[ip]
      self.update_layout_view()
  
  def toggle_focus_stream(self, ip):
    self.focused_ip = None if self.focused_ip == ip else ip
    self.update_layout_view()

  def update_layout_view(self):
    """Limpa as duas colunas e redistribui as streams de forma inteligente."""
    # Remove temporariamente os widgets das colunas sem destruí-los
    for ip, widget in list(self.active_streams.items()):
      self.main_stream_container.removeWidget(widget)
      self.mini_streams_container.removeWidget(widget)
      widget.hide()

    # Captura os IPs ativos
    lista_ips = list(self.active_streams.keys())
    
    if not lista_ips:
      return

    # Decide quem vai para o espaço grande da esquerda
    if self.focused_ip and self.focused_ip in self.active_streams:
      ip_principal = self.focused_ip
    else:
      ip_principal = lista_ips[0] # Agora é 100% seguro acessar o índice 0

    # Envia o vídeo principal com destaque para a esquerda
    widget_principal = self.active_streams[ip_principal]
    self.main_stream_container.addWidget(widget_principal)
    widget_principal.show()
    widget_principal.resize_frame()

    # Empilha os vídeos restantes na barra lateral direita
    for ip in lista_ips:
      if ip != ip_principal:
        widget_mini = self.active_streams[ip]
        self.mini_streams_container.addWidget(widget_mini)
        widget_mini.show()
        widget_mini.resize_frame()

  def run_watch_thread(self, ip):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
      loop.run_until_complete(self.receive_stream(ip))
    except Exception:
      pass

  async def receive_stream(self, ip):
    global DEFAULT_PORT
    uri = f"ws://{ip}:{DEFAULT_PORT}"
    is_connected = False
    try:
      async with websockets.connect(uri, ping_interval=None) as websocket:
        is_connected = True # Conexão feita com sucesso!
        while ip in self.active_streams:
          data = await websocket.recv()
          
          # Limpeza de buffer de rede para evitar atrasos a 60 FPS
          try:
            while True:
              data = await asyncio.wait_for(websocket.recv(), timeout=0.001)
          except asyncio.TimeoutError:
            pass
          
          np_arr = np.frombuffer(data, dtype=np.uint8)
          frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
          if frame is None:
            continue
          
          frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          height, width, channel = frame.shape
          bytes_per_line = channel * width
          q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()
          
          self.update_image_signal.emit(ip, q_img)
    except Exception as e:
      print(f"Não foi possível conectar ao host {ip} (O Host está ligado?): {e}")
    finally:
      if is_connected:
        self.handle_close_request(ip)
      else:
        self.remove_stream_signal.emit(ip)
    
  @pyqtSlot(str, QImage)
  def dispatch_frame(self, ip, q_img):
    if ip in self.active_streams:
      self.active_streams[ip].update_frame(q_img)

  # ----------------------------------------------------
  # Other Functions
  # ----------------------------------------------------
  def stream_type(self, stream_type_idx):
    global STREAM_TYPE
    STREAM_TYPE = stream_type_idx
    print("Activated", STREAM_TYPE)

  def on_test_button_click(self):
    #print("Hello World!")
    global test_var
    print(test_var)
    test_var = "olá"
    print(test_var)

  def stream_add(self):
    print(self.ip)
    self.ip_input.clear()

  def show_hosting_settings(self):
    self.settings_window = SettingsWindow()
    self.settings_window.show()

  def show_webcam_settings(self):
    self.webcam_settings_window = WebcamSettingsWindow()
    self.webcam_settings_window.show()

  def show_saved_ips(self):
    self.saved_ips_window = SavedConnections()
    self.saved_ips_window.show()

  def my_ip(self):
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8", 80))
      ip = s.getsockname()[0]
      s.close()
      return ip
    except Exception:
      return "127.0.0.1"

# ----------------------------------------------------
# Settings Window
# ----------------------------------------------------
class SettingsWindow(QWidget):
  def __init__(self):
    super().__init__()
    self.setObjectName("SettingsWidget")
    self.screen_width, self.screen_height = pyautogui.size()
    self.app_width, self.app_height = (round(self.screen_width*0.35), round(self.screen_height*0.55))

    self.setWindowTitle(lang["HOST_SETTINGS"]["HOST_SETTINGS_TITLE"])
    self.setGeometry(self.screen_width//2-self.app_width//2, self.screen_height//2-self.app_height//2, self.app_width, self.app_height)
    
    # Global styles
    self.setStyleSheet("""
      #SettingsWidget { background-color: #262626; }
      QLabel { color: white; font-size: 14px; }
      QLineEdit { background-color: #333; color: white; border: 1px solid #555; padding: 4px; border-radius: 4px; }
      QPushButton { background-color: #444; color: white; border: None; padding: 6px 12px; border-radius: 4px; }
      QComboBox { background-color: #444; color: white; border: None; padding: 6px 8px; border-radius: 4px; }
      QPushButton:hover { background-color: #555; }
      QCheckBox { color: white; font-size: 14px; }
    """)

    # Main Layout (Vertical)
    main_layout = QVBoxLayout()
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    main_layout.setSpacing(15)

    # Title
    """
    self.label = QLabel("Settings")
    self.label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
    main_layout.addWidget(self.label)"""

    # ----------------------------------------------------
    # Setting 1: Connection Port
    # ----------------------------------------------------
    global DEFAULT_PORT
    row1_layout = QHBoxLayout()
    
    row1_label = QLabel(lang["HOST_SETTINGS"]["SERVER_PORT"])
    self.connection_port = QLineEdit()
    #self.connection_port.setPlaceholderText(f"Default {DEFAULT_PORT}")
    self.connection_port.setText(str(DEFAULT_PORT))
    self.connection_port.setFixedWidth(100)
    
    row1_layout.addWidget(row1_label)
    row1_layout.addStretch()
    row1_layout.addWidget(self.connection_port)
    
    main_layout.addLayout(row1_layout)

    # ----------------------------------------------------
    # Setting 2: Stream FPS
    # ----------------------------------------------------
    global IDX_FPS_TARGET
    stream_fps_layout = QHBoxLayout()
    
    row2_label = QLabel(lang["HOST_SETTINGS"]["STREAM_FPS"])
    self.fps_combobox = QComboBox()
    self.fps_combobox.addItems([lang["HOST_SETTINGS"]["FPS_OPTIONS"]["0"],
                                lang["HOST_SETTINGS"]["FPS_OPTIONS"]["1"],
                                lang["HOST_SETTINGS"]["FPS_OPTIONS"]["2"],
                                lang["HOST_SETTINGS"]["FPS_OPTIONS"]["3"],
                                lang["HOST_SETTINGS"]["FPS_OPTIONS"]["4"],
                                lang["HOST_SETTINGS"]["FPS_OPTIONS"]["5"],
                                lang["HOST_SETTINGS"]["FPS_OPTIONS"]["6"],
                                lang["HOST_SETTINGS"]["FPS_OPTIONS"]["7"]])
    self.fps_combobox.setCurrentIndex(IDX_FPS_TARGET)
    
    stream_fps_layout.addWidget(row2_label)
    stream_fps_layout.addStretch()
    stream_fps_layout.addWidget(self.fps_combobox)
    
    main_layout.addLayout(stream_fps_layout)

    # ----------------------------------------------------
    # Setting 3: Stream FPS
    # ----------------------------------------------------
    global STREAM_RES
    stream_res_layout = QHBoxLayout()
    stream_res_label = QLabel(lang["HOST_SETTINGS"]["RESOLUTION"])
    self.stream_res_width = QLineEdit()
    self.stream_res_width.setPlaceholderText(lang["HOST_SETTINGS"]["RESOLUTION_WIDTH_PLACEHOLDER"])
    self.stream_res_width.setFixedWidth(80)
    self.stream_res_width.setText(str(STREAM_RES[0]))
    stream_res_label2 = QLabel("X")
    self.stream_res_height = QLineEdit()
    self.stream_res_height.setPlaceholderText(lang["HOST_SETTINGS"]["RESOLUTION_HEIGHT_PLACEHOLDER"])
    self.stream_res_height.setFixedWidth(80)
    self.stream_res_height.setText(str(STREAM_RES[1]))

    stream_res_layout.addWidget(stream_res_label)
    stream_res_layout.addStretch()
    stream_res_layout.addWidget(self.stream_res_width)
    stream_res_layout.addWidget(stream_res_label2)
    stream_res_layout.addWidget(self.stream_res_height)
    main_layout.addLayout(stream_res_layout)

    # ----------------------------------------------------
    # Setting 4: Show Cursor
    # ----------------------------------------------------
    global SHOW_CURSOR
    cursor_layout = QHBoxLayout()

    cursor_label = QLabel(lang["HOST_SETTINGS"]["SHOW_CURSOR"])
    self.show_cursor_checkbox = QCheckBox()

    self.show_cursor_checkbox.setChecked(True) if SHOW_CURSOR else self.show_cursor_checkbox.setChecked(False)

    cursor_layout.addWidget(cursor_label)
    cursor_layout.addStretch()
    cursor_layout.addWidget(self.show_cursor_checkbox)

    main_layout.addLayout(cursor_layout)

    # ----------------------------------------------------
    # Setting 5: Specific Window
    # ----------------------------------------------------
    global SELECTED_WINDOW_TITLE
    specific_window_layout = QHBoxLayout()
    specific_window_label = QLabel(lang["HOST_SETTINGS"]["WINDOWS_TO_STREAM"])
    self.specific_window_combobox = QComboBox()
    
    # Coleta todos os títulos de janelas abertas e filtra strings vazias do Windows
    raw_titles = gw.getAllTitles()
    filtered_titles = [lang["HOST_SETTINGS"]["WINDOWS_TO_STREAM_DEFAULT"]] + [t for t in raw_titles if t.strip()]
    self.specific_window_combobox.addItems(filtered_titles)
    
    # Restaura a seleção anterior se houver
    if SELECTED_WINDOW_TITLE:
      idx_win = self.specific_window_combobox.findText(SELECTED_WINDOW_TITLE)
      if idx_win >= 0: self.specific_window_combobox.setCurrentIndex(idx_win)

    specific_window_layout.addWidget(specific_window_label)
    specific_window_layout.addStretch()
    specific_window_layout.addWidget(self.specific_window_combobox)
    main_layout.addLayout(specific_window_layout)

    # ----------------------------------------------------
    # Setting 6: Monitor
    # ----------------------------------------------------
    global SELECTED_MONITOR
    monitor_layout = QHBoxLayout()
    monitor_label = QLabel(lang["HOST_SETTINGS"]["MONITOR"])
    self.monitor_combobox = QComboBox()
    monitors = mss.mss().monitors[1:]

    for idx, monitor in enumerate(monitors, start=1):
      self.monitor_combobox.addItem(f"Monitor {idx}: {monitor['width']}x{monitor['height']}")

    print(self.monitor_combobox.currentIndex())

    monitor_layout.addWidget(monitor_label)
    monitor_layout.addStretch()
    monitor_layout.addWidget(self.monitor_combobox)
    main_layout.addLayout(monitor_layout)

    # ----------------------------------------------------
    # Setting 6: Selected Language
    # ----------------------------------------------------
    language_layout = QHBoxLayout()
    language_label = QLabel(lang["HOST_SETTINGS"]["LANGUAGES"])
    self.languages =  QComboBox()
    self.languages.addItems(["ENG", "BR"])
    current_language = config_software["LANGUAGE"]
    idx_language = 0
    match current_language:
      case "ENG":idx_language = 0
      case "BR":idx_language = 1
    self.languages.setCurrentIndex(idx_language)

    language_layout.addWidget(language_label)
    language_layout.addStretch()
    language_layout.addWidget(self.languages)
    main_layout.addLayout(language_layout)

    # ----------------------------------------------------
    # Update button
    # ----------------------------------------------------
    main_layout.addStretch()

    update_button = QPushButton(lang["HOST_SETTINGS"]["SAVE_SETTINGS_BUTTON"])
    update_button.setCursor(Qt.CursorShape.PointingHandCursor)
    update_button.clicked.connect(self.update_settings)

    main_layout.addWidget(update_button, alignment=Qt.AlignmentFlag.AlignCenter)

    # Aplica o layout principal na janela
    self.setLayout(main_layout)

  def update_settings(self):
    global DEFAULT_PORT, IDX_FPS_TARGET, STREAM_RES, SHOW_CURSOR, IDX_FPS_TARGET, FPS_TARGET_INT, FPS_OPTIONS, SELECTED_WINDOW_TITLE, SELECTED_MONITOR
    global config, config_host
    def debug_settings(old_Values=True):
      print(
        f"- Old:\n" if old_Values else f"- New:\n",
        f"Port: {DEFAULT_PORT}\n",
        f"FPS: {self.fps_combobox.itemText(IDX_FPS_TARGET)}, {IDX_FPS_TARGET}\n",
        f"Stream Res: {int(self.stream_res_width.text())}x{int(self.stream_res_height.text())}"
        f"Cursor: {SHOW_CURSOR}\n",
        f"Selected Window: {SELECTED_WINDOW_TITLE}\n",
        f"Monitor Index: {SELECTED_MONITOR}\n",
        f"Language: {self.languages.currentText()}"
      )
    debug_settings(old_Values=True)
    print(f"- Updating...\n")
    DEFAULT_PORT = self.connection_port.text()
    IDX_FPS_TARGET = self.fps_combobox.currentIndex()
    FPS_TARGET_INT = FPS_OPTIONS[IDX_FPS_TARGET]
    STREAM_RES = (int(self.stream_res_width.text()), int(self.stream_res_height.text()))
    SHOW_CURSOR = self.show_cursor_checkbox.isChecked()
    SELECTED_WINDOW_TITLE = self.specific_window_combobox.currentText()
    SELECTED_MONITOR = self.monitor_combobox.currentIndex()
    debug_settings(old_Values=False)

    config_host["DEFAULT_PORT"] = str(self.connection_port.text())
    config_host["IDX_FPS_TARGET"] = str(self.fps_combobox.currentIndex())
    config_host["STREAM_RES"] = str((self.stream_res_width.text(), self.stream_res_height.text()))
    config_host["SHOW_CURSOR"] = str(self.show_cursor_checkbox.isChecked())
    config_host["SELECTED_MONITOR"] = str(self.monitor_combobox.currentIndex())
    config_software["LANGUAGE"] = str(self.languages.currentText())
    with open(config_file_path, "w", encoding="utf-8") as configfile:
      config.write(configfile)

# ----------------------------------------------------
# Webcam Settings Window
# ----------------------------------------------------
class WebcamSettingsWindow(QWidget):
  def __init__(self):
    super().__init__()
    self.setObjectName("WebcamSettingsWidget")
    self.screen_width, self.screen_height = pyautogui.size()
    self.app_width, self.app_height = (round(self.screen_width*0.45), round(self.screen_height*0.75))

    self.setWindowTitle(lang["WEBCAM_SETTINGS"]["WEBCAM_SETTINGS_TITLE"])
    self.setGeometry(self.screen_width//2-self.app_width//2, self.screen_height//2-self.app_height//2, self.app_width, self.app_height)
    
    # Global styles
    self.setStyleSheet("""
        #WebcamSettingsWidget { background-color: #262626; }
        QLabel { color: white; font-size: 14px; }
        QLineEdit { background-color: #333; color: white; border: 1px solid #555; padding: 4px; border-radius: 4px; }
        QPushButton { background-color: #444; color: white; border: None; padding: 6px 12px; border-radius: 4px; }
        QComboBox { background-color: #444; color: white; border: None; padding: 6px 8px; border-radius: 4px; }
        QPushButton:hover { background-color: #555; }
        QCheckBox { color: white; font-size: 14px; }
    """)

    # Main Layout (Vertical)
    main_layout = QVBoxLayout()
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    main_layout.setSpacing(15) # Vertical spacing between settings

    # Title
    #self.label = QLabel("Webcam")
    #self.label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
    #main_layout.addWidget(self.label)

    # ----------------------------------------------------
    # Setting 1: Webcams
    # ----------------------------------------------------
    global SELECTED_WEBCAM
    row1_layout = QHBoxLayout()
    row3_label = QLabel(lang["WEBCAM_SETTINGS"]["WEBCAMS"])
    self.row1_webcams_combobox = QComboBox()
    
    # Busca e popula o combobox com as câmeras ativas via enumerador
    try:
      cameras = cv2_ec.enumerate_cameras()
      camera_items = [f"Camera {cam.index}: {cam.name}" for cam in cameras]
      if not camera_items:
        camera_items = ["None"]
    except Exception:
      camera_items = ["Camera 0", "None"]
        
    self.row1_webcams_combobox.addItems(camera_items)
    
    # Mantém selecionada a câmera configurada anteriormente
    if SELECTED_WEBCAM:
      idx = self.row1_webcams_combobox.findText(SELECTED_WEBCAM)
      if idx >= 0:
        self.row1_webcams_combobox.setCurrentIndex(idx)

    row1_layout.addWidget(row3_label)
    row1_layout.addStretch()
    row1_layout.addWidget(self.row1_webcams_combobox)
    main_layout.addLayout(row1_layout)

    # ----------------------------------------------------
    # Setting 2: Webcam on Stream
    # ----------------------------------------------------
    global WEBCAM_ON_STREAM, WEBCAM_ON_STREAM_SIZE
    row2_layout = QHBoxLayout()
    row2_label = QLabel(lang["WEBCAM_SETTINGS"]["WEBCAM_ON_STREAM_AND_SIZE"])
    self.row2_checkbox = QCheckBox()
    self.row2_checkbox.setChecked(WEBCAM_ON_STREAM)

    self.row2_slider = QSlider(Qt.Orientation.Horizontal)
    self.row2_slider.setRange(0, 100)
    self.row2_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    self.row2_slider.setTickInterval(11)
    self.row2_slider.setValue(int(WEBCAM_ON_STREAM_SIZE * 100))
    self.row2_slider.setSingleStep(1)
    self.row2_slider.setFixedWidth(200)
    self.row2_slider.valueChanged.connect(self.set_webcam_overlay_size)

    row2_layout.addWidget(row2_label)
    row2_layout.addStretch()
    row2_layout.addWidget(self.row2_checkbox)
    row2_layout.addWidget(self.row2_slider)

    main_layout.addLayout(row2_layout)

    # ----------------------------------------------------
    # Setting 3: Webcam Default Corner Positions
    # ----------------------------------------------------
    global WEBCAM_DEFAULT_POS_ENABLED, WEBCAM_DEFAULT_POS

    row3_layout = QHBoxLayout()
    row3_label = QLabel(lang["WEBCAM_SETTINGS"]["SNAP_TO_CORNER"])
    self.row3_checkbox = QCheckBox()
    self.row3_checkbox.setChecked(WEBCAM_DEFAULT_POS_ENABLED)
    self.row3_combobox_positions = QComboBox()
    self.row3_combobox_positions.addItems([lang["WEBCAM_SETTINGS"]["UPPER_LEFT"], lang["WEBCAM_SETTINGS"]["UPPER_RIGHT"], lang["WEBCAM_SETTINGS"]["LOWER_LEFT"], lang["WEBCAM_SETTINGS"]["LOWER_RIGHT"]])

    row3_layout.addWidget(row3_label)
    row3_layout.addStretch()
    row3_layout.addWidget(self.row3_checkbox)
    row3_layout.addWidget(self.row3_combobox_positions)

    main_layout.addLayout(row3_layout)

    # ----------------------------------------------------
    # Setting 4: Custom POS X
    # ----------------------------------------------------
    global WEBCAM_X

    row4_layout = QHBoxLayout()
    row4_layout.setSpacing(5)
    row4_label = QLabel(lang["WEBCAM_SETTINGS"]["POSITION_X"])
    row4_minus_100 = QPushButton("-100")
    row4_minus_10 = QPushButton("-10")
    row4_minus_1 = QPushButton("-1")
    self.row4_current_x = QLabel(str(WEBCAM_X))
    row4_plus_1 = QPushButton("+1")
    row4_plus_10 = QPushButton("+10")
    row4_plus_100 = QPushButton("+100")

    row4_minus_100.setCursor(Qt.CursorShape.PointingHandCursor)
    row4_minus_10.setCursor(Qt.CursorShape.PointingHandCursor)
    row4_minus_1.setCursor(Qt.CursorShape.PointingHandCursor)
    row4_plus_1.setCursor(Qt.CursorShape.PointingHandCursor)
    row4_plus_10.setCursor(Qt.CursorShape.PointingHandCursor)
    row4_plus_100.setCursor(Qt.CursorShape.PointingHandCursor)

    row4_minus_100.clicked.connect(lambda: self.change_webcam_pos("X", -100))
    row4_minus_10.clicked.connect(lambda: self.change_webcam_pos("X", -10))
    row4_minus_1.clicked.connect(lambda: self.change_webcam_pos("X", -1))
    row4_plus_1.clicked.connect(lambda: self.change_webcam_pos("X", 1))
    row4_plus_10.clicked.connect(lambda: self.change_webcam_pos("X", 10))
    row4_plus_100.clicked.connect(lambda: self.change_webcam_pos("X", 100))

    row4_layout.addWidget(row4_label)
    row4_layout.addStretch()
    row4_layout.addWidget(row4_minus_100)
    row4_layout.addWidget(row4_minus_10)
    row4_layout.addWidget(row4_minus_1)
    row4_layout.addWidget(self.row4_current_x)
    row4_layout.addWidget(row4_plus_1)
    row4_layout.addWidget(row4_plus_10)
    row4_layout.addWidget(row4_plus_100)

    main_layout.addLayout(row4_layout)

    # ----------------------------------------------------
    # Setting 5: Custom POS Y
    # ----------------------------------------------------
    global WEBCAM_Y
    
    row5_layout = QHBoxLayout()
    row5_layout.setSpacing(5)
    row5_label = QLabel(lang["WEBCAM_SETTINGS"]["POSITION_Y"])
    row5_minus_100 = QPushButton("-100")
    row5_minus_10 = QPushButton("-10")
    row5_minus_1 = QPushButton("-1")
    self.row5_current_y = QLabel(str(WEBCAM_Y))
    row5_plus_1 = QPushButton("+1")
    row5_plus_10 = QPushButton("+10")
    row5_plus_100 = QPushButton("+100")

    row5_minus_100.setCursor(Qt.CursorShape.PointingHandCursor)
    row5_minus_10.setCursor(Qt.CursorShape.PointingHandCursor)
    row5_minus_1.setCursor(Qt.CursorShape.PointingHandCursor)
    row5_plus_1.setCursor(Qt.CursorShape.PointingHandCursor)
    row5_plus_10.setCursor(Qt.CursorShape.PointingHandCursor)
    row5_plus_100.setCursor(Qt.CursorShape.PointingHandCursor)

    row5_minus_100.clicked.connect(lambda: self.change_webcam_pos("Y", -100))
    row5_minus_10.clicked.connect(lambda: self.change_webcam_pos("Y", -10))
    row5_minus_1.clicked.connect(lambda: self.change_webcam_pos("Y", -1))
    row5_plus_1.clicked.connect(lambda: self.change_webcam_pos("Y", 1))
    row5_plus_10.clicked.connect(lambda: self.change_webcam_pos("Y", 10))
    row5_plus_100.clicked.connect(lambda: self.change_webcam_pos("Y", 100))

    row5_layout.addWidget(row5_label)
    row5_layout.addStretch()
    row5_layout.addWidget(row5_minus_100)
    row5_layout.addWidget(row5_minus_10)
    row5_layout.addWidget(row5_minus_1)
    row5_layout.addWidget(self.row5_current_y)
    row5_layout.addWidget(row5_plus_1)
    row5_layout.addWidget(row5_plus_10)
    row5_layout.addWidget(row5_plus_100)

    main_layout.addLayout(row5_layout)

    # ----------------------------------------------------
    # Setting 7: Enable / Disable Crop
    # ----------------------------------------------------
    global WEBCAM_CROP_ENABLED, W_CROP_RIGHT, W_CROP_LEFT
    row7_layout = QHBoxLayout()
    row7_label = QLabel(lang["WEBCAM_SETTINGS"]["ENABLE_CROPPING"])
    self.row7_checkbox = QCheckBox()
    self.row7_checkbox.setChecked(WEBCAM_CROP_ENABLED)
    self.row7_checkbox.clicked.connect(self.enable_crop)

    row7_layout.addWidget(row7_label)
    row7_layout.addStretch()
    row7_layout.addWidget(self.row7_checkbox)
    main_layout.addLayout(row7_layout)

    # ----------------------------------------------------
    # Setting 8: Crop Top
    # ----------------------------------------------------
    global W_CROP_TOP
    row8_layout = QHBoxLayout()
    row8_label = QLabel(lang["WEBCAM_SETTINGS"]["CROP_TOP"])
    self.row8_slider = QSlider(Qt.Orientation.Horizontal)
    self.row8_slider.setRange(0, 100)
    self.row8_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    self.row8_slider.setTickInterval(11)
    self.row8_slider.setValue(int(W_CROP_TOP*100))
    self.row8_slider.setSingleStep(1)
    self.row8_slider.setFixedWidth(300)
    self.row8_slider.valueChanged.connect(self.set_crop_top)

    row8_layout.addWidget(row8_label)
    row8_layout.addStretch()
    row8_layout.addWidget(self.row8_slider)
    main_layout.addLayout(row8_layout)

    # ----------------------------------------------------
    # Setting 9: Crop Bottom
    # ----------------------------------------------------
    global W_CROP_BOTTOM
    row9_layout = QHBoxLayout()
    row9_label = QLabel(lang["WEBCAM_SETTINGS"]["CROP_BOTTOM"])
    self.row9_slider = QSlider(Qt.Orientation.Horizontal)
    self.row9_slider.setRange(0, 100)
    self.row9_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    self.row9_slider.setTickInterval(11)
    self.row9_slider.setValue(int(W_CROP_BOTTOM*100))
    self.row9_slider.setSingleStep(1)
    self.row9_slider.setFixedWidth(300)
    self.row9_slider.valueChanged.connect(self.set_crop_bottom)

    row9_layout.addWidget(row9_label)
    row9_layout.addStretch()
    row9_layout.addWidget(self.row9_slider)
    main_layout.addLayout(row9_layout)

    # ----------------------------------------------------
    # Setting 10: Crop Left
    # ----------------------------------------------------
    global W_CROP_LEFT
    row10_layout = QHBoxLayout()
    row10_label = QLabel(lang["WEBCAM_SETTINGS"]["CROP_LEFT"])
    self.row10_slider = QSlider(Qt.Orientation.Horizontal)
    self.row10_slider.setRange(0, 100)
    self.row10_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    self.row10_slider.setTickInterval(11)
    self.row10_slider.setValue(int(W_CROP_LEFT*100))
    self.row10_slider.setSingleStep(1)
    self.row10_slider.setFixedWidth(300)
    self.row10_slider.valueChanged.connect(self.set_crop_left)

    row10_layout.addWidget(row10_label)
    row10_layout.addStretch()
    row10_layout.addWidget(self.row10_slider)
    main_layout.addLayout(row10_layout)

    # ----------------------------------------------------
    # Setting 11: Crop Right
    # ----------------------------------------------------
    global W_CROP_RIGHT
    row11_layout = QHBoxLayout()
    row11_label = QLabel(lang["WEBCAM_SETTINGS"]["CROP_RIGHT"])
    self.row11_slider = QSlider(Qt.Orientation.Horizontal)
    self.row11_slider.setRange(0, 100)
    self.row11_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    self.row11_slider.setTickInterval(11)
    self.row11_slider.setValue(int(W_CROP_RIGHT*100))
    self.row11_slider.setSingleStep(1)
    self.row11_slider.setFixedWidth(300)
    self.row11_slider.valueChanged.connect(self.set_crop_right)

    row11_layout.addWidget(row11_label)
    row11_layout.addStretch()
    row11_layout.addWidget(self.row11_slider)
    main_layout.addLayout(row11_layout)

    # ----------------------------------------------------
    # Update button
    # ----------------------------------------------------
    main_layout.addStretch()

    update_button = QPushButton(lang["HOST_SETTINGS"]["SAVE_SETTINGS_BUTTON"])
    update_button.setCursor(Qt.CursorShape.PointingHandCursor)
    update_button.clicked.connect(self.update_settings)

    main_layout.addWidget(update_button, alignment=Qt.AlignmentFlag.AlignCenter)

    # Aplica o layout principal na janela
    self.setLayout(main_layout)

  def enable_crop(self):
    global WEBCAM_CROP_ENABLED
    WEBCAM_CROP_ENABLED = self.row7_checkbox.isChecked()

  def set_webcam_overlay_size(self):
    global WEBCAM_ON_STREAM_SIZE
    WEBCAM_ON_STREAM_SIZE = self.row2_slider.value() / 100

  def set_crop_top(self):
    global W_CROP_TOP
    W_CROP_TOP = self.row8_slider.value() / 100

  def set_crop_bottom(self):
    global W_CROP_BOTTOM
    W_CROP_BOTTOM = self.row9_slider.value() / 100

  def set_crop_left(self):
    global W_CROP_LEFT
    W_CROP_LEFT = self.row10_slider.value() / 100

  def set_crop_right(self):
    global W_CROP_RIGHT
    W_CROP_RIGHT = self.row11_slider.value() / 100

  def change_webcam_pos(self, direction:str, value:int):
    global WEBCAM_WIDTH, WEBCAM_HEIGHT, WEBCAM_X, WEBCAM_Y, screen_width, screen_height
    if direction == "X":
      temp = WEBCAM_X + value
      WEBCAM_X = WEBCAM_X + value if temp >= 0 and temp <= screen_width - WEBCAM_WIDTH else WEBCAM_X
      self.row4_current_x.setText(str(WEBCAM_X))
    else:
      temp = WEBCAM_Y + value
      WEBCAM_Y = WEBCAM_Y + value if temp >= 0 and temp <= screen_height - WEBCAM_HEIGHT else WEBCAM_Y
      self.row5_current_y.setText(str(WEBCAM_Y))

    print(f"X {WEBCAM_X} | Y {WEBCAM_Y}")

  def update_settings(self):
    global SELECTED_WEBCAM, WEBCAM_ON_STREAM, WEBCAM_ON_STREAM_SIZE, WEBCAM_DEFAULT_POS_ENABLED, WEBCAM_DEFAULT_POS, WEBCAM_X, WEBCAM_Y, WEBCAM_CROP_ENABLED, W_CROP_TOP, W_CROP_BOTTOM, W_CROP_RIGHT, W_CROP_LEFT
    global config, config_webcam

    def debug_settings(old_Values=True):
      print(
        f"- Old:\n" if old_Values else f"- New:\n",
        f"Webcam: {SELECTED_WEBCAM}\n",
        f"Above Stream: {WEBCAM_ON_STREAM}\n",
        f"Corner Cam: {WEBCAM_DEFAULT_POS_ENABLED}\n",
        f"Corner Selected: {WEBCAM_DEFAULT_POS}\n",
        f"Crop Top: {W_CROP_TOP}\n",
        f"Crop Bottom: {W_CROP_BOTTOM}\n",
        f"Crop Left: {W_CROP_LEFT}\n",
        f"Crop Right: {W_CROP_RIGHT}\n",
      )
    debug_settings(old_Values=True)

    print(f"- Updating...\n")
    SELECTED_WEBCAM = self.row1_webcams_combobox.currentText()
    WEBCAM_ON_STREAM = self.row2_checkbox.isChecked()
    WEBCAM_DEFAULT_POS_ENABLED = self.row3_checkbox.isChecked()
    WEBCAM_DEFAULT_POS = self.row3_combobox_positions.currentIndex()
    debug_settings(old_Values=False)

    config_webcam["WEBCAM_ON_STREAM"] = str(self.row2_checkbox.isChecked())
    config_webcam["WEBCAM_ON_STREAM_SIZE"] = str(WEBCAM_ON_STREAM_SIZE)
    config_webcam["WEBCAM_DEFAULT_POS_ENABLED"] = str(self.row3_checkbox.isChecked())
    config_webcam["WEBCAM_DEFAULT_POS"] = str(self.row3_combobox_positions.currentIndex())
    config_webcam["WEBCAM_X"] = str(WEBCAM_X)
    config_webcam["WEBCAM_Y"] = str(WEBCAM_Y)
    config_webcam["WEBCAM_CROP_ENABLED"] = str(WEBCAM_CROP_ENABLED)
    config_webcam["W_CROP_TOP"] = str(W_CROP_TOP)
    config_webcam["W_CROP_RIGHT"] = str(W_CROP_RIGHT)
    config_webcam["W_CROP_BOTTOM"] = str(W_CROP_BOTTOM)
    config_webcam["W_CROP_LEFT"] = str(W_CROP_LEFT)

    with open(config_file_path, "w", encoding="utf-8") as configfile:
      config.write(configfile)

# ----------------------------------------------------
# Stream Widget
# ----------------------------------------------------
class VideoStream(QWidget):
  def __init__(self, ip, close_callback, focus_callback):
    super().__init__()
    from PyQt6.QtWidgets import QSizePolicy
    self.ip = ip
    self.close_callback = close_callback
    #self.double_click_callback = double_click_callback
    self.current_pixmap = None

    # Stream Resize
    self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    self.main_layout = QVBoxLayout(self)
    self.main_layout.setContentsMargins(5, 5, 5, 5)
    self.main_layout.setSpacing(5)

    # Stream Top Bar
    self.top_bar = QHBoxLayout()
    self.title_label = QLabel(f"{ip}")
    self.title_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
    
    self.close_btn = QPushButton("-")
    self.close_btn.setFixedSize(22, 22)
    self.close_btn.setStyleSheet("""
      QPushButton {
        background-color: #cc0000; color: white; border: none; 
        border-radius: 10px; font-weight: bold; font-size: 11px;
      }
      QPushButton:hover { background-color: #ff3333; }
    """)
    self.close_btn.clicked.connect(lambda: self.close_callback(self.ip))

    self.top_bar.addWidget(self.title_label)
    self.top_bar.addStretch()
    self.top_bar.addWidget(self.close_btn)
    self.main_layout.addLayout(self.top_bar)

    # Tela de renderização configurada para ocupar 100% da área disponível
    self.video_label = QLabel(". . .")
    self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.video_label.setStyleSheet("background-color: #121212; color: white; border: 1px solid #3a3a3a; border-radius: 4px;")
    self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.video_label.setMinimumSize(100, 100) 
    self.main_layout.addWidget(self.video_label, 1) # O número 1 diz para o layout dar prioridade de espaço para o vídeo

    self.setStyleSheet("background-color: #252526; border-radius: 6px;")

  def update_frame(self, q_img):
    if q_img.isNull():
        return
    self.current_pixmap = QPixmap.fromImage(q_img)
    self.resize_frame()

  def resize_frame(self):
    if self.current_pixmap and not self.current_pixmap.isNull():
      w = self.video_label.width()
      h = self.video_label.height()
      if w > 10 and h > 10:
        scaled = self.current_pixmap.scaled(
          w, h,
          Qt.AspectRatioMode.KeepAspectRatio,
          Qt.TransformationMode.SmoothTransformation,
        )
      self.video_label.setPixmap(scaled)

  def resizeEvent(self, event):
    super().resizeEvent(event)
    self.resize_frame()

  def mouseDoubleClickEvent(self, event):
    #self.double_click_callback(self.ip)
    print("Click")

class SavedConnections(QWidget):
  def __init__(self):
    super().__init__()
    self.setObjectName("SavedConnections")
    self.screen_width, self.screen_height = pyautogui.size()
    self.app_width, self.app_height = (round(self.screen_width*0.3), round(self.screen_height*0.5))

    self.setWindowTitle(lang["SAVED_CONTACTS"]["SAVED_CONNECTIONS_TITLE"])
    self.setGeometry(self.screen_width//2-self.app_width//2, self.screen_height//2-self.app_height//2, self.app_width, self.app_height)
    #self.setMaximumWidth(250)
    #self.setMinimumWidth(250)
    #self.setMaximumHeight(500)
    
    # Global styles
    self.setStyleSheet("""
        #SavedConnections { background-color: #262626; }
        QLabel { color: white; font-size: 14px; }
        QLineEdit { background-color: #333; color: white; border: 1px solid #555; padding: 4px; border-radius: 4px; }
        QPushButton { background-color: #444; color: white; border: None; padding: 6px 12px; border-radius: 4px; }
        QComboBox { background-color: #444; color: white; border: None; padding: 6px 8px; border-radius: 4px; }
        QPushButton:hover { background-color: #555; }
        QCheckBox { color: white; font-size: 14px; }
    """)

    # Main Layout (Vertical)
    main_layout = QVBoxLayout()
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    main_layout.setSpacing(15) # Vertical spacing between settings

    # Title
    #self.label = QLabel("Saved Connections")
    #self.label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
    #main_layout.addWidget(self.label)

    # ----------------------------------------------------
    # Setting 1: IP Saver
    # ----------------------------------------------------
    row1_layout = QHBoxLayout()
    row1_layout.setSpacing(5)
    self.ip_name_input = QLineEdit()
    self.ip_name_input.setPlaceholderText(lang["SAVED_CONTACTS"]["CONTACT_NAME"])
    self.ip_input = QLineEdit()
    self.ip_input.setPlaceholderText(lang["SAVED_CONTACTS"]["CONTACT_IP"])
    save_button = QPushButton("💾")
    save_button.clicked.connect(self.save_ip)
    save_button.setCursor(Qt.CursorShape.PointingHandCursor)
    save_button.setFixedWidth(35)

    row1_layout.addWidget(self.ip_name_input)
    row1_layout.addWidget(self.ip_input)
    row1_layout.addWidget(save_button)
    main_layout.addLayout(row1_layout)

    # ----------------------------------------------------
    # Setting 2: Saved IP's
    # ----------------------------------------------------
    global config, config_software

    self.row2_layout = QVBoxLayout()
    saved_ips = eval(config_software["SAVED_IPS"])

    for saved_item in saved_ips:
      row2_sublayout = QHBoxLayout()
      copy_ip_button = self.return_copy_button()
      copy_ip_button.clicked.connect(partial(self.copy_ip, saved_item["ip"]))
      remove_ip_button = self.return_delete_button()
      remove_ip_button.clicked.connect(partial(self.del_ip, saved_item["ip"]))

      row2_sublayout.addWidget(QLabel(f"{saved_item['ip']} | {saved_item['name']}"))
      row2_sublayout.addStretch()
      row2_sublayout.addWidget(copy_ip_button)
      row2_sublayout.addWidget(remove_ip_button)
      self.row2_layout.addLayout(row2_sublayout)

    print(self.row2_layout.count())
    main_layout.addLayout(self.row2_layout)

    self.setLayout(main_layout)

  def del_ip(self, ip:str):
    global config, config_software

    temp_saved_ips = []
    saved_ips = eval(config_software["SAVED_IPS"])
    for item in saved_ips:
      if item["ip"] != ip:
        temp_saved_ips.append(item)

    config_software["SAVED_IPS"] = str(temp_saved_ips)
    with open(config_file_path, "w") as configfile:
      config.write(configfile)

    while self.row2_layout.count():
      item = self.row2_layout.takeAt(0)
      if item.layout() is not None:
        sub = item.layout()
        while sub.count():
          child = sub.takeAt(0)
          if child.widget() is not None:
            child.widget().deleteLater()
        sub.deleteLater()
    
    for saved_item in temp_saved_ips:
      row2_sublayout = QHBoxLayout()
      copy_ip_button = self.return_copy_button()
      copy_ip_button.clicked.connect(partial(self.copy_ip, saved_item["ip"]))
      remove_ip_button = self.return_delete_button()
      remove_ip_button.clicked.connect(partial(self.del_ip, saved_item["ip"]))

      row2_sublayout.addWidget(QLabel(f"{saved_item['ip']} | {saved_item['name']}"))
      row2_sublayout.addStretch()
      row2_sublayout.addWidget(copy_ip_button)
      row2_sublayout.addWidget(remove_ip_button)
      self.row2_layout.addLayout(row2_sublayout)

  def copy_ip(self, ip:str):
    clipboard = QApplication.clipboard()
    clipboard.setText(ip)

  def save_ip(self):
    global config, config_software
    ip_name = self.ip_name_input.text()
    ip = self.ip_input.text()

    if ip.strip() != "" and ip_name.strip() != "":
      saved_ips = eval(config_software["SAVED_IPS"])
      saved_ips.append({"name":ip_name, "ip":ip})
      config_software["SAVED_IPS"] = str(saved_ips)
      
      with open(config_file_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)

      saved_ip_layout = QHBoxLayout()
      saved = QLabel(f"{saved_ips[-1]['ip']} | {saved_ips[-1]['name']}")

      copy_ip_button = self.return_copy_button()
      copy_ip_button.clicked.connect(partial(self.copy_ip, ip))

      remove_ip_button = self.return_delete_button()
      remove_ip_button.clicked.connect(lambda _ = False: self.del_ip(ip))
      saved_ip_layout.addWidget(saved)
      saved_ip_layout.addStretch()
      saved_ip_layout.addWidget(copy_ip_button)
      saved_ip_layout.addWidget(remove_ip_button)
      self.row2_layout.addLayout(saved_ip_layout)

  def return_delete_button(self):
    remove_ip_button = QPushButton("🗑")
    remove_ip_button.setFixedWidth(33)
    remove_ip_button.setCursor(Qt.CursorShape.PointingHandCursor)
    return remove_ip_button

  def return_copy_button(self):
    copy_ip_button = QPushButton("+")
    copy_ip_button.setFixedWidth(33)
    copy_ip_button.setCursor(Qt.CursorShape.PointingHandCursor)
    return copy_ip_button

if __name__ == '__main__':
  q_app = QApplication(sys.argv)
  app = ScreenshareApp()
  app.show()
  sys.exit(q_app.exec())
  
