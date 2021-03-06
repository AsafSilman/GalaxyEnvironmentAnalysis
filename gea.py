import logging
from pathlib import Path

import click
from src.config.load_config import load_config
from src.config.load_workbook import load_workbook
from src.utils.submit_job_slurm import submit_job_slurm
from src.utils.rm_tree import rm_tree

from src.data.audit_raw_data import generate_file_catalog, audit_all_files
from src.data.model_data_set import ModelDataset

from src.model.model_info import ModelInfo
from src.model.run_model_experiment import run_model_experiment
from src.model.galaxy_model import GalaxyModelClassifier


from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

root_config = load_config("config.yml")

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    logging_level = logging.INFO
    if debug:
        logging_level = logging.DEBUG
    logging.basicConfig(format='%(levelname)s %(message)s', level=logging_level)

@cli.command()
@click.option('--all-files/--data-only', default=False)
@click.pass_context
def clean(ctx, all_files):
    processed_data = Path(__file__).parent / "data" / "processed"
    interim_data = Path(__file__).parent / "data" / "interim"

    logger.info(f'Cleaning {processed_data} directory')
    rm_tree(processed_data)

    logger.info(f'Cleaning {interim_data} directory')
    rm_tree(interim_data)

    if all_files:
        log_directory = Path(__file__).parent / "logs"
        models_directory = Path(__file__).parent / "models"

        logger.info(f'Cleaning {log_directory} directory')
        rm_tree(log_directory)

        logger.info(f'Cleaning {models_directory} directory')
        rm_tree(models_directory)

@cli.command()
@click.pass_context
@click.argument('model-name', type=click.STRING)
@click.argument('job-memory', default=40, type=click.INT)
@click.argument('job-partition', default="mlgpu", type=click.STRING)
@click.argument('job-project-dir', default="~/GalaxyEnvironmentAnalysis", type=click.STRING)
def submit_job(ctx, model_name, job_memory, job_partition, job_project_dir):
    submit_job_slurm(
        model_name,
        mem_limit_gb=job_memory,
        partition=job_partition,
        project_directory=job_project_dir
    )

@cli.command()
@click.pass_context
@click.argument('out-file', default="out.csv", type=click.Path(dir_okay=False))
def audit(ctx, out_file):
    _, data_files_dictionary = load_workbook(root_config)
    audit_all_files(data_files_dictionary, root_config, out_file)

@cli.command()
@click.pass_context
@click.argument('data-id', default=None, type=click.INT, required=False)
@click.option('--extract-files/--no-extract-files', default=True)
@click.argument('out-file', default="out.csv", type=click.Path(dir_okay=False))
def catalog(ctx, data_id, extract_files, out_file):
    _, data_files_dictionary = load_workbook(root_config)
    generate_file_catalog(data_files_dictionary, root_config, data_id, extract_files, out_file)

@cli.command()
@click.pass_context
@click.argument('model-name', type=click.STRING)
def prepare_data(ctx, model_name):
    model_config_dictionary, data_files_dictionary = load_workbook(root_config)
    model_info = ModelInfo(model_name, model_config_dictionary, data_files_dictionary)

    model_data_set = ModelDataset(model_info, root_config)

    model_data_set.create_model_data_set()

@cli.command()
@click.pass_context
@click.argument('model-name', type=click.STRING)
def run_experiment(ctx, model_name):
    model_config_dictionary, data_files_dictionary = load_workbook(root_config)
    model_info = ModelInfo(model_name, model_config_dictionary, data_files_dictionary)

    model = GalaxyModelClassifier(model_info, root_config)

    run_model_experiment(model, root_config)

if __name__ == '__main__':
    cli(obj={})