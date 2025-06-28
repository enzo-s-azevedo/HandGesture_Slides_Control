# Apresentações com Controle por Gestos

Este projeto Python permite **controlar apresentações do PowerPoint com gestos das mãos**, além de desenhar na tela com um lápis virtual ou apontar com um laser. Ideal para apresentações interativas sem precisar de mouse ou teclado.

## Funcionalidades

- **Controle de Slides com Gestos:**
  - 1 dedo levantado: Próximo slide
  - 2 dedos levantados: Slide anterior
  - 5 dedos levantados: Inicia a apresentação em tela cheia
  - Punho fechado (0 dedos): Sai da tela cheia
- **Modo Lápis:**
  - Gesto de 3 dedos centrais levantados ativa/desativa o lápis virtual para desenhar sobre a tela.
- **Modo Laser:**
  - Gesto de polegar + dois dedos levantados ativa/desativa o ponteiro laser.
- **Apagar Rabiscos:**
  - 4 dedos levantados limpam todos os desenhos.

## Tecnologias Utilizadas

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/) – Captura e processamento de vídeo
- [MediaPipe](https://mediapipe.dev/) – Detecção de mãos e dedos
- [PyQt5](https://pypi.org/project/PyQt5/) – Interface gráfica e sobreposição transparente
- [PyAutoGUI](https://pyautogui.readthedocs.io/) – Automação do teclado para controle do PowerPoint

## Como Executar

1. **Clone este repositório**:
   ```bash
   git clone https://github.com/seu-usuario/overlay-gestos.git
   cd overlay-gestos
    ```
2. Instale as dependências:
  ```bash
  pip install opencv-python mediapipe pyqt5 pyautogui numpy
  ```
3. Configure o caminho do arquivo PowerPoint:
No final do arquivo código.py, altere:
```bash
caminho_pptx = r"C:\Users\Enzo\Desktop\Teste.pptx"
```
4. Execute o script:
```bash
python código.py
```

## Como Usar
- Ativar Modo Lápis: Mostre 3 dedos centrais.
- Ativar Modo Laser: Mostre polegar + 2 dedos.
- Desenhar: Movimente a mão com o lápis ativado.
- Apontar: Movimente a mão com o laser ativado.
- Controlar slides: Use gestos descritos acima.

## Personalização

### Cor e espessura do lápis
No construtor da classe `TransparentOverlay`, edite:

```python
self.pen_color = QColor(255, 0, 0)  # Cor RGB
self.pen_width = 5                  # Espessura
```

### Sensibilidade de suavização:
Ajuste:
```python
self.suavizacao_laser = 0.01
self.suavizacao_lapis = 0.01
```

## Requisitos
- Python 3.7 ou superior
- Webcam funcional
