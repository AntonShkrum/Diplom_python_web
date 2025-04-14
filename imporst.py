from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import sqlite3
import datetime
from datetime import datetime, timedelta
import hashlib # библиотека для хеширования
import calendar
import telebot
import requests
import jwt
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template as flask_render_template, request
from flask import abort
import json
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import pytz
from pytz import timezone
from flask_apscheduler import APScheduler
import openai
from openai import OpenAI
import time
from cerberus import Validator
import re
import threading
from flask import current_app
from functools import partial
import ssl
from requests.exceptions import SSLError
import smtplib
from email.mime.text import MIMEText
