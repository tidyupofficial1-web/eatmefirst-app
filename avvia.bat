@echo off
title EatMeFirst - Avvio Applicazione
color 0A
cls

echo ========================================================
echo               EATMEFIRST - AVVIO APPLICAZIONE
echo ========================================================
echo.
echo Avvio del server di supporto in background...
echo.

:: 1. Avvia il server Python in background
start /B python IT/carico/server_scanner.py

:: Breve pausa per consentire l'avvio del server
timeout /t 2 /nobreak > nul

echo Sistema pronto! Apertura dell'introduzione multilingua...
echo.

:: 2. APRE LA PAGINA DI INTRODUZIONE LOCALE IN C:\
start "" "%~dp0IT\intro.html"

echo ========================================================
echo Nota: Non chiudere questa finestra finche usi EatMeFirst.
echo ========================================================
echo.
pause