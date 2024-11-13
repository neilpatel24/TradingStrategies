# RSI Trading Script

This repository contains a trading script that calculates RSI (Relative Strength Index) signals for S&P 500 stocks and sends an email report with the results. The script fetches and analyzes stock data, calculates performance metrics, and saves the results to an Excel file.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Current Versions](#current-versions)

## Introduction
The trading script calculates RSI signals for S&P 500 stocks and generates buy/sell signals based on the RSI values. It also calculates performance metrics, including Sharpe and Sortino ratios, and sends an email report with the results.

## Features
- Calculate RSI for S&P 500 stocks
- Generate buy/sell signals based on RSI values - default is 51/71
- Calculate performance metrics (Sharpe and Sortino ratios)
- Save results to an Excel file with separate sheets for buy and sell signals
- Send an email report with the results and an Excel file attachment (output will vary depending on which script is used)

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

## Current Versions
1. RSISP500EmailDailyFile.py - this script allows you to run a one-time analysis and email the output in individual Excel files with a timestamp for each time it runs
2. [WIP] RSISP500EmailAppendedData.py - this script will append the additional buy and sell signals to the bottom of the previous Excel file to allow analysis of signals over time
3. [WIP] RSISP500EmailMASTER.py - this will append the raw data and update dashboard/views in another read-only tab. 
