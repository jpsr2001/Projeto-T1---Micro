# Importa as classe Pin da biblioteca machine para controlar o hardware do Raspberry Pi Pico
from machine import Pin, I2C
# Importa a classe DHT11 da biblioteca dht.py
from dht import DHT11
# Importa a biblioteca utime e time para usar funções relacionadas ao tempo
import utime
import time
# Importa a classe SSD1306_I2C da biblioteca ssd1306.py
import ssd1306

# Defina os pinos GPIO para os segmentos de cada dígito
# Primeiro dígito
digit1_pins = [
    Pin(0, Pin.OUT),  # Segmento A
    Pin(1, Pin.OUT),  # Segmento B
    Pin(2, Pin.OUT),  # Segmento C
    Pin(3, Pin.OUT),  # Segmento D
    Pin(4, Pin.OUT),  # Segmento E
    Pin(5, Pin.OUT),  # Segmento F
    Pin(6, Pin.OUT)   # Segmento G
]

# Segundo dígito
digit2_pins = [
    Pin(16, Pin.OUT),  # Segmento A
    Pin(17, Pin.OUT),  # Segmento B
    Pin(18, Pin.OUT),  # Segmento C
    Pin(19, Pin.OUT),  # Segmento D
    Pin(20, Pin.OUT),  # Segmento E
    Pin(21, Pin.OUT),  # Segmento F
    Pin(22, Pin.OUT)   # Segmento G
]

#Mapa de Segmento para o DISPLAY
segment_map = {
    '0': [0, 0, 0, 0, 0, 0, 1],
    '1': [1, 0, 0, 1, 1, 1, 1],
    '2': [0, 0, 1, 0, 0, 1, 0],
    '3': [0, 0, 0, 0, 1, 1, 0],
    '4': [1, 0, 0, 1, 1, 0, 0],
    '5': [0, 1, 0, 0, 1, 0, 0],
    '6': [0, 1, 0, 0, 0, 0, 0],
    '7': [0, 0, 0, 1, 1, 1, 1],
    '8': [0, 0, 0, 0, 0, 0, 0],
    '9': [0, 0, 0, 0, 1, 0, 0]
}

# Define os pinos do Raspberry Pi Pico conectados ao sensor DHT11
dht11_pin = 7
# Define os pinos do Raspberry Pi Pico conectados ao barramento I2C 0
i2c0_slc_pin = 9
i2c0_sda_pin = 8
# Define o pino do Raspberry Pi Pico conectado ao módulo sensor de obstáculo infravermelho
obstacle_pin = 14
# Define o pino do Raspberry Pi Pico conectado ao LED (Associado ao sensor de obstáculo)
LED_obstacle_pin = 15
# Define o pino do Raspberry Pi Pico conectado ao Buzzer (Associado ao sensor de obstáculo)
buzzer_pin = 13
# Define o pino do Raspberry Pi Pico conectado ao Relé
rele_pin = 26
# Define os pinos para os botões que configuram a temperatura
lowButton_pin = 10
highButton_pin = 12

# Configura o pino da saída digital do sensor
obstacle = Pin(obstacle_pin, Pin.IN)
# Configuração do pino do botão e do LED
lowButton = Pin(lowButton_pin, Pin.IN, Pin.PULL_UP)
highButton = Pin(highButton_pin, Pin.IN, Pin.PULL_UP)
# Criando um objeto DHT11 com pino do sensor como entrada sem pull-up
dht11_sensor = DHT11(Pin(dht11_pin, Pin.IN))
# Definindo o pino do LED obstacle como OUTPUT
LED_Obstacle = Pin(LED_obstacle_pin,Pin.OUT)
# Definindo o pino do Buzzer como OUTPUT
Buzzer = Pin(buzzer_pin, Pin.OUT)
# Definindo o pino do Relé como OUTPUT
rele = Pin(rele_pin, Pin.OUT)
# Inicializa o I2C0 com os pinos GPIO9 (SCL) e GPIO8 (SDA)
i2c0 = I2C(0, scl=Pin(i2c0_slc_pin), sda=Pin(i2c0_sda_pin), freq=400000)

print("Scanning I2C bus...")
devices = i2c0.scan()

if devices:
    print("I2C devices found:", devices)
else:
    print("No I2C devices found")

# Inicializa o display OLED I2C de 128x64
display = ssd1306.SSD1306_I2C(128, 64, i2c0,addr=0x3C)

# Tempo de debounce para o sensor em ms
debounce_time_ms = 10
debounce_buttonTime_ms = 20

# Variável global para armazenar o estado atual do sensor e dos botões
obstacle_state = 0
highButton_state = 1
lowButton_state = 1
# Variável global para armazenar o estado anterior do sensor
obstacle_last_state = 0
last_highButton_state = 1
last_lowButton_state = 1

