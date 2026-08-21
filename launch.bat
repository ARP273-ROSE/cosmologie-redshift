@echo off
rem ===========================================================================
rem  Calculateur de distances cosmologiques - lanceur Windows
rem
rem    launch.bat                 lance l'interface graphique
rem    launch.bat console         version console, mode interactif
rem    launch.bat console 2.34    calcul direct pour z = 2.34
rem    launch.bat table           table des huit presets
rem    launch.bat check           auto-test du noyau de calcul
rem    launch.bat update          reinstalle les dependances du venv
rem    launch.bat reset           supprime le venv et repart de zero
rem    launch.bat system          se passe du venv (pip install --user)
rem    launch.bat doctor          diagnostic complet de l'installation
rem
rem  Cree le venv et installe les dependances au premier lancement. Si Python
rem  est absent, il est installe automatiquement (winget, sinon python.org).
rem  Equivalent Linux / macOS : ./launch.sh
rem ===========================================================================
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
cd /d "%~dp0."

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "MODE=%~1"

rem --- Ou placer le venv ? ---------------------------------------------------
rem  Windows REFUSE d'executer les binaires d'un venv situe sur un partage
rem  reseau (WinError 5 / "Acces refuse"). Si le depot est sur un lecteur
rem  reseau, on met donc le venv en local, dans %LOCALAPPDATA%.
set "NETDRIVE="
for %%D in ("%CD%") do set "DRV=%%~dD"
for /f "tokens=*" %%T in ('fsutil fsinfo drivetype !DRV! 2^>nul') do set "DRVINFO=%%T"
if defined DRVINFO echo !DRVINFO! | findstr /i "remote distant reseau" >nul && set "NETDRIVE=1"
if "%CD:~0,2%"=="\\" set "NETDRIVE=1"

if defined COSMO_VENV (
    set "VENV=%COSMO_VENV%"
) else if defined NETDRIVE (
    set "VENV=%LOCALAPPDATA%\cosmologie-redshift\venv"
) else (
    set "VENV=.venv"
)
set "PY=!VENV!\Scripts\python.exe"
set "PYW=!VENV!\Scripts\pythonw.exe"
set "STAMP=!VENV!\.deps-ok"

if defined NETDRIVE if not defined COSMO_VENV (
    echo   [INFO] Le depot est sur un lecteur reseau. Windows interdit d'executer
    echo          un environnement virtuel depuis un partage ^(Acces refuse^) :
    echo          le venv est donc place en local, dans
    echo          !VENV!
    echo.
)

if /i "%MODE%"=="help"   goto :usage
if /i "%MODE%"=="-h"     goto :usage
if /i "%MODE%"=="/?"     goto :usage
if /i "%MODE%"=="doctor" goto :doctor
if /i "%MODE%"=="reset"  goto :reset
if /i "%MODE%"=="system" goto :system

rem === 1. Python systeme =====================================================
call :find_python
if errorlevel 1 goto :no_python
:after_python_install
rem  Le Python du Store casse le venv, que celui-ci existe deja ou non.
if defined STORE goto :store_python

rem === 2. venv ===============================================================
if not exist "!PY!" (
    echo   Creation de l'environnement virtuel dans !VENV! ...
    !BOOTSTRAP! -m venv "!VENV!"
    if errorlevel 1 goto :venv_failed
)

rem  Le venv existe : verifie qu'il s'EXECUTE reellement.
"!PY!" -c "import sys" >nul 2>&1
if errorlevel 1 (
    call :repair_venv
    "!PY!" -c "import sys" >nul 2>&1
    if errorlevel 1 goto :venv_broken
)

rem === 3. dependances ========================================================
if /i "%MODE%"=="update" if exist "!STAMP!" del "!STAMP!"

if not exist "!STAMP!" (
    echo   Installation des dependances ^(quelques minutes la premiere fois^) ...
    "!PY!" -m pip install --upgrade pip
    "!PY!" -m pip install -r requirements.txt
    if errorlevel 1 goto :pip_failed
    echo ok> "!STAMP!"
)
if /i "%MODE%"=="update" (
    echo   Dependances a jour.
    pause
    exit /b 0
)

rem === 4. lancement ==========================================================
if /i "%MODE%"=="console" (
    "!PY!" programme\redshift_distance_calculator.py %2 %3
    goto :eof
)
if /i "%MODE%"=="table" (
    "!PY!" programme\redshift_distance_calculator.py --table
    pause
    goto :eof
)
if /i "%MODE%"=="check" (
    "!PY!" programme\cosmo_core.py
    pause
    goto :eof
)
if not "%MODE%"=="" goto :usage

