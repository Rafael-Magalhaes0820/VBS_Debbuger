import subprocess
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from tempfile import NamedTemporaryFile

class VBSDebuggerApp(App):
    def build(self):
        # Layout principal (vertical)
        main_layout = BoxLayout(orientation='vertical')

        # Barra superior com os botões "File", "Run" e "Step"
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), padding=[10, 10, 10, 10], spacing=10)

        # Botão "File" (para carregar e salvar arquivos)
        file_button = Button(text="File", size_hint=(None, 1), width=100, on_press=self.show_file_chooser)

        # Botão "Run" (executa o código inteiro)
        run_button = Button(text="Run", size_hint=(None, 1), width=100, on_press=self.run_code)

        # Botão "Step" (executa linha por linha)
        step_button = Button(text="Step", size_hint=(None, 1), width=100, on_press=self.execute_next_line)

        # Adiciona os botões à barra superior
        top_bar.add_widget(file_button)
        top_bar.add_widget(run_button)
        top_bar.add_widget(step_button)

        # Adiciona a barra superior ao layout principal
        main_layout.add_widget(top_bar)

        # Área de edição do código VBS (editável)
        self.code_input = TextInput(text='''WScript.Echo "Hello"
WScript.Echo "World"
WScript.Echo "Line by Line"''', multiline=True)
        main_layout.add_widget(self.code_input)

        # Saída do debugger
        self.output_display = Label(text="Debugger output here", size_hint=(1, 0.2))
        main_layout.add_widget(self.output_display)

        # Variável para acompanhar a linha atual
        self.current_line = 0
        self.vbs_lines = []  # Para armazenar as linhas de código

        return main_layout

    def show_file_chooser(self, instance):
        # Cria um popup com um FileChooser
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserIconView()
        content.add_widget(file_chooser)

        # Botão para abrir o arquivo
        open_button = Button(text='Open', size_hint_y=None, height=50)
        open_button.bind(on_press=lambda x: self.load_file(file_chooser.selection))
        content.add_widget(open_button)

        # Botão para salvar o arquivo
        save_button = Button(text='Save', size_hint_y=None, height=50)
        save_button.bind(on_press=lambda x: self.save_file(file_chooser.path))
        content.add_widget(save_button)

        self.popup = Popup(title="File Chooser", content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def load_file(self, selection):
        if selection:
            file_path = selection[0]
            with open(file_path, 'r') as file:
                self.code_input.text = file.read()
            self.popup.dismiss()

    def save_file(self, path):
        if not path.endswith('.vbs'):
            path += '.vbs'  # Adiciona a extensão se não estiver presente

        with open(path, 'w') as file:
            file.write(self.code_input.text)
        self.popup.dismiss()

    def run_code(self, instance):
        # Atualiza as linhas do código com base no que o usuário escreveu
        self.vbs_lines = self.code_input.text.splitlines()

        # Cria um arquivo temporário para o código VBS
        with NamedTemporaryFile(delete=False, suffix=".vbs", mode='w') as temp_vbs_file:
            temp_vbs_file.write(self.code_input.text)
            temp_vbs_name = temp_vbs_file.name

        # Executa o arquivo VBS completo
        process = subprocess.Popen(['cscript', '//Nologo', temp_vbs_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Atualiza a saída no display do Kivy
        if stderr:
            self.output_display.text = f"Erro: {stderr.decode()}"
        else:
            self.output_display.text = f"Resultado: {stdout.decode()}"

        # Exclui o arquivo temporário
        os.remove(temp_vbs_name)

    def execute_next_line(self, instance):
        # Atualiza as linhas do código com base no que o usuário escreveu
        self.vbs_lines = self.code_input.text.splitlines()

        if self.current_line < len(self.vbs_lines):
            # Acumula as linhas executadas até o momento
            accumulated_code = '\n'.join(self.vbs_lines[:self.current_line + 1])

            # Cria um arquivo temporário com o código acumulado até a linha atual
            with NamedTemporaryFile(delete=False, suffix=".vbs", mode='w') as temp_vbs_file:
                temp_vbs_file.write(accumulated_code)
                temp_vbs_name = temp_vbs_file.name

            # Executa o arquivo VBS temporário
            process = subprocess.Popen(['cscript', '//Nologo', temp_vbs_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # Atualiza a saída no display do Kivy
            if stderr:
                self.output_display.text += f"\nErro na linha {self.current_line + 1}: {stderr.decode()}"
            else:
                self.output_display.text += f"\nLinha {self.current_line + 1} executada: {stdout.decode()}"

            # Avança para a próxima linha
            self.current_line += 1

            # Exclui o arquivo temporário
            os.remove(temp_vbs_name)
        else:
            self.output_display.text += "\nFim do código."
            # Reseta a variável current_line para permitir nova execução
            self.current_line = 0

# Rodar a aplicação
if __name__ == '__main__':
    VBSDebuggerApp().run()
