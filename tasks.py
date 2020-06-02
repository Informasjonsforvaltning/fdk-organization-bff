import json
import os
import requests
from invoke import task

pipenv_install = "pipenv install --dev"
root_dir = os.path


@task
def unit_test(ctx, install=False):
    pipenv_run_test = "pipenv run pytest -m unit --disable-warnings"
    if install:
        ctx.run(pipenv_install)
    ctx.run(pipenv_run_test)


@task
def build_image(ctx, tags="digdir/fdk-organization-bff:latest", staging=False):
    if staging:
        ctx.run(pipenv_install)
    gen_requirements = "pipenv lock -r >requirements.txt"
    ctx.run(gen_requirements)
    tag = ""
    for t in tags.split(","):
        tag = tag + ' -t ' + t

    print("building image with tag " + tag)
    build_cmd = "docker build . " + tag
    ctx.run(build_cmd)


# start docker-compose for contract-tests
@task
def start_docker(ctx, image="digdir/fdk-organization-bff:latest", attach=False):
    print("starting docker network..")
    host_dir = os.getcwd()
    if attach:
        start_compose = "TEST_IMAGE={0} MOCK_DIR={1} docker-compose -f  tests/docker-compose.contract.yml up".format(
            image, host_dir)
    else:
        start_compose = "TEST_IMAGE={0} MOCK_DIR={1} docker-compose -f  tests/docker-compose.contract.yml up -d".format(
            image, host_dir)
    ctx.run(start_compose)


# stop docker-compose for contract-tests
@task
def stop_docker(ctx, clean=False, remove=False):
    print("stopping docker network..")
    kill = "docker-compose -f tests/docker-compose.contract.yml kill"
    docker_clean = "docker system prune"
    ctx.run(kill)
    if remove:
        ctx.run(f"{docker_clean} -a")
    elif clean:
        ctx.run(docker_clean)


@task
def contract_test(ctx, image="digdir/fdk-organization-bff:latest", compose=False, build=False):
    print("______CONTRACT TESTS_______")
    if build:
        build_image(ctx, image)
    if compose:
        start_docker(ctx, image)
    pipenv_run_test = "pipenv run pytest -m contract --tb=line"
    ctx.run(pipenv_run_test)


@task
def update_organization_catalog(ctx, env=None):
    if env:
        publisher_url = "https://www.{0}.fellesdatakatalog.digdir.no/publisher".format(env)
        org_catalog_url = "https://organization-catalogue.{0}.fellesdatakatalog.digdir.no/organizations/".format(env)
    else:
        publisher_url = "https://www.fellesdatakatalog.digdir.no/publisher"
        org_catalog_url = "https://organization-catalogue.fellesdatakatalog.digdir.no/organizations/".format(env)

    print(publisher_url)
    print(org_catalog_url)

    publishers = requests.get(url=publisher_url)
    for hit in publishers.json()["hits"]["hits"]:
        update_url = org_catalog_url + (hit["_source"]["id"])
        print(update_url)
        x = requests.get(url=update_url, headers={'Accept': 'application/json'})
        print(x)


@task
def record_harvest_data(ctx, old=False, with_org_mock=True):
    if old:
        record_content_from_old_harvesters()


def record_content_from_old_harvesters(env=None):
    # start wiremock recording on https://www.fellesdatakatalog.digdir.no/api/
    old_datasets = "http://localhost:8080/datasets?orgPath="
    old_dataservices = "http://localhost:8080/apis?orgPath="
    old_concepts = "http://localhost:8080/concepts?orgPath="
    old_info_model = "http://localhost:8080/informationmodels?orgPath="

    with open(f"{os.getcwd()}/mock/mappings/organizations-eecaa36f-d383-4f91-87cb-5035515bfa77.json") as mockorgs:
        organizations = json.loads(mockorgs.read())
        org_json = json.loads(organizations['response']['jsonBody'])
        for org in org_json:
            org_catalog_orgPath = org["orgPath"]
            orgPath = get_org_path_for_old_harvester(org["orgPath"])
            print(f"-----collecting data for org {orgPath} ----.")
            dataset_res = requests.get(url=f"{old_datasets}{orgPath}", headers={'Accept': 'application/json'})
            dataset_res = requests.get(url=f"{old_datasets}{org_catalog_orgPath}", headers={'Accept': 'application/json'})
            print("datasets: {0}".format(dataset_res.status_code))
            dataservice_res = requests.get(url=f"{old_dataservices}{orgPath}")
            dataservice_res = requests.get(url=f"{old_dataservices}{org_catalog_orgPath}")
            print("dataservices: {0}".format(dataservice_res.status_code))
            concepts_res = requests.get(url=f"{old_concepts}{orgPath}")
            concepts_res = requests.get(url=f"{old_concepts}{org_catalog_orgPath}")
            print("concepts: {0}".format(concepts_res.status_code))
            info_res = requests.get(url=f"{old_info_model}{org_catalog_orgPath}")
            info_res = requests.get(url=f"{old_info_model}{orgPath}")
            print("informationmodels: {0}".format(info_res.status_code))


def get_content_from_new_harvesters():
    print("TODO")


def get_org_path_for_old_harvester(orgPath: str):
    if orgPath.startswith("/"):
        return orgPath
    else:
        return f"/{orgPath}"