rem  pythonw : pas de console residuelle derriere la fenetre
if exist "!PYW!" (
    start "" "!PYW!" programme\redshift_distance_gui.py
) else (
    "!PY!" programme\redshift_distance_gui.py
    if errorlevel 1 pause
)
goto :eof


rem ===========================================================================
rem  Sous-routines
rem ===========================================================================

:find_python
set "BOOTSTRAP="
set "PYEXE="
set "STORE="
py -3 --version >nul 2>&1 && set "BOOTSTRAP=py -3"
if not defined BOOTSTRAP (
    python --version >nul 2>&1 && set "BOOTSTRAP=python"
)
if not defined BOOTSTRAP exit /b 1
rem  Le Python du Microsoft Store cree des venv inutilisables : on le repere
rem  a son chemin (...\WindowsApps\...) avant de perdre du temps.
for /f "delims=" %%P in ('!BOOTSTRAP! -c "import sys;print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
if defined PYEXE echo !PYEXE! | findstr /i "WindowsApps" >nul && set "STORE=1"
exit /b 0


:repair_venv
rem  Le python du venv refuse de s'executer : on retente une fois en forcant
rem  la copie des binaires (--copies) plutot que les liens de redirection.
echo.
echo   Le venv existant est inutilisable ^(Acces refuse^).
echo   Nouvelle tentative en recreant le venv avec --copies ...
if exist "!VENV!" rmdir /s /q "!VENV!"
!BOOTSTRAP! -m venv --copies "!VENV!"
if errorlevel 1 exit /b 1
"!PY!" -c "import sys" >nul 2>&1
if errorlevel 1 (
    echo   Toujours refuse.
    exit /b 1
)
echo   Reussi : le nouveau venv fonctionne.
echo.
exit /b 0


rem ===========================================================================
rem  Modes speciaux
rem ===========================================================================

:reset
echo   Suppression de !VENV! ...
if exist "!VENV!" rmdir /s /q "!VENV!"
echo   Fait. Relancez launch.bat pour tout reinstaller.
pause
exit /b 0

:system
rem  Repli sans venv : installe pour l'utilisateur courant et lance directement.
rem     launch.bat system            -> interface graphique
rem     launch.bat system console 2.34 / table / check
call :find_python
if errorlevel 1 goto :no_python
echo   Mode SANS venv : installation des dependances pour l'utilisateur courant.
echo   ^(Python utilise : !PYEXE!^)
echo.
!BOOTSTRAP! -m pip install --user -r requirements.txt
if errorlevel 1 (
    echo.
    echo   [ERREUR] Installation impossible meme en mode --user.
    echo   Lancez "launch.bat doctor" et transmettez la sortie.
    pause
    exit /b 1
)
echo.
if /i "%~2"=="console" (
    !BOOTSTRAP! programme\redshift_distance_calculator.py %3 %4
    exit /b 0
)
if /i "%~2"=="table" (
    !BOOTSTRAP! programme\redshift_distance_calculator.py --table
    pause
    exit /b 0
)
if /i "%~2"=="check" (
    !BOOTSTRAP! programme\cosmo_core.py
    pause
    exit /b 0
)
echo   Lancement de l'interface graphique ...
rem  Variante sans console : pyw pour le launcher, pythonw sinon.
set "GUIRUN="
if /i "!BOOTSTRAP!"=="py -3" (
    where pyw >nul 2>&1 && set "GUIRUN=pyw -3"
) else (
    where pythonw >nul 2>&1 && set "GUIRUN=pythonw"
)
if defined GUIRUN (
    start "" !GUIRUN! programme\redshift_distance_gui.py
) else (
    !BOOTSTRAP! programme\redshift_distance_gui.py
    if errorlevel 1 pause
)
exit /b 0

:doctor
echo ===========================================================================
echo   DIAGNOSTIC
echo ===========================================================================
echo.
echo   Dossier courant : %CD%
echo %CD% | findstr /i "OneDrive Proton Dropbox Nextcloud iCloud MEGAsync" >nul && echo   ^<-- dossier synchronise dans le cloud : deconseille pour un venv
echo.
echo   --- Lecteur -----------------------------------------------------------
for %%D in ("%CD%") do set "DRV=%%~dD"
fsutil fsinfo drivetype %DRV% 2>nul || echo   (fsutil indisponible)
echo.
echo   --- Test d'ecriture dans le dossier -----------------------------------
echo test> ".__write_test.tmp" 2>nul
if exist ".__write_test.tmp" (
    echo   Ecriture : OK
    del ".__write_test.tmp"
) else (
    echo   Ecriture : REFUSEE  ^<-- dossier protege ou lecteur reseau
)
echo.
echo   --- Python systeme ----------------------------------------------------
where py 2>nul
where python 2>nul
py -3 --version 2>nul || echo   py -3 : absent
python --version 2>nul || echo   python : absent
echo.
echo   Emplacement de l'executable Python :
py -3 -c "import sys; print('   ', sys.executable)" 2>nul || python -c "import sys; print('   ', sys.executable)" 2>nul
echo   ^(si le chemin contient WindowsApps, c'est le Python du Microsoft Store :
echo    il cree des venv inutilisables - installez celui de python.org^)
echo.
echo   --- Venv ---------------------------------------------------------------
echo   Emplacement : !VENV!
if defined NETDRIVE echo   ^(deporte en local : le depot est sur un lecteur reseau^)
if exist "!VENV!\Scripts" (
    dir /b "!VENV!\Scripts" 2>nul
    echo.
    echo   Test d'execution du python du venv :
    "!PY!" -c "import sys; print('   OK :', sys.version)" || echo   ECHEC ^(Acces refuse = venv inutilisable^)
) else (
    echo   Pas de venv ^(!VENV!\Scripts absent^).
)
echo.
echo   --- Modules -----------------------------------------------------------
"!PY!" -c "import numpy, scipy, astropy, PyQt6, pyqtgraph; print('   tous presents')" 2>nul || echo   dependances absentes ou venv KO
echo.
echo ===========================================================================
pause
exit /b 0


rem ===========================================================================
rem  Messages d'erreur
rem ===========================================================================

:no_python
rem  Python absent : on propose de l'installer automatiquement.
echo.
echo ===========================================================================
echo   Python 3 n'est pas installe sur cette machine.
echo ===========================================================================
echo.
echo   Ce programme en a besoin. Deux solutions :
echo.
echo     1. L'installer maintenant, automatiquement ^(recommande^) ;
echo     2. telecharger l'executable autonome, qui n'a besoin de rien :
echo        https://github.com/ARP273-ROSE/cosmologie-redshift/releases/latest
echo.
if /i "%COSMO_AUTO_INSTALL%"=="1" goto :do_install
set /p "REPLY=  Installer Python automatiquement ? [O/n] "
if /i "!REPLY!"=="n" goto :install_declined

:do_install
echo.
echo   --- Tentative via winget ^(gestionnaire de paquets Windows^) ---
where winget >nul 2>&1
if not errorlevel 1 (
    winget install --id Python.Python.3.12 --scope user --silent ^
        --accept-package-agreements --accept-source-agreements
    call :find_python_after_install
    if not errorlevel 1 goto :python_installed
)

echo   --- Tentative par telechargement direct depuis python.org ---
set "PYURL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
set "PYEXE=%TEMP%\python-installer.exe"
echo   Telechargement ^(~25 Mo^) ...
powershell -NoProfile -Command ^
  "try { Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYEXE%' -UseBasicParsing } catch { exit 1 }"
if errorlevel 1 goto :install_failed
echo   Installation silencieuse ^(pour l'utilisateur courant^) ...
"%PYEXE%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_launcher=1
del "%PYEXE%" >nul 2>&1
call :find_python_after_install
if errorlevel 1 goto :install_failed

:python_installed
echo.
echo   Python est installe. Poursuite du demarrage...
echo.
call :find_python
if errorlevel 1 goto :install_failed
goto :after_python_install

:install_declined
echo.
echo   Installation refusee. L'executable autonome ne demande aucun prerequis :
echo   https://github.com/ARP273-ROSE/cosmologie-redshift/releases/latest
echo.
pause
exit /b 1

:install_failed
echo.
echo   [ERREUR] L'installation automatique de Python a echoue.
echo.
echo   Deux solutions :
echo     * telecharger l'executable autonome ^(rien a installer^) :
echo       https://github.com/ARP273-ROSE/cosmologie-redshift/releases/latest
echo     * ou installer Python a la main depuis https://www.python.org/downloads/
echo       en cochant "Add python.exe to PATH".
echo.
echo   N'utilisez PAS la version du Microsoft Store : ses environnements
echo   virtuels sont inutilisables ^(Acces refuse^).
echo.
pause
exit /b 1


:find_python_after_install
rem  Le PATH du processus courant ne contient pas encore la nouvelle
rem  installation : on cherche aux emplacements standard.
set "BOOTSTRAP="
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
) do (
    if exist %%P (
        set "BOOTSTRAP=%%~P"
        set "PATH=%%~dpP;%%~dpP\Scripts;!PATH!"
        exit /b 0
    )
)
py -3 --version >nul 2>&1 && exit /b 0
python --version >nul 2>&1 && exit /b 0
exit /b 1

:store_python
echo.
echo   [ATTENTION] Le Python detecte vient du Microsoft Store :
echo     !PYEXE!
echo.
echo   Cette version cree des environnements virtuels dont le python.exe
echo   refuse de s'executer ^("Acces refuse"^) : c'est la cause numero 1 de
echo   l'echec d'installation des dependances.
echo.
echo   Solution recommandee :
echo     1. Installer Python depuis https://www.python.org/downloads/
echo        en cochant "Add python.exe to PATH" ;
echo     2. Desactiver les alias du Store :
echo        Parametres ^> Applications ^> Alias d'execution d'application
echo        -^> decocher python.exe et python3.exe ;
echo     3. Relancer "launch.bat reset" puis "launch.bat".
echo.
echo   Contournement immediat, sans venv :
echo     launch.bat system
echo.
pause
exit /b 1

:venv_failed
echo.
echo   [ERREUR] Echec de la creation de l'environnement virtuel.
echo   Lancez "launch.bat doctor" et transmettez la sortie.
echo.
pause
exit /b 1

:venv_broken
echo.
echo ===========================================================================
echo   [ERREUR] Le python du venv refuse de s'executer ^("Acces refuse"^),
echo            meme apres recreation avec --copies.
echo ===========================================================================
echo.
echo   Diagnostic automatique :
echo.
echo     Python systeme  : !PYEXE!
if defined STORE (
    echo     -^> C'EST LE PYTHON DU MICROSOFT STORE : cause confirmee.
) else (
    echo     -^> Ce Python ne vient pas du Store, la cause est ailleurs.
)
echo     Dossier         : %CD%
echo %CD% | findstr /i "OneDrive Proton Dropbox Nextcloud iCloud MEGAsync" >nul && echo     -^> DOSSIER SYNCHRONISE dans le cloud : le client de synchro verrouille
echo %CD% | findstr /i "OneDrive Proton Dropbox Nextcloud iCloud MEGAsync" >nul && echo        les fichiers pendant l'ecriture. Copiez le depot ailleurs sur C:.
for %%D in ("%CD%") do set "DRV=%%~dD"
for /f "tokens=2 delims=:" %%T in ('fsutil fsinfo drivetype !DRV! 2^>nul') do set "DRVTYPE=%%T"
if defined DRVTYPE (
    echo     Lecteur !DRV!      :!DRVTYPE!
    echo !DRVTYPE! | findstr /i "remote distant reseau" >nul && echo     -^> LECTEUR RESEAU : copiez le depot sur C: ^(cause tres probable^).
    echo !DRVTYPE! | findstr /i "removable amovible" >nul && echo     -^> SUPPORT AMOVIBLE : copiez le depot sur C:.
)
echo     Python systeme executable :
!BOOTSTRAP! -c "print('       oui')" 2>nul || echo        NON - votre installation Python est elle-meme cassee.
echo.
echo   Que faire, selon le cas :
echo     * Python du Store        -^> installez celui de python.org en cochant
echo                                 "Add python.exe to PATH", puis desactivez
echo                                 les alias ^(Parametres ^> Applications ^>
echo                                 Alias d'execution d'application^).
echo     * Antivirus              -^> exception sur %CD%\!VENV!
echo     * Lecteur reseau / cloud -^> normalement gere : le venv est deporte
echo                                 dans %%LOCALAPPDATA%%. Si le message persiste,
echo                                 copiez le depot sur C: ou definissez
echo                                 COSMO_VENV=C:\chemin\venv
echo.
echo   Pour utiliser le programme des maintenant, sans venv :
echo.
echo        launch.bat system
echo.
echo   ^(launch.bat doctor donne le detail complet^)
echo.
pause
exit /b 1

:pip_failed
echo.
echo   [ERREUR] Installation des dependances impossible.
echo   Regardez les lignes ci-dessus : elles donnent la cause exacte.
echo     - "Acces refuse"       -^> antivirus, dossier protege ou lecteur reseau
echo     - erreur reseau / SSL  -^> connexion, proxy ou pare-feu
echo   Essayez "launch.bat reset" puis relancez, ou "launch.bat system".
echo.
pause
exit /b 1

:usage
echo.
echo   Usage :
echo     launch.bat                 interface graphique
echo     launch.bat console [z]     version console ^(interactif si z absent^)
echo     launch.bat table           table des huit presets
echo     launch.bat check           auto-test du noyau de calcul
echo     launch.bat update          reinstalle les dependances
echo     launch.bat reset           supprime le venv et repart de zero
echo     launch.bat system          se passe du venv ^(pip install --user^)
echo     launch.bat doctor          diagnostic complet
echo.
echo   COSMO_AUTO_INSTALL=1  installe Python sans rien demander
echo.
pause
exit /b 0
