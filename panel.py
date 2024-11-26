import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from services import Universal, Logger
from models import DI
from apscheduler.job import Job
from decorators import admin

panelBP = Blueprint('panel', __name__)

@panelBP.route('/<accessKey>')
def panel(accessKey):
    return redirect(url_for('panel.options', accessKey=accessKey))

@panelBP.route('/<accessKey>/home', methods=['GET'])
@admin
def options():
    return render_template('panel.html')

@panelBP.route('/<accessKey>/toggleLock', methods=['GET'])
@admin
def toggleLock():
    Universal.configManager.config["systemLock"] = not Universal.configManager.getSystemLock()
    Universal.configManager.dump()
    
    Logger.log("PANEL TOGGLELOCK: System lock toggled to '{}'.".format(Universal.configManager.getSystemLock()))
    
    return "SUCCESS: System lock toggled to '{}'.".format(Universal.configManager.getSystemLock())

@panelBP.route('/<accessKey>/toggleCleaner', methods=['GET'])
@admin
def toggleCleaner():
    if os.environ.get("CLEANER_DISABLED", "False") == "True":
        return "ERROR: Cleaning agent is disabled."
    
    if "CleanerID" in Universal.store:
        try:
            job: Job = Universal.asyncProcessor.scheduler.get_job(Universal.store["CleanerID"])
            if job == None:
                raise Exception("Job not found.")
            
            if job.next_run_time == None:
                job.resume()
                Logger.log("PANEL TOGGLECLEANER: Cleaning agent job has been resumed.")
                return "SUCCESS: Cleaning agent job has been resumed."
            else:
                job.pause()
                Logger.log("PANEL TOGGLECLEANER: Cleaning agent job has been paused.")
                return "SUCCESS: Cleaning agent job has been paused."
        except Exception as e:
            Logger.log("PANEL TOGGLECLEANER ERROR: Failed to toggle cleaner job active status. Error: {}".format(e))
            return "ERROR: Failed to toggle cleaner job active status."
    else:
        Logger.log("PANEL TOGGLECLEANER ERROR: CleanerID not found in Universal store.")
        return "ERROR: Failed to toggle cleaner job active status."

@panelBP.route('/<accessKey>/logs', methods=['GET'])
@admin
def logs():
    try:
        logs = Logger.readAll()
        if isinstance(logs, str):
            print("PANEL LOGS ERROR: Failed to load logs; response: {}".format(logs))
            return "ERROR: Failed to load logs."
        
        if len(logs) == 0:
            return "No logs to display."
        
        return "<br>".join(logs)
    except Exception as e:
        print("PANEL LOGS ERROR: Failed to load logs; error: {}".format(e))
        return "ERROR: Failed to load logs."

@panelBP.route('/<accessKey>/clearLogs', methods=['GET'])
@admin
def clearLogs():
    try:
        Logger.destroyAll()
        return "SUCCESS: Logs have been cleared."
    except Exception as e:
        print("PANEL CLEARLOGS ERROR: Failed to clear logs; error: {}".format(e))
        return "ERROR: Failed to clear logs."

@panelBP.route('/<accessKey>/reset', methods=['GET'])
@admin
def reset():
    try:
        res = DI.save(None)
        if res != True:
            Logger.log("PANEL RESET ERROR: Non-True response from DI; response: {}".format(res))
            return "ERROR: Failed to reset DI."
        
        Logger.log("PANEL RESET: Database reset.")
        return "SUCCESS: Database reset."
    except Exception as e:
        Logger.log("PANEL RESET ERROR: Failed to reset database; error: {}".format(e))
        return "ERROR: Failed to reset database."