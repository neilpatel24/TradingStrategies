# Trading Scripts

This repository contains trading scripts that outputs buy and sell signals for S&P 500 stocks and sends an email report with the results. The script fetches and analyzes stock data, calculates performance metrics, and saves the results to an Excel file.

## Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [RSI Strategy Features](#rsi-strategy-features)
- [Current Versions](#current-versions)

## Requirements
- Python 3.6+
- `yfinance` library
- `pandas` library
- `pytickersymbols` library
- `numpy` library
- `smtplib` library
- `email` library
- `datetime` library
- manually update script to include your email address and app password to send the email from
- manually update script to include the email address the output needs to be sent to

## RSI Strategy Features
- Calculate RSI for S&P 500 stocks (any stock can be included, but S&P500 is used by default here)
- Generate buy/sell signals based on RSI values - default is 51/71
- Calculate performance metrics (Sharpe and Sortino ratios) to accompany signals
- Save results to an Excel file with separate sheets for buy and sell signals
- Send an email report with the results and an Excel file attachment (type of output will vary depending on which script is used - see #current-versions)

## Current Versions
1. RSISP500EmailDailyFile.py - this script allows you to run a one-time analysis and email the output in individual Excel files with a timestamp for each time it runs
      - Sample output: RSISP500EmailDailyFile.py
2. [WIP] RSISP500EmailAppendedData.py - this script will append the additional buy and sell signals to the bottom of the previous Excel file to allow analysis of signals over time

3. [WIP] RSISP500EmailMASTER.py - this will append the raw data and update dashboard/views in another read-only tab. 
