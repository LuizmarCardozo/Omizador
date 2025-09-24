**Disdal Tech – Otimizador (Windows 10/11)**

Aplicativo gráfico (GUI) para otimizações seguras e reversíveis no Windows.
Foco em simplicidade para o usuário final e em operações que não quebram o sistema.

✅ Compatível com Windows 10 e 11
🔒 Várias ações funcionam melhor como Administrador (UAC)
📦 Distribuição portátil: .exe único (PyInstaller)

✨ Recursos

Ponto de restauração (antes de mudanças).

Esvaziar Lixeira (silencioso, sem prompt).

Otimizar unidades (defrag/TRIM de todas as unidades) com aviso de conclusão.

Limpeza de cache dos navegadores:

Google Chrome

Microsoft Edge (Chromium)

Opera / Opera GX

Mozilla Firefox

A limpeza ignora histórico/senhas. O foco é reduzir espaço/archivos temporários.

Limpar cache de miniaturas (thumbcache*.db).

Gerenciar inicialização (Run): listar, desabilitar/habilitar apps de startup.

Plano de energia: alternar Alto desempenho ↔ Balanceado.

Aparência: alternar Melhor desempenho ↔ Melhor aparência.

Desfazer rápido: volta para Balanceado + Melhor aparência.

Otimizar memória RAM (esvazia working set de processos não-críticos).

Busca de drivers: dispara varredura do Windows Update e pnputil /scan-devices.

📥 Download

Baixe o executável na seção Releases deste repositório:

Vá em Releases (barra lateral direita no GitHub).

Baixe o arquivo DisdalTechOptimizer.exe (ou main.exe, dependendo do seu build).

Salve em uma pasta local (ex.: Downloads ou Área de Trabalho).

💡 Primeiro uso: o Windows SmartScreen pode alertar. Clique em Mais informações > Executar mesmo assim. O aplicativo não coleta dados nem faz alterações irreversíveis.

▶️ Como usar

Execute o .exe.

Para melhor compatibilidade, clique com o botão direito → Executar como administrador.

Na tela principal:

Geral: ações rápidas (ponto de restauração, lixeira, defrag, otimizar RAM, miniaturas).

Caches: limpar cache de Chrome/Edge/Opera/Firefox de uma vez.

Inicialização: atualizar lista, selecionar um item e Desabilitar/Habilitar.

Energia & Aparência: escolher plano de energia e visual do Windows.

Desfazer: existe um botão para voltar a Balanceado + Melhor aparência.

🔔 O app mostra mensagens de confirmação ao concluir operações como otimização de disco e otimização de RAM.

🧼 Limpeza de cache dos navegadores

Fecha automaticamente arquivos temporários quando possível; se o browser estiver aberto, alguns arquivos podem ficar em uso.
Dica: feche os navegadores antes de limpar.

O que é afetado:

Pastas de Cache, GPUCache, Code Cache (JS/WASM) e Service Worker Cache.

Firefox: cache2, startupCache, etc.

O que não é apagado: histórico, senhas, favoritos, cookies de login principais.

⚙️ Permissões & Segurança

Administrador (UAC) é recomendado para:

Otimização de disco/defrag de todas as unidades.

Ajustes no Registro (aparência/visual effects).

Inicialização em HKLM.

Otimização de RAM em mais processos.

O app não faz alterações irreversíveis e não remove arquivos do sistema/usuário sem confirmação de contexto.

Antes de mudanças, você pode criar um ponto de restauração.

💻 Requisitos

Windows 10 ou Windows 11 (64-bit).

Sem dependências extras para o usuário final (binário portátil).

Espaço livre para criar logs temporários.

🧩 Erros comuns & Soluções

SmartScreen bloqueou: clique em Mais informações > Executar mesmo assim.

Logo não aparece (build customizado): verifique se o executável foi empacotado com a imagem DTO.png.

Caches não limpam totalmente: feche o navegador antes e tente novamente.

Inicialização não lista apps: pode faltar permissão de administrador ou as chaves estão vazias.

Otimização de RAM com pouco efeito: alguns processos do sistema são ignorados por segurança.

🔄 Atualização de drivers

O botão “Buscar atualização de drivers (Windows Update)”:

Dispara UsoClient StartScan / StartInteractiveScan.

Executa pnputil /scan-devices.

Abre as Configurações → Windows Update para você acompanhar e instalar.

Para drivers OEM (GPU, chipset, rede, etc.), recomendamos o utilitário do fabricante (GeForce Experience, AMD Adrenalin, Intel DSA, etc.).

🧯 Desfazer rápido

Se quiser voltar ao estado padrão visual:

Desfazer → Balanceado + Melhor aparência
(altera o plano de energia e o VisualFXSetting do usuário).

🛠️ Para quem vai compilar (.exe)

Usuário final não precisa disso.
Abaixo, instruções para a equipe/manutenção:

Ambiente
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pyinstaller psutil send2trash pillow

Empacotar (One-File, com ícone e logo)

Ajuste os caminhos conforme seu repo. No Windows, --add-data usa ;.

pyinstaller ^
  -F -w ^
  -i assets\DTO.ico ^
  --add-data "assets\DTO.png;assets" ^
  main.py


-F: executável único

-w: sem console (GUI)

-i: ícone do executável

--add-data: inclui a logo para o resource_path localizar

Se o código busca resource_path("DTO.png") (sem assets/), troque para:

--add-data "assets\DTO.png;."

Pedir admin ao abrir (opcional)
pyinstaller ^
  -F -w --uac-admin ^
  -i assets\DTO.ico ^
  --add-data "assets\DTO.png;assets" ^
  main.py

Debug (inspecionar arquivos incluídos)
pyinstaller -D -w -i assets\DTO.ico --add-data "assets\DTO.png;assets" main.py
# Executável ficará em dist\main\main.exe com pasta junto

🧾 Privacidade

O aplicativo não coleta informações pessoais.

Logs locais são gerados apenas para diagnóstico (em %TEMP%\win_optimizer_logs).

❗ Aviso

Use por sua conta e risco. Embora tenhamos priorizado ações seguras e reversíveis, cada ambiente é único. Recomendamos criar ponto de restauração antes de grandes mudanças.