# Habilita o uso de interrupção para o sensor e botões
enable_irq = True
enable_highButton_irq = True
enable_lowButton_irq = True
enable_rele_irq = True

# Verifica se a interrupção está habilitada
if enable_irq:
    # Função de callback para a interrupção do sensor
    def obstacle_callback(pin):
        # Atualiza a variável global obstacle_state com o valor do pino
        global obstacle_state
        obstacle_state = pin.value()

    # Adiciona a interrupção para detectar a mudança no estado do sensor de obstáculo infravermelho (borda de subida e descida)
    obstacle.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=obstacle_callback)
    
if enable_highButton_irq:
    def highButtonCallback(pin):
        global highButton_state
        highButton_state = pin.value()
        
    highButton.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=highButtonCallback)

if enable_lowButton_irq:
    def lowButtonCallback(pin):
        global lowButton_state
        lowButton_state = pin.value()
        
    lowButton.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=lowButtonCallback)

# Atualiza o estado atual e anterior da saída digital do sensor
obstacle_state = obstacle.value()
obstacle_last_state = obstacle.value()

highButton_state = highButton.value()
lowButton_state = lowButton.value()

last_highButton_state = highButton.value()
last_lowButton_state = lowButton.value()


# Imprime mensagem inicial
print("Coloque um obstáculo na frente do sensor de obstáculo infravermelho para testá-lo!")

# Inicializa a variável de tempo de início
start_time = None

# Verifica o estado inicial do sensor
if obstacle.value() == 1:
    # Imprime que não foi detectado um obstáculo no sensor de obstáculo infravermelho
    print("Obstáculo não detectado!")
    # start_time = None
else:
    # Imprime que foi detectado um obstáculo no sensor de obstáculo infravermelho
    print("Obstáculo detectado!")
    # start_time = utime.time()

# Limpa o display
display.fill(0)
display.show()

# Desenha o logo do MicroPython e imprime um texto
display.fill(0)                        # preenche toda a tela com cor = 0
display.fill_rect(0, 0, 32, 32, 1)     # desenha um retângulo sólido de 0,0 a 32,32, cor = 1
display.fill_rect(2, 2, 28, 28, 0)     # desenha um retângulo sólido de 2,2 a 28,28, cor = 0
display.vline(9, 8, 22, 1)             # desenha uma linha vertical x = 9 , y = 8, altura = 22, cor = 1
display.vline(16, 2, 22, 1)            # desenha uma linha vertical x = 16, y = 2, altura = 22, cor = 1
display.vline(23, 8, 22, 1)            # desenha uma linha vertical x = 23, y = 8, altura = 22, cor = 1
display.fill_rect(26, 24, 2, 4, 1)     # desenha um retângulo sólido de 26,24 a 2,4, cor = 1
display.text('MicroPython', 40, 0, 1)  # desenha algum texto em x = 40, y = 0 , cor = 1
display.text('SSD1306', 40, 12, 1)     # desenha algum texto em x = 40, y = 12, cor = 1
display.text('OLED 128x64', 40, 24, 1) # desenha algum texto em x = 40, y = 24, cor = 1
display.show()                         # escreve o conteúdo do FrameBuffer na memória do display

utime.sleep(1)

# Função para exibir um dígito no display
def display_digit(segments, value):
    for i in range(7):
        segments[i].value(segment_map[value][i])

# Função principal para exibir um número de dois dígitos
def display_number(num):
    str_num = "{:02d}".format(num)
    display_digit(digit1_pins, str_num[0])
    display_digit(digit2_pins, str_num[1])

# Define a temperatura desejada no cooler
temp_desejada = 10
# Define a variavel que vai verificar se o peltier está no intervalo de temp desejado
intervalo = 0

elapsed_time = 0
start_time_rele = 0
start_time_desligarele = 0

# Loop infinito
while True:
    
    # Tenta realizar uma medição com o sensor
    try:
        # LED_Obstacle.value(1)
        # Verifica se a interrupção está desabilitada
        if not enable_irq:
            # Lê o estado do sensor
            obstacle_state = obstacle.value()
        if not enable_highButton_irq:
            highButton_state = highButton.value()
        if not enable_lowButton_irq:
            lowButton_state = lowButton.value()
            
        # Verifica se o estado do sensor mudou
        if obstacle_state != obstacle_last_state:
            # Aguarda um período para fazer o debounce
            utime.sleep_ms(debounce_time_ms)
            # Verifica se a interrupção está desabilitada
            if not enable_irq:
                # Lê o estado do sensor
                obstacle_state = obstacle.value()
                
        if (highButton_state != last_highButton_state) or (lowButton_state != last_lowButton_state):
        # Aguarda um período para fazer o debounce
            utime.sleep_ms(debounce_buttonTime_ms)
            # Verifica se a interrupção está desabilitada
            if not enable_highButton_irq:
                highButton_state = highButton.value()
            if not enable_lowButton_irq:
                lowButton_state = lowButton.value()

        # Verifica se ocorreu uma borda de subida no sinal do sensor
        if obstacle_state == 1 and obstacle_last_state == 0:
            # Atualiza o estado anterior do sensor
            obstacle_last_state = 1
            # Imprime que o obstáculo detectado pelo sensor de obstáculo infravermelho foi removido  
            print("Obstáculo removido!")
            start_time = utime.time()

        # Verifica se ocorreu uma borda de descida no sinal do sensor
        elif obstacle_state == 0 and obstacle_last_state == 1:
            # Atualiza o estado anterior do sensor
            obstacle_last_state = 0
            # Imprime que foi detectado um obstáculo no sensor de obstáculo infravermelho
            print("Obstáculo detectado!")
            start_time = None
            
        if lowButton_state == 0 and last_lowButton_state == 1:
            if highButton_state == 1:
                # Atualiza o estado anterior do sensor
                last_lowButton_state = 1
                temp_desejada = temp_desejada - 1
                if(temp_desejada < 2):
                    temp_desejada = 2
                # Imprime que foi detectado um obstáculo no sensor de obstáculo infravermelho
                print("Botão 1 acionado!")
        
        if highButton_state == 0 and last_highButton_state == 1:
            if lowButton_state == 1:
            # Atualiza o estado anterior do sensor
                last_lowButton_state = 1
                temp_desejada = temp_desejada + 1
                if(temp_desejada > 30):
                    temp_desejada = 30
                # Imprime que foi detectado um obstáculo no sensor de obstáculo infravermelho
                print("Botão 2 acionado!")
        
        # Fazendo a leitura do sensor
        dht11_sensor.measure()
        
        # Obtendo a temperatura e a umidade
        dht11_temp = dht11_sensor.temperature()
        dht11_humid = dht11_sensor.humidity()
        temp = int(dht11_sensor.temperature())
        
        # Verifica se a temperatura medida está no intervalo desejado
        if (temp == temp_desejada - 1) and rele.value() == 0:
            if start_time_rele == 0:
                start_time_rele = time.time()
            elif time.time() - start_time_rele >= 10:
                start_time_desligarele = 0
                rele.value(1)
                print("Relé ativado!")
        elif (temp == temp_desejada + 1) and rele.value() == 1:
            if start_time_desligarele == 0:
                start_time_desligarele = time.time()
            elif time.time() - start_time_desligarele >= 10:
                start_time_rele = 0
                rele.value(0)
                print("Relé desativado!")
        elif((LED_Obstacle.value() == 0) or (0 <= elapsed_time <= 10)) and (temp > temp_desejada + 1):
            rele.value(0)
            print("Relé desativado!")
        
        # Imprimindo os valores obtidos no console 
        #print(f"Temperatura: {temp}°C")
        print("Temperatura: {:.2f}%".format(dht11_temp))
        print("Umidade: {:.1f}%".format(dht11_humid))
        print("Atualiza o display com a temperatura e umidade...")
        
        # Imprime a temperatura no display de dois digitos
        display_number(temp)
        
        display.fill(0)  # Limpa o display
        if(temp_desejada == 2):
            display.text(f"Temp: LO",0,0)
        elif(temp_desejada == 30):
            display.text(f"Temp: HI",0,0)
        else:
            display.text(f"Temp: {temp_desejada}",0,0)
    
        display.text("Umidade: {:.1f}%".format(dht11_humid), 0, 20)
        if obstacle_state == 0:
            display.text("Cooler Fechado".format(dht11_temp), 0, 40)
            LED_Obstacle.value(0)
            Buzzer.value(0)
        else:
            display.text("Cooler Aberto".format(dht11_temp), 0, 40)
            LED_Obstacle.value(1)
            print("Cooler está aberto")
            if start_time is not None:
                print("Start_time is not none")
                elapsed_time = utime.time() - start_time
                # print(f"Start_time: {start_time}")
                print(f"Elapsed Time: {elapsed_time}")
                if elapsed_time > 10:
                    rele.value(1)
                    print("Relé ativado por tempo!")
                if elapsed_time > 30:
                    # print("elapsed time maior que 7...")
                    # print("Tempo máximo excedido!")
                    display.text("TEMPO EXCEDIDO",0,60)
                    Buzzer.value(1)
                    utime.sleep(1)
        
        display.show()
        
    # Erro de sistema durante a medição do sensor
    except OSError as e:
        
        # Tratando possíveis erros na leitura do sensor
        print("Erro ao ler dados do sensor:", e)

    # Aguardando 2 segundos antes de realizar uma nova leitura
    utime.sleep(1)
