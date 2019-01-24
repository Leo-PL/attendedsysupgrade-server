from asu import app

from flask import request, send_from_directory, redirect
import json
import os
from http import HTTPStatus

from asu.build_request import BuildRequest
from asu.upgrade_check import UpgradeCheck
from asu.utils.config import Config
from asu.utils.database import Database

config = Config()
database = Database(config)

uc = UpgradeCheck(config, database)
br = BuildRequest(config, database)

@app.route("/update-request", methods=['POST'])
@app.route("/api/upgrade-check", methods=['POST'])
@app.route("/api/upgrade-check/<request_hash>", methods=['GET'])
def api_upgrade_check(request_hash=None):
    if request.method == 'POST':
        try:
            request_json = json.loads(request.get_data().decode('utf-8'))
        except:
            return "[]", HTTPStatus.BAD_REQUEST
    else:
        if not request_hash:
            return "[]", HTTPStatus.BAD_REQUEST
        request_json = { "request_hash": request_hash }
    return uc.process_request(request_json)

# direct link to download a specific image based on hash
@app.route("/download/<path:image_path>/<path:image_name>")
def download_image(image_path, image_name):
    return send_from_directory(directory=os.path.join(config.get_folder("download_folder"), image_path), filename=image_name)

# request methos for individual image
# uses post methos to receive build information

# the post request should contain the following entries
# distribution, version, revision, target, packages
@app.route("/image-request", methods=['POST']) # legacy
@app.route("/api/upgrade-request", methods=['POST'])
@app.route("/api/upgrade-request/<request_hash>", methods=['GET'])
def api_upgrade_request(request_hash=None):
    if request.method == 'POST':
        try:
            request_json = json.loads(request.get_data().decode('utf-8'))
        except:
            return "[]", HTTPStatus.BAD_REQUEST
    else:
        if not request_hash:
            return "[]", HTTPStatus.BAD_REQUEST
        request_json = { "request_hash": request_hash }

    return br.process_request(request_json, sysupgrade_requested=1)

@app.route("/api/")
@app.route("/stats")
def api_redirect():
    redirect("https://github.com/aparcar/attendedsysupgrade-server/")

@app.route("/build-request", methods=['POST']) # legacy
@app.route("/api/build-request", methods=['POST'])
@app.route("/api/build-request/<request_hash>", methods=['GET'])
def api_files_request(request_hash=None):
    if request.method == 'POST':
        try:
            request_json = json.loads(request.get_data().decode('utf-8'))
        except:
            return "[]", HTTPStatus.BAD_REQUEST
    else:
        if not request_hash:
            return "[]", HTTPStatus.BAD_REQUEST
        request_json = { "request_hash": request_hash }
    return br.process_request(request_json)

@app.route("/api/v1/stats/images_count")
@app.route("/api/v1/stats/image_stats")
def api_stats_image_stats():
    return mime_json(database.get_image_stats())

@app.route("/api/v1/stats/images_latest")
def api_stats_images_latest():
    return mime_json(database.get_images_latest())

@app.route("/api/v1/stats/fails_latest")
def api_stats_fails_latest():
    return mime_json(database.get_fails_latest())

# create response with mimetype set to json
# usefull when json is directly created by postgresql
def mime_json(response):
    return app.response_class(
            response=response,
            mimetype='application/json')

@app.route("/api/v1/stats/popular_targets")
def api_stats_popular_targets():
    return mime_json(database.get_popular_targets())

@app.route("/api/v1/stats/popular_packages")
def api_stats_popular_packages():
    return mime_json(database.get_popular_packages())

@app.route("/api/distros")
def api_distros():
    return mime_json(database.api_get_distros())

@app.route("/api/distributions")
def api_distributions():
    return mime_json(config.get_all())

@app.route("/api/versions")
def api_versions():
    return mime_json(database.api_get_versions())

@app.route("/api/models")
def api_models():
    distro = request.args.get("distro", "")
    version = request.args.get("version", "")
    model_search = request.args.get("model_search", "")
    if distro != "" and version != "":
        return mime_json(database.get_supported_models_json(model_search, distro, version))
    else:
        return "[]", HTTPStatus.BAD_REQUEST

@app.route("/api/packages_image")
@app.route("/api/default_packages")
def api_default_packages():
    distro = request.args.get("distro", "")
    version = request.args.get("version", "")
    target = request.args.get("target", "")
    subtarget = request.args.get("subtarget", "")
    profile = request.args.get("profile", "")
    if distro != "" and version != "" and target != "" and subtarget != "" and profile != "":
        return mime_json(database.get_image_packages(distro, version, target, subtarget, profile))
    else:
        return "[]", HTTPStatus.BAD_REQUEST

@app.route("/api/image/<image_hash>")
def api_image(image_hash):
    return mime_json(database.get_image_info(image_hash))

@app.route("/api/v1/packages_hash/<packages_hash>")
def api_packages_hash(packages_hash):
    return mime_json(database.get_packages_hash(packages_hash))

@app.route("/api/manifest/<manifest_hash>")
def api_manifest(manifest_hash):
    return mime_json(database.get_manifest_info(manifest_hash))

@app.route("/api/v1/supported")
def api_supported():
    return mime_json(database.get_supported_subtargets_json())