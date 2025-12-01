"""
Help Dialog for MinerU Desktop Client.

Provides comprehensive documentation and guidance for using the application,
including features, keyboard shortcuts, FAQ, and troubleshooting.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QTextEdit, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class HelpDialog(QDialog):
    """Dialog for displaying comprehensive help documentation."""

    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """
        Initialize the help dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()
        logger.debug("Help dialog initialized")

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Manual do Usuário - MinerU Desktop Client")
        self.setMinimumSize(800, 600)

        # Main layout
        layout = QVBoxLayout()

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_getting_started_tab(), "Como Usar")
        self.tab_widget.addTab(self._create_features_tab(), "Funcionalidades")
        self.tab_widget.addTab(self._create_shortcuts_tab(), "Atalhos de Teclado")
        self.tab_widget.addTab(self._create_faq_tab(), "FAQ")
        self.tab_widget.addTab(self._create_troubleshooting_tab(), "Solução de Problemas")

        layout.addWidget(self.tab_widget)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)

        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_text_widget(self, html_content: str) -> QTextEdit:
        """
        Create a read-only text widget with HTML content.

        Args:
            html_content: HTML-formatted content

        Returns:
            QTextEdit widget configured for display
        """
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(html_content)

        # Set font
        font = QFont()
        font.setPointSize(10)
        text_edit.setFont(font)

        return text_edit

    def _create_getting_started_tab(self) -> QWidget:
        """
        Create the 'Getting Started' tab.

        Returns:
            QWidget with getting started content
        """
        content = """
        <h2>📘 Como Usar o MinerU Desktop Client</h2>

        <h3>1. Configuração Inicial</h3>
        <p>Antes de processar documentos, configure o aplicativo:</p>
        <ol>
            <li>Acesse <b>Arquivo → Configurações</b> (ou pressione <b>Ctrl+,</b>)</li>
            <li>Insira seu <b>API Token do MinerU</b> no campo apropriado</li>
            <li>Selecione a <b>Pasta de Saída</b> onde os arquivos processados serão salvos</li>
            <li>Configure as <b>Opções de Processamento</b> conforme necessário:
                <ul>
                    <li><b>Force OCR</b>: Ativa reconhecimento óptico de caracteres</li>
                    <li><b>Enable Formula Recognition</b>: Detecta e processa fórmulas matemáticas</li>
                    <li><b>Enable Table Recognition</b>: Detecta e processa tabelas</li>
                    <li><b>MinerU Model</b>: Escolha entre Pipeline (melhor para Português) ou VLM (mais novo)</li>
                    <li><b>OCR Language</b>: Selecione o idioma (apenas para modelo Pipeline)</li>
                </ul>
            </li>
            <li>Clique em <b>Save</b> para salvar suas configurações</li>
        </ol>

        <h3>2. Processando Documentos</h3>
        <p>Siga estes passos para processar seus documentos:</p>
        <ol>
            <li><b>Adicione arquivos</b>:
                <ul>
                    <li>Clique em <b>📁 Adicionar Arquivos...</b></li>
                    <li>Ou arraste e solte arquivos diretamente na lista</li>
                    <li>Formatos suportados: PDF, imagens (PNG, JPG), documentos Office</li>
                </ul>
            </li>
            <li><b>Revise a lista</b>: Verifique os arquivos adicionados na lista</li>
            <li><b>Remova arquivos indesejados</b>: Selecione e clique em <b>🗑️ Remover Selecionados</b></li>
            <li><b>Inicie o processamento</b>: Clique em <b>▶️ Iniciar Processamento</b></li>
            <li><b>Acompanhe o progresso</b>:
                <ul>
                    <li>A barra de progresso mostra o status do upload</li>
                    <li>O status de cada arquivo é atualizado na lista</li>
                    <li>O painel Console exibe mensagens detalhadas</li>
                </ul>
            </li>
            <li><b>Acesse os resultados</b>: Quando concluído, clique em <b>📂 Abrir Pasta de Saída</b></li>
        </ol>

        <h3>3. Monitoramento e Console</h3>
        <p>O painel de Console na parte inferior da janela oferece:</p>
        <ul>
            <li><b>Logs em tempo real</b>: Todas as operações são registradas</li>
            <li><b>Filtro de nível</b>: Filtre por DEBUG, INFO, WARNING, ERROR</li>
            <li><b>Controles</b>:
                <ul>
                    <li><b>Limpar</b>: Remove todas as mensagens do console</li>
                    <li><b>Copiar</b>: Copia o conteúdo para a área de transferência</li>
                    <li><b>Exportar</b>: Salva os logs em um arquivo</li>
                </ul>
            </li>
            <li><b>Visibilidade</b>: Use <b>Visualizar → Mostrar Console</b> para ocultar/exibir</li>
        </ul>

        <h3>4. Personalizando a Interface</h3>
        <ul>
            <li><b>Tema</b>: Alterne entre tema claro e escuro em <b>Visualizar → Tema</b></li>
            <li><b>Painel Console</b>: Redimensione arrastando o divisor entre painéis</li>
        </ul>
        """

        return self._create_text_widget(content)

    def _create_features_tab(self) -> QWidget:
        """
        Create the 'Features' tab.

        Returns:
            QWidget with features content
        """
        content = """
        <h2>✨ Funcionalidades do MinerU Desktop Client</h2>

        <h3>📤 Upload e Processamento</h3>
        <ul>
            <li><b>Upload em Lote</b>: Envie múltiplos arquivos simultaneamente para processamento</li>
            <li><b>Suporte Multi-Formato</b>: PDF, imagens (PNG, JPG, JPEG), documentos Office</li>
            <li><b>Drag & Drop</b>: Arraste arquivos diretamente da área de trabalho para a aplicação</li>
            <li><b>Gerenciamento de Fila</b>: Adicione ou remova arquivos antes de iniciar o processamento</li>
            <li><b>Processamento Assíncrono</b>: Continue usando a aplicação durante o processamento</li>
        </ul>

        <h3>🔍 Opções de Processamento Avançadas</h3>
        <ul>
            <li><b>OCR (Optical Character Recognition)</b>:
                <ul>
                    <li>Reconhecimento de texto em imagens e PDFs digitalizados</li>
                    <li>Suporte para Chinês, Inglês e Português</li>
                    <li>Pode ser forçado para todos os documentos</li>
                </ul>
            </li>
            <li><b>Reconhecimento de Fórmulas</b>:
                <ul>
                    <li>Detecta e extrai fórmulas matemáticas</li>
                    <li>Mantém formatação LaTeX quando possível</li>
                </ul>
            </li>
            <li><b>Reconhecimento de Tabelas</b>:
                <ul>
                    <li>Identifica e extrai dados de tabelas</li>
                    <li>Preserva estrutura e formatação</li>
                </ul>
            </li>
            <li><b>Modelos MinerU</b>:
                <ul>
                    <li><b>Pipeline</b>: Modelo legado com melhor suporte para português</li>
                    <li><b>VLM</b>: Modelo mais recente baseado em Vision Language Model</li>
                </ul>
            </li>
        </ul>

        <h3>📊 Monitoramento e Status</h3>
        <ul>
            <li><b>Status em Tempo Real</b>: Acompanhe o progresso de cada arquivo</li>
            <li><b>Indicadores Visuais</b>:
                <ul>
                    <li>[✓ Pronto] - Arquivo pronto para upload</li>
                    <li>[⬆ Upload] - Arquivo sendo enviado</li>
                    <li>[⚙ Processando] - Arquivo em processamento no servidor</li>
                    <li>[✓ Concluído] - Processamento concluído com sucesso</li>
                    <li>[✗ Falha] - Erro no processamento</li>
                </ul>
            </li>
            <li><b>Barra de Progresso</b>: Progresso visual do upload em lote</li>
            <li><b>Notificações Toast</b>: Alertas não-intrusivos para eventos importantes</li>
        </ul>

        <h3>🖥️ Interface e Usabilidade</h3>
        <ul>
            <li><b>Temas Claro e Escuro</b>: Interface adaptável à preferência do usuário</li>
            <li><b>Design Responsivo</b>: Painéis redimensionáveis para melhor visualização</li>
            <li><b>Interface em Português</b>: Totalmente localizada para falantes de português</li>
            <li><b>Atalhos de Teclado</b>: Navegação rápida e eficiente (veja aba "Atalhos de Teclado")</li>
            <li><b>Console Integrado</b>:
                <ul>
                    <li>Logs detalhados de todas as operações</li>
                    <li>Filtros por nível de severidade</li>
                    <li>Exportação e cópia de logs</li>
                </ul>
            </li>
        </ul>

        <h3>💾 Gerenciamento de Arquivos</h3>
        <ul>
            <li><b>Download Automático</b>: Resultados baixados automaticamente ao concluir</li>
            <li><b>Extração Inteligente</b>: Arquivos ZIP extraídos automaticamente</li>
            <li><b>Organização de Saída</b>: Pasta de saída configurável e organizada</li>
            <li><b>Acesso Rápido</b>: Botão para abrir pasta de saída diretamente</li>
        </ul>

        <h3>🔒 Segurança e Privacidade</h3>
        <ul>
            <li><b>Armazenamento Seguro de Token</b>: API token armazenado no Linux Keyring</li>
            <li><b>Validação de Entrada</b>: Verificação de arquivos e configurações</li>
            <li><b>Tratamento de Erros</b>: Mensagens claras e logs detalhados para debugging</li>
        </ul>

        <h3>🏗️ Arquitetura e Qualidade</h3>
        <ul>
            <li><b>Princípios SOLID</b>: Código bem estruturado e manutenível</li>
            <li><b>Separação de Responsabilidades</b>: UI separada da lógica de negócio</li>
            <li><b>Workers Assíncronos</b>: Operações em background para UI responsiva</li>
            <li><b>Sistema de Logging Robusto</b>: Logs estruturados para diagnóstico</li>
        </ul>
        """

        return self._create_text_widget(content)

    def _create_shortcuts_tab(self) -> QWidget:
        """
        Create the 'Keyboard Shortcuts' tab.

        Returns:
            QWidget with shortcuts content
        """
        content = """
        <h2>⌨️ Atalhos de Teclado</h2>

        <p>Use estes atalhos para navegar rapidamente pelo aplicativo:</p>

        <h3>Arquivo</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: rgba(52, 152, 219, 0.1);">
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Atalho</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Ação</th>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+,</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Abrir Configurações</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+Q</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Sair do Aplicativo</td>
            </tr>
        </table>

        <h3>Navegação e Interface</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: rgba(52, 152, 219, 0.1);">
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Atalho</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Ação</th>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>F1</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Abrir Manual do Usuário (esta janela)</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+T</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Alternar Tema (Claro/Escuro)</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+Shift+C</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Mostrar/Ocultar Console</td>
            </tr>
        </table>

        <h3>Seleção de Arquivos</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: rgba(52, 152, 219, 0.1);">
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Atalho</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Ação</th>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+O</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Adicionar Arquivos</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Delete</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Remover Arquivos Selecionados</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+A</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Selecionar Todos os Arquivos</td>
            </tr>
        </table>

        <h3>Processamento</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: rgba(52, 152, 219, 0.1);">
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Atalho</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Ação</th>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+P</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Iniciar Processamento</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+O (após conclusão)</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Abrir Pasta de Saída</td>
            </tr>
        </table>

        <h3>Console</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: rgba(52, 152, 219, 0.1);">
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Atalho</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Ação</th>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+L</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Limpar Console</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+C (no console)</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Copiar Conteúdo do Console</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Ctrl+E</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Exportar Logs</td>
            </tr>
        </table>

        <h3>Diálogos</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: rgba(52, 152, 219, 0.1);">
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Atalho</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #3498db;">Ação</th>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Enter</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Confirmar/OK</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Esc</b></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">Cancelar/Fechar</td>
            </tr>
        </table>

        <p style="margin-top: 20px;"><i><b>Nota:</b> Alguns atalhos podem estar planejados para implementação futura.
        Verifique a disponibilidade de cada atalho testando-o na aplicação.</i></p>
        """

        return self._create_text_widget(content)

    def _create_faq_tab(self) -> QWidget:
        """
        Create the 'FAQ' tab.

        Returns:
            QWidget with FAQ content
        """
        content = """
        <h2>❓ Perguntas Frequentes (FAQ)</h2>

        <h3>Q: Como obtenho um API Token do MinerU?</h3>
        <p><b>A:</b> Para obter um token da API MinerU:</p>
        <ol>
            <li>Acesse o site oficial do MinerU</li>
            <li>Crie uma conta ou faça login</li>
            <li>Navegue até a seção de API ou configurações de desenvolvedor</li>
            <li>Gere um novo token de API</li>
            <li>Copie o token e cole nas Configurações do aplicativo</li>
        </ol>

        <h3>Q: Onde meu token de API é armazenado?</h3>
        <p><b>A:</b> O token é armazenado com segurança no <b>Linux Keyring</b> do sistema.
        Isso garante que suas credenciais não fiquem expostas em arquivos de texto simples.</p>

        <h3>Q: Quais formatos de arquivo são suportados?</h3>
        <p><b>A:</b> O MinerU Desktop Client suporta:</p>
        <ul>
            <li><b>PDF</b>: Documentos PDF (.pdf)</li>
            <li><b>Imagens</b>: PNG (.png), JPEG (.jpg, .jpeg)</li>
            <li><b>Documentos Office</b>: Dependendo da configuração do servidor MinerU</li>
        </ul>

        <h3>Q: Qual modelo MinerU devo escolher?</h3>
        <p><b>A:</b></p>
        <ul>
            <li><b>Pipeline</b>: Recomendado para documentos em <b>Português</b>. É o modelo legado
            com melhor suporte para seleção de idioma.</li>
            <li><b>VLM (Vision Language Model)</b>: Modelo mais recente, potencialmente mais preciso,
            mas sem suporte explícito para seleção de idioma.</li>
        </ul>

        <h3>Q: O que fazer se o upload falhar?</h3>
        <p><b>A:</b> Se o upload falhar:</p>
        <ol>
            <li>Verifique sua conexão com a internet</li>
            <li>Confirme que seu API token está correto e válido</li>
            <li>Verifique o tamanho do arquivo (pode haver limites no servidor)</li>
            <li>Consulte o painel Console para mensagens de erro detalhadas</li>
            <li>Tente novamente com um único arquivo para isolar o problema</li>
        </ol>

        <h3>Q: Como posso ver logs detalhados?</h3>
        <p><b>A:</b> O painel Console na parte inferior da janela exibe logs em tempo real.
        Para ver mais detalhes:</p>
        <ul>
            <li>Certifique-se de que o console está visível (<b>Visualizar → Mostrar Console</b>)</li>
            <li>Selecione o nível de filtro apropriado (DEBUG mostra o máximo de detalhes)</li>
            <li>Use o botão <b>Exportar</b> para salvar logs em um arquivo para análise posterior</li>
        </ul>

        <h3>Q: Posso processar múltiplos arquivos ao mesmo tempo?</h3>
        <p><b>A:</b> Sim! O aplicativo suporta processamento em lote. Adicione todos os arquivos
        desejados à lista antes de clicar em "Iniciar Processamento". Todos serão enviados e
        processados em sequência.</p>

        <h3>Q: Onde os arquivos processados são salvos?</h3>
        <p><b>A:</b> Os arquivos são salvos na <b>Pasta de Saída</b> configurada em
        <b>Arquivo → Configurações</b>. Após o processamento, clique em
        <b>📂 Abrir Pasta de Saída</b> para acessá-los diretamente.</p>

        <h3>Q: O processamento continua se eu fechar o aplicativo?</h3>
        <p><b>A:</b> Não. O processamento é gerenciado localmente pelo aplicativo. Se você fechar
        o aplicativo durante o processamento, o upload em andamento será interrompido.
        No entanto, arquivos já enviados para o servidor MinerU continuarão sendo processados
        no servidor.</p>

        <h3>Q: Como alterno entre temas claro e escuro?</h3>
        <p><b>A:</b> Use <b>Visualizar → Tema</b> no menu principal, ou o atalho
        <b>Ctrl+T</b> (se implementado). Sua preferência será salva para as próximas sessões.</p>

        <h3>Q: O que significa cada status na lista de arquivos?</h3>
        <p><b>A:</b></p>
        <ul>
            <li><b>[✓ Pronto]</b>: Arquivo adicionado, aguardando processamento</li>
            <li><b>[⬆ Upload]</b>: Arquivo sendo enviado para o servidor</li>
            <li><b>[⚙ Processando]</b>: Arquivo sendo processado pelo MinerU</li>
            <li><b>[✓ Concluído]</b>: Processamento bem-sucedido, resultado disponível</li>
            <li><b>[✗ Falha]</b>: Erro durante upload ou processamento</li>
        </ul>

        <h3>Q: Como reporto um bug ou sugiro uma funcionalidade?</h3>
        <p><b>A:</b> Visite o repositório GitHub do projeto em
        <a href="https://github.com/ozp/MinerU-linux-desktop">github.com/ozp/MinerU-linux-desktop</a>
        e abra uma issue descrevendo o problema ou sugestão.</p>
        """

        return self._create_text_widget(content)

    def _create_troubleshooting_tab(self) -> QWidget:
        """
        Create the 'Troubleshooting' tab.

        Returns:
            QWidget with troubleshooting content
        """
        content = """
        <h2>🔧 Solução de Problemas</h2>

        <h3>Problema: "API Token inválido" ou erros de autenticação</h3>
        <p><b>Possíveis Causas:</b></p>
        <ul>
            <li>Token incorreto ou expirado</li>
            <li>Token não foi salvo corretamente</li>
            <li>Problemas com o Linux Keyring</li>
        </ul>
        <p><b>Soluções:</b></p>
        <ol>
            <li>Verifique se copiou o token completo sem espaços extras</li>
            <li>Gere um novo token no site do MinerU</li>
            <li>Abra <b>Configurações</b> e insira novamente o token</li>
            <li>Certifique-se de clicar em <b>Save</b> após inserir o token</li>
            <li>Reinicie o aplicativo após salvar o novo token</li>
        </ol>

        <h3>Problema: Upload muito lento ou trava</h3>
        <p><b>Possíveis Causas:</b></p>
        <ul>
            <li>Conexão de internet lenta ou instável</li>
            <li>Arquivos muito grandes</li>
            <li>Sobrecarga no servidor MinerU</li>
        </ul>
        <p><b>Soluções:</b></p>
        <ol>
            <li>Verifique sua velocidade de internet</li>
            <li>Tente fazer upload de arquivos menores primeiro</li>
            <li>Reduza o número de arquivos no lote</li>
            <li>Aguarde alguns minutos e tente novamente</li>
            <li>Verifique os logs no Console para mensagens de erro específicas</li>
        </ol>

        <h3>Problema: Arquivos processados não aparecem na pasta de saída</h3>
        <p><b>Possíveis Causas:</b></p>
        <ul>
            <li>Processamento ainda em andamento</li>
            <li>Caminho de saída incorreto</li>
            <li>Permissões de arquivo/pasta insuficientes</li>
            <li>Falha no download</li>
        </ul>
        <p><b>Soluções:</b></p>
        <ol>
            <li>Verifique se o status do arquivo é <b>[✓ Concluído]</b></li>
            <li>Confirme o caminho da pasta de saída em <b>Configurações</b></li>
            <li>Verifique permissões da pasta de saída (deve ter permissão de escrita)</li>
            <li>Consulte o Console para erros de download</li>
            <li>Tente definir uma pasta de saída diferente</li>
        </ol>

        <h3>Problema: OCR não está reconhecendo texto corretamente</h3>
        <p><b>Possíveis Causas:</b></p>
        <ul>
            <li>Idioma OCR incorreto selecionado</li>
            <li>Qualidade de imagem ruim</li>
            <li>Modelo VLM selecionado (sem suporte a idioma específico)</li>
        </ul>
        <p><b>Soluções:</b></p>
        <ol>
            <li>Use o modelo <b>Pipeline</b> para documentos em Português</li>
            <li>Selecione <b>Portuguese</b> nas configurações de idioma OCR</li>
            <li>Ative <b>Force OCR</b> nas opções de processamento</li>
            <li>Use imagens de maior qualidade/resolução</li>
            <li>Certifique-se de que o texto na imagem está legível</li>
        </ol>

        <h3>Problema: Tema escuro/claro não está aplicando corretamente</h3>
        <p><b>Possíveis Causas:</b></p>
        <ul>
            <li>Arquivos de tema corrompidos ou ausentes</li>
            <li>Erros ao carregar stylesheet</li>
        </ul>
        <p><b>Soluções:</b></p>
        <ol>
            <li>Reinicie o aplicativo</li>
            <li>Alterne entre temas algumas vezes</li>
            <li>Verifique os logs do Console para erros ao carregar tema</li>
            <li>Reinstale o aplicativo se necessário</li>
        </ol>

        <h3>Problema: Console não está mostrando logs</h3>
        <p><b>Possíveis Causas:</b></p>
        <ul>
            <li>Console oculto</li>
            <li>Filtro de nível muito restritivo</li>
            <li>Console foi limpo</li>
        </ul>
        <p><b>Soluções:</b></p>
        <ol>
            <li>Verifique <b>Visualizar → Mostrar Console</b></li>
            <li>Altere o filtro de nível para <b>DEBUG</b> para ver todas as mensagens</li>
            <li>Realize uma nova ação (como adicionar arquivos) para gerar logs</li>
        </ol>

        <h3>Problema: Aplicativo trava ou não responde</h3>
        <p><b>Possíveis Causas:</b></p>
        <ul>
            <li>Operação de longa duração em andamento</li>
            <li>Recursos de sistema insuficientes</li>
            <li>Bug no código</li>
        </ul>
        <p><b>Soluções:</b></p>
        <ol>
            <li>Aguarde alguns momentos (especialmente durante upload/download)</li>
            <li>Verifique uso de CPU e memória no monitor do sistema</li>
            <li>Feche outros aplicativos para liberar recursos</li>
            <li>Force o fechamento e reinicie o aplicativo</li>
            <li>Reduza o número de arquivos processados simultaneamente</li>
            <li>Reporte o problema no GitHub com passos para reproduzir</li>
        </ol>

        <h3>Problema: Erro "Pasta não encontrada" ao tentar abrir saída</h3>
        <p><b>Possíveis Causas:</b></p>
        <ul>
            <li>Pasta de saída foi movida ou deletada</li>
            <li>Caminho configurado incorretamente</li>
            <li>Permissões insuficientes</li>
        </ul>
        <p><b>Soluções:</b></p>
        <ol>
            <li>Abra <b>Configurações</b> e verifique/reconfigure a pasta de saída</li>
            <li>Crie manualmente a pasta se ela não existir</li>
            <li>Escolha um local com permissões adequadas (ex: sua pasta Home)</li>
            <li>Salve as configurações e tente novamente</li>
        </ol>

        <h3>Obtendo Ajuda Adicional</h3>
        <p>Se você ainda tiver problemas após tentar estas soluções:</p>
        <ol>
            <li><b>Exporte os logs</b>: Use o botão <b>Exportar</b> no Console para salvar os logs</li>
            <li><b>Tire screenshots</b>: Capture imagens do erro ou comportamento inesperado</li>
            <li><b>Abra uma issue</b>: Visite
                <a href="https://github.com/ozp/MinerU-linux-desktop">github.com/ozp/MinerU-linux-desktop</a>
                e crie uma nova issue incluindo:
                <ul>
                    <li>Descrição detalhada do problema</li>
                    <li>Passos para reproduzir</li>
                    <li>Logs exportados (remova informações sensíveis)</li>
                    <li>Screenshots, se aplicável</li>
                    <li>Informações do sistema (distro Linux, versão do Python, etc.)</li>
                </ul>
            </li>
        </ol>

        <p style="margin-top: 20px; padding: 10px; background-color: rgba(52, 152, 219, 0.1); border-left: 4px solid #3498db;">
        <b>💡 Dica:</b> Manter o painel Console visível e configurado para nível DEBUG
        durante operações pode ajudar a identificar problemas rapidamente.</p>
        """

        return self._create_text_widget(content)
