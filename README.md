# Trading Script

This repository contains a trading script that calculates RSI (Relative Strength Index) signals for S&P 500 stocks and sends an email report with the results. The script fetches and analyzes stock data, calculates performance metrics, and saves the results to an Excel file.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Files](#files)
- [License](#license)

## Introduction
The trading script calculates RSI signals for S&P 500 stocks and generates buy/sell signals based on the RSI values. It also calculates performance metrics, including Sharpe and Sortino ratios, and sends an email report with the results.

## Features
- Calculate RSI for S&P 500 stocks
- Generate buy/sell signals based on RSI values
- Calculate performance metrics (Sharpe and Sortino ratios)
- Save results to an Excel file with separate sheets for buy and sell signals
- Send an email report with the results and an Excel file attachment

## Requirements
- Python 3.6+
- `yfinance` library
- `pandas` library
- `pytickersymbols` library
- `numpy` library
- `smtplib` library
- `email` library

## Installation
View a .py version of the script as well as the .ipynb version in the file repo
